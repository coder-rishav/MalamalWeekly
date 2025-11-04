"""
Payment Gateway Service Layer
Handles payment processing for multiple providers (Stripe, Razorpay, PayU, etc.)
"""

import json
import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from transactions.models import PaymentGateway, Transaction, DepositRequest


class PaymentService:
    """Universal payment service that routes to appropriate gateway"""
    
    def __init__(self, gateway_id=None):
        """Initialize with specific gateway or use default active gateway"""
        if gateway_id:
            self.gateway = PaymentGateway.objects.get(id=gateway_id, is_active=True)
        else:
            # Get first active gateway
            self.gateway = PaymentGateway.objects.filter(is_active=True).first()
            if not self.gateway:
                raise ValueError("No active payment gateway configured")
        
        self.credentials = self.gateway.get_active_credentials()
    
    def get_active_gateways(self):
        """Get all active payment gateways"""
        return PaymentGateway.objects.filter(is_active=True).order_by('display_order')
    
    def calculate_fees(self, amount):
        """Calculate gateway fees"""
        fee = (Decimal(amount) * self.gateway.transaction_fee_percent / 100) + self.gateway.transaction_fee_fixed
        total = Decimal(amount) + fee
        return {
            'amount': Decimal(amount),
            'fee': fee,
            'total': total
        }
    
    def create_order(self, user, amount, description="Deposit"):
        """Create payment order based on gateway provider"""
        
        # Calculate fees
        fee_calc = self.calculate_fees(amount)
        
        # Get current balance
        current_balance = user.profile.wallet_balance
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=user,
            transaction_type='deposit',
            amount=fee_calc['amount'],
            fee_amount=fee_calc['fee'],
            total_amount=fee_calc['total'],
            payment_gateway=self.gateway,
            status='pending',
            balance_before=current_balance,
            balance_after=current_balance,  # Will be updated when payment completes
            description=description
        )
        
        # Route to appropriate provider
        if self.gateway.provider == 'razorpay':
            return self._create_razorpay_order(transaction)
        elif self.gateway.provider == 'stripe':
            return self._create_stripe_order(transaction)
        elif self.gateway.provider == 'payu':
            return self._create_payu_order(transaction)
        elif self.gateway.provider == 'phonepe':
            return self._create_phonepe_order(transaction)
        elif self.gateway.provider == 'cashfree':
            return self._create_cashfree_order(transaction)
        else:
            # For other gateways, return basic info
            return {
                'success': True,
                'transaction_id': transaction.reference_id,
                'gateway': self.gateway.name,
                'provider': self.gateway.get_provider_display(),
                'amount': float(fee_calc['amount']),
                'fee': float(fee_calc['fee']),
                'total': float(fee_calc['total']),
                'message': f'Please proceed with {self.gateway.name} payment'
            }
    
    def _create_razorpay_order(self, transaction):
        """Create Razorpay order"""
        try:
            import razorpay
            
            client = razorpay.Client(auth=(
                self.credentials['api_key'],
                self.credentials['api_secret']
            ))
            
            # Create order
            order_data = {
                'amount': int(transaction.total_amount * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': transaction.reference_id,
                'notes': {
                    'user_id': transaction.user.id,
                    'username': transaction.user.username
                }
            }
            
            order = client.order.create(data=order_data)
            
            # Update transaction
            transaction.gateway_order_id = order['id']
            transaction.payment_details = json.dumps(order)
            transaction.save()
            
            return {
                'success': True,
                'provider': 'razorpay',
                'order_id': order['id'],
                'amount': float(transaction.amount),
                'fee': float(transaction.fee_amount),
                'total': float(transaction.total_amount),
                'currency': 'INR',
                'transaction_id': transaction.reference_id,
                'key': self.credentials['api_key'],
                'name': settings.SITE_NAME if hasattr(settings, 'SITE_NAME') else 'Malamal Weekly',
                'description': transaction.description,
                'prefill': {
                    'name': transaction.user.get_full_name() or transaction.user.username,
                    'email': transaction.user.email,
                },
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Razorpay library not installed. Install with: pip install razorpay'
            }
        except Exception as e:
            transaction.status = 'failed'
            transaction.failure_reason = str(e)
            transaction.save()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_stripe_order(self, transaction):
        """Create Stripe payment intent"""
        try:
            import stripe
            
            stripe.api_key = self.credentials['api_secret']
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(transaction.total_amount * 100),  # Amount in cents
                currency='inr',
                metadata={
                    'transaction_id': transaction.reference_id,
                    'user_id': transaction.user.id,
                    'username': transaction.user.username,
                },
                description=transaction.description,
            )
            
            # Update transaction
            transaction.gateway_order_id = intent.id
            transaction.payment_details = json.dumps(dict(intent))
            transaction.save()
            
            return {
                'success': True,
                'provider': 'stripe',
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': float(transaction.amount),
                'fee': float(transaction.fee_amount),
                'total': float(transaction.total_amount),
                'transaction_id': transaction.reference_id,
                'publishable_key': self.credentials['api_key'],
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Stripe library not installed. Install with: pip install stripe'
            }
        except Exception as e:
            transaction.status = 'failed'
            transaction.failure_reason = str(e)
            transaction.save()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_payu_order(self, transaction):
        """Create PayU order"""
        # PayU implementation
        merchant_key = self.credentials['api_key']
        merchant_salt = self.credentials['api_secret']
        
        # Generate hash
        hash_string = f"{merchant_key}|{transaction.reference_id}|{transaction.total_amount}|{transaction.description}|{transaction.user.get_full_name()}|{transaction.user.email}|||||||||||{merchant_salt}"
        hash_value = hashlib.sha512(hash_string.encode()).hexdigest()
        
        # Update transaction
        transaction.gateway_order_id = transaction.reference_id
        transaction.save()
        
        payu_url = "https://secure.payu.in/_payment" if self.gateway.mode == 'live' else "https://test.payu.in/_payment"
        
        return {
            'success': True,
            'provider': 'payu',
            'action_url': payu_url,
            'params': {
                'key': merchant_key,
                'txnid': transaction.reference_id,
                'amount': str(transaction.total_amount),
                'productinfo': transaction.description,
                'firstname': transaction.user.get_full_name() or transaction.user.username,
                'email': transaction.user.email,
                'phone': getattr(transaction.user.profile, 'phone_number', ''),
                'surl': settings.PAYMENT_SUCCESS_URL if hasattr(settings, 'PAYMENT_SUCCESS_URL') else '',
                'furl': settings.PAYMENT_FAILURE_URL if hasattr(settings, 'PAYMENT_FAILURE_URL') else '',
                'hash': hash_value,
            },
            'amount': float(transaction.amount),
            'fee': float(transaction.fee_amount),
            'total': float(transaction.total_amount),
            'transaction_id': transaction.reference_id,
        }
    
    def _create_phonepe_order(self, transaction):
        """Create PhonePe order"""
        # PhonePe implementation (placeholder)
        return {
            'success': True,
            'provider': 'phonepe',
            'message': 'PhonePe integration coming soon',
            'transaction_id': transaction.reference_id,
            'amount': float(transaction.amount),
            'fee': float(transaction.fee_amount),
            'total': float(transaction.total_amount),
        }
    
    def _create_cashfree_order(self, transaction):
        """Create Cashfree order"""
        # Cashfree implementation (placeholder)
        return {
            'success': True,
            'provider': 'cashfree',
            'message': 'Cashfree integration coming soon',
            'transaction_id': transaction.reference_id,
            'amount': float(transaction.amount),
            'fee': float(transaction.fee_amount),
            'total': float(transaction.total_amount),
        }
    
    def verify_payment(self, payment_data):
        """Verify payment based on gateway provider"""
        
        if self.gateway.provider == 'razorpay':
            return self._verify_razorpay_payment(payment_data)
        elif self.gateway.provider == 'stripe':
            return self._verify_stripe_payment(payment_data)
        elif self.gateway.provider == 'payu':
            return self._verify_payu_payment(payment_data)
        else:
            return {'success': False, 'error': 'Verification not implemented for this gateway'}
    
    def _verify_razorpay_payment(self, payment_data):
        """Verify Razorpay payment signature"""
        try:
            import razorpay
            
            client = razorpay.Client(auth=(
                self.credentials['api_key'],
                self.credentials['api_secret']
            ))
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': payment_data.get('razorpay_order_id'),
                'razorpay_payment_id': payment_data.get('razorpay_payment_id'),
                'razorpay_signature': payment_data.get('razorpay_signature')
            }
            
            client.utility.verify_payment_signature(params_dict)
            
            return {
                'success': True,
                'payment_id': payment_data.get('razorpay_payment_id'),
                'order_id': payment_data.get('razorpay_order_id'),
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _verify_stripe_payment(self, payment_data):
        """Verify Stripe payment"""
        try:
            import stripe
            
            stripe.api_key = self.credentials['api_secret']
            
            payment_intent = stripe.PaymentIntent.retrieve(payment_data.get('payment_intent_id'))
            
            if payment_intent.status == 'succeeded':
                return {
                    'success': True,
                    'payment_id': payment_intent.id,
                }
            else:
                return {
                    'success': False,
                    'error': f'Payment status: {payment_intent.status}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _verify_payu_payment(self, payment_data):
        """Verify PayU payment hash"""
        try:
            merchant_salt = self.credentials['api_secret']
            
            # Verify hash
            hash_string = f"{merchant_salt}|{payment_data.get('status')}||||||||||{payment_data.get('email')}|{payment_data.get('firstname')}|{payment_data.get('productinfo')}|{payment_data.get('amount')}|{payment_data.get('txnid')}|{self.credentials['api_key']}"
            hash_value = hashlib.sha512(hash_string.encode()).hexdigest()
            
            if hash_value == payment_data.get('hash'):
                return {
                    'success': True,
                    'payment_id': payment_data.get('mihpayid'),
                    'transaction_id': payment_data.get('txnid'),
                }
            else:
                return {
                    'success': False,
                    'error': 'Hash verification failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def complete_payment(self, transaction, payment_id, payment_details=None):
        """Mark payment as completed and credit user wallet"""
        try:
            transaction.status = 'completed'
            transaction.payment_id = payment_id
            transaction.completed_at = timezone.now()
            
            if payment_details:
                transaction.payment_details = json.dumps(payment_details)
            
            # Credit user wallet
            user_profile = transaction.user.profile
            user_profile.add_credits(transaction.amount)
            
            # Update balance_after
            transaction.balance_after = user_profile.wallet_balance
            transaction.save()
            
            return {
                'success': True,
                'message': f'₹{transaction.amount} credited to your wallet'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def fail_payment(self, transaction, reason):
        """Mark payment as failed"""
        transaction.status = 'failed'
        transaction.description = f"{transaction.description or ''}\nFailure: {reason}"
        transaction.save()


# Quick helper functions
def get_available_gateways():
    """Get all active payment gateways"""
    return PaymentGateway.objects.filter(is_active=True).order_by('display_order')


def create_payment_order(user, amount, gateway_id=None):
    """Quick function to create payment order"""
    service = PaymentService(gateway_id)
    return service.create_order(user, amount)


def verify_and_complete_payment(transaction_id, payment_data):
    """Quick function to verify and complete payment"""
    try:
        transaction = Transaction.objects.get(reference_id=transaction_id)
        service = PaymentService(transaction.payment_gateway.id)
        
        verification = service.verify_payment(payment_data)
        
        if verification['success']:
            return service.complete_payment(
                transaction,
                verification['payment_id'],
                payment_data
            )
        else:
            service.fail_payment(transaction, verification.get('error', 'Verification failed'))
            return verification
            
    except Transaction.DoesNotExist:
        return {
            'success': False,
            'error': 'Transaction not found'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
