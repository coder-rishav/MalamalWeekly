from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Transaction, DepositRequest, WithdrawalRequest, PaymentGateway
from .payment_service import PaymentService, get_available_gateways, verify_and_complete_payment


@login_required
def transaction_history(request):
    """View all transactions"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'transactions': transactions,
    }
    return render(request, 'transactions/transaction_history.html', context)


@login_required
def add_credits(request):
    """Add credits using payment gateway - Direct payment integration"""
    # Check if user has permission to deposit
    profile = request.user.profile
    if not profile.can_deposit:
        messages.error(request, 'You do not have permission to make deposits. Contact admin for more information.')
        return redirect('games:dashboard')
    
    if profile.is_blocked:
        messages.error(request, f'Your account has been banned. Reason: {profile.blocked_reason}')
        return redirect('games:dashboard')
    
    # Get all active payment gateways
    available_gateways = get_available_gateways()
    
    if not available_gateways.exists():
        messages.error(request, 'No payment methods available. Please contact support.')
        return redirect('games:dashboard')
    
    context = {
        'gateways': available_gateways,
        'user': request.user,
        'wallet_balance': profile.wallet_balance,
    }
    return render(request, 'transactions/add_credits.html', context)


@login_required
@require_POST
def create_payment_order(request):
    """Create payment order via AJAX"""
    try:
        data = json.loads(request.body)
        amount = float(data.get('amount'))
        gateway_id = int(data.get('gateway_id'))
        
        # Validate amount
        gateway = get_object_or_404(PaymentGateway, id=gateway_id, is_active=True)
        
        if amount < float(gateway.min_amount):
            return JsonResponse({
                'success': False,
                'error': f'Minimum deposit amount is ₹{gateway.min_amount}'
            })
        
        if amount > float(gateway.max_amount):
            return JsonResponse({
                'success': False,
                'error': f'Maximum deposit amount is ₹{gateway.max_amount}'
            })
        
        # Create payment order
        service = PaymentService(gateway_id)
        order_data = service.create_order(request.user, amount, description="Wallet Recharge")
        
        return JsonResponse(order_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@require_POST
def verify_payment(request):
    """Verify payment and credit wallet"""
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        payment_data = data.get('payment_data', {})
        
        # Verify and complete payment
        result = verify_and_complete_payment(transaction_id, payment_data)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result.get('error', 'Payment verification failed'))
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def payment_success(request):
    """Payment success callback page"""
    transaction_id = request.GET.get('transaction_id')
    
    try:
        transaction = Transaction.objects.get(reference_id=transaction_id, user=request.user)
        context = {
            'transaction': transaction,
            'amount': transaction.amount,
            'total_amount': transaction.total_amount,
            'fee': transaction.fee_amount,
        }
        return render(request, 'transactions/payment_success.html', context)
    except Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found.')
        return redirect('transactions:transaction_history')


@login_required
def payment_failure(request):
    """Payment failure callback page"""
    transaction_id = request.GET.get('transaction_id')
    reason = request.GET.get('reason', 'Payment failed')
    
    context = {
        'transaction_id': transaction_id,
        'reason': reason,
    }
    return render(request, 'transactions/payment_failure.html', context)


@login_required
def withdraw_credits(request):
    """Request to withdraw credits"""
    # Ensure user has a profile (create if missing)
    from accounts.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Check if user has permission to withdraw
    if not profile.can_withdraw:
        messages.error(request, 'You do not have permission to withdraw funds. Contact admin for more information.')
        return redirect('games:dashboard')
    
    if profile.is_blocked:
        messages.error(request, f'Your account has been banned. Reason: {profile.blocked_reason}')
        return redirect('games:dashboard')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        bank_name = request.POST.get('bank_name')
        account_number = request.POST.get('account_number')
        ifsc_code = request.POST.get('ifsc_code')
        account_holder_name = request.POST.get('account_holder_name')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Check if user has sufficient balance
            if profile.wallet_balance < amount:
                messages.error(request, 'Insufficient balance in your wallet.')
                return redirect('transactions:withdraw_credits')
            
            # Minimum withdrawal amount
            if amount < 100:
                messages.error(request, 'Minimum withdrawal amount is ₹100.')
                return redirect('transactions:withdraw_credits')
            
            # Create withdrawal request
            withdrawal_request = WithdrawalRequest.objects.create(
                user=request.user,
                amount=amount,
                bank_name=bank_name,
                account_number=account_number,
                ifsc_code=ifsc_code,
                account_holder_name=account_holder_name
            )
            
            messages.success(request, 'Your withdrawal request has been submitted. It will be processed within 24-48 hours.')
            return redirect('transactions:transaction_history')
        
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount entered.')
    
    return render(request, 'transactions/withdraw_credits.html')


@login_required
def deposit_requests(request):
    """View user's deposit requests"""
    deposits = DepositRequest.objects.filter(user=request.user).order_by('-requested_at')
    
    context = {
        'deposits': deposits,
    }
    return render(request, 'transactions/deposit_requests.html', context)


@login_required
def withdrawal_requests(request):
    """View user's withdrawal requests"""
    withdrawals = WithdrawalRequest.objects.filter(user=request.user).order_by('-requested_at')
    
    context = {
        'withdrawals': withdrawals,
    }
    return render(request, 'transactions/withdrawal_requests.html', context)


# ==================== WEBHOOK HANDLERS ====================

@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """Handle Razorpay webhook notifications"""
    try:
        webhook_secret = request.META.get('HTTP_X_RAZORPAY_SIGNATURE')
        webhook_body = request.body.decode('utf-8')
        
        # Parse webhook data
        data = json.loads(webhook_body)
        event_type = data.get('event')
        
        if event_type == 'payment.captured':
            payment_entity = data.get('payload', {}).get('payment', {}).get('entity', {})
            order_id = payment_entity.get('order_id')
            payment_id = payment_entity.get('id')
            
            # Find transaction by order_id
            try:
                transaction = Transaction.objects.get(gateway_order_id=order_id)
                
                if transaction.status == 'pending':
                    # Verify and complete payment
                    service = PaymentService(transaction.payment_gateway.id)
                    result = service.complete_payment(
                        transaction,
                        payment_id,
                        payment_entity
                    )
                    
                    if result['success']:
                        return JsonResponse({'status': 'success'})
                
            except Transaction.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'received'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook notifications"""
    try:
        import stripe
        from django.conf import settings
        
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        # You'd get webhook_secret from gateway configuration
        # For now, simplified version
        event_data = json.loads(payload)
        event_type = event_data.get('type')
        
        if event_type == 'payment_intent.succeeded':
            payment_intent = event_data.get('data', {}).get('object', {})
            payment_intent_id = payment_intent.get('id')
            
            # Find transaction
            try:
                transaction = Transaction.objects.get(gateway_order_id=payment_intent_id)
                
                if transaction.status == 'pending':
                    service = PaymentService(transaction.payment_gateway.id)
                    result = service.complete_payment(
                        transaction,
                        payment_intent_id,
                        payment_intent
                    )
                    
                    if result['success']:
                        return JsonResponse({'status': 'success'})
                
            except Transaction.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'received'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@csrf_exempt
@require_POST
def payu_webhook(request):
    """Handle PayU webhook notifications"""
    try:
        # PayU sends data as POST parameters
        status = request.POST.get('status')
        txnid = request.POST.get('txnid')
        mihpayid = request.POST.get('mihpayid')
        
        if status == 'success':
            try:
                transaction = Transaction.objects.get(reference_id=txnid)
                
                if transaction.status == 'pending':
                    service = PaymentService(transaction.payment_gateway.id)
                    
                    # Verify hash
                    verification = service.verify_payment(request.POST.dict())
                    
                    if verification['success']:
                        result = service.complete_payment(
                            transaction,
                            mihpayid,
                            request.POST.dict()
                        )
                        
                        if result['success']:
                            return JsonResponse({'status': 'success'})
                
            except Transaction.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'received'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
