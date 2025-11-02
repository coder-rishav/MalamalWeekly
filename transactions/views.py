from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Transaction, DepositRequest, WithdrawalRequest


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
    """Request to add credits"""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        payment_reference = request.POST.get('payment_reference', '')
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Create deposit request
            deposit_request = DepositRequest.objects.create(
                user=request.user,
                amount=amount,
                payment_method=payment_method,
                payment_reference=payment_reference
            )
            
            messages.success(request, 'Your deposit request has been submitted. It will be processed shortly.')
            return redirect('transactions:transaction_history')
        
        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount entered.')
    
    return render(request, 'transactions/add_credits.html')


@login_required
def withdraw_credits(request):
    """Request to withdraw credits"""
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
            
            # Ensure user has a profile (create if missing)
            from accounts.models import UserProfile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            
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
