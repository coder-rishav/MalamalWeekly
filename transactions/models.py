from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import json


class PaymentGateway(models.Model):
    """Flexible payment gateway configuration system"""
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('razorpay', 'Razorpay'),
        ('payu', 'PayU'),
        ('paypal', 'PayPal'),
        ('phonepe', 'PhonePe'),
        ('paytm', 'Paytm'),
        ('cashfree', 'Cashfree'),
        ('instamojo', 'Instamojo'),
        ('other', 'Other/Custom'),
    ]
    
    MODE_CHOICES = [
        ('test', 'Test Mode'),
        ('live', 'Live Mode'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=100, help_text="Display name for this gateway")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, help_text="Payment provider type")
    description = models.TextField(blank=True, null=True, help_text="Internal notes about this gateway")
    
    # Configuration
    is_active = models.BooleanField(default=False, help_text="Enable/disable this gateway for users")
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='test', help_text="Test or Live mode")
    display_order = models.IntegerField(default=0, help_text="Order in which gateway appears to users")
    
    # Test Mode Credentials
    test_api_key = models.CharField(max_length=500, blank=True, null=True, help_text="Test API Key")
    test_api_secret = models.CharField(max_length=500, blank=True, null=True, help_text="Test API Secret")
    test_merchant_id = models.CharField(max_length=200, blank=True, null=True, help_text="Test Merchant ID (if required)")
    test_additional_config = models.TextField(blank=True, null=True, help_text="Additional test config as JSON")
    
    # Live Mode Credentials
    live_api_key = models.CharField(max_length=500, blank=True, null=True, help_text="Live API Key")
    live_api_secret = models.CharField(max_length=500, blank=True, null=True, help_text="Live API Secret")
    live_merchant_id = models.CharField(max_length=200, blank=True, null=True, help_text="Live Merchant ID (if required)")
    live_additional_config = models.TextField(blank=True, null=True, help_text="Additional live config as JSON")
    
    # Webhook Configuration
    webhook_secret = models.CharField(max_length=500, blank=True, null=True, help_text="Webhook signing secret")
    webhook_url = models.URLField(blank=True, null=True, help_text="Webhook endpoint URL")
    
    # UI Customization
    logo_url = models.URLField(blank=True, null=True, help_text="Logo URL for this payment method")
    button_color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for payment button")
    
    # Limits and Fees
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, help_text="Minimum transaction amount")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=100000.00, help_text="Maximum transaction amount")
    transaction_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Fee percentage (0 for none)")
    transaction_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fixed fee amount")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_gateways')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_gateways')
    
    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_display()}) - {'Active' if self.is_active else 'Inactive'}"
    
    def get_active_credentials(self):
        """Get credentials based on current mode"""
        if self.mode == 'test':
            return {
                'api_key': self.test_api_key,
                'api_secret': self.test_api_secret,
                'merchant_id': self.test_merchant_id,
                'additional_config': self.parse_additional_config(self.test_additional_config),
            }
        else:
            return {
                'api_key': self.live_api_key,
                'api_secret': self.live_api_secret,
                'merchant_id': self.live_merchant_id,
                'additional_config': self.parse_additional_config(self.live_additional_config),
            }
    
    def parse_additional_config(self, config_text):
        """Parse JSON config or return empty dict"""
        if not config_text:
            return {}
        try:
            return json.loads(config_text)
        except json.JSONDecodeError:
            return {}
    
    def calculate_total_amount(self, base_amount):
        """Calculate total including fees"""
        fee = (base_amount * self.transaction_fee_percent / 100) + self.transaction_fee_fixed
        return base_amount + fee
    
    def clean(self):
        """Validate model data"""
        if self.is_active:
            creds = self.get_active_credentials()
            if not creds['api_key']:
                raise ValidationError(f"Cannot activate gateway without {self.mode} API key")


class Transaction(models.Model):
    """All financial transactions"""
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('game_entry', 'Game Entry Fee'),
        ('winning', 'Winning Amount'),
        ('refund', 'Refund'),
        ('bonus', 'Bonus Credit'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
        ('admin', 'Admin Credit'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Gateway fees")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Amount + Fees")
    
    # Payment Gateway Integration
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, blank=True, null=True)
    payment_id = models.CharField(max_length=200, blank=True, null=True, help_text="Payment gateway transaction ID")
    gateway_order_id = models.CharField(max_length=200, blank=True, null=True, help_text="Gateway's order ID")
    payment_details = models.TextField(blank=True, null=True, help_text="JSON data from gateway")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Balances
    balance_before = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reference
    reference_id = models.CharField(max_length=100, unique=True, editable=False)
    description = models.TextField(blank=True, null=True)
    
    # Related objects
    game_entry = models.ForeignKey('games.UserEntry', on_delete=models.SET_NULL, null=True, blank=True, related_name='transaction')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.reference_id:
            # Generate unique reference ID
            import uuid
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.reference_id = f"TXN-{timestamp}-{uuid.uuid4().hex[:6].upper()}"
        
        # Calculate total amount if not set
        if self.total_amount is None:
            self.total_amount = self.amount + self.fee_amount
        
        super().save(*args, **kwargs)


class DepositRequest(models.Model):
    """User deposit/credit purchase requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposit_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, null=True, blank=True, related_name='deposit_requests')
    
    # Gateway Details
    gateway_order_id = models.CharField(max_length=200, blank=True, null=True, help_text="Gateway's order/payment ID")
    gateway_payment_id = models.CharField(max_length=200, blank=True, null=True, help_text="Gateway's payment reference")
    payment_response = models.TextField(blank=True, null=True, help_text="Raw gateway response JSON")
    
    # Payment proof (for manual methods)
    transaction_screenshot = models.ImageField(upload_to='deposits/', blank=True, null=True)
    payment_reference = models.CharField(max_length=200, blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    # Related transaction
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='deposit_request')
    
    # Metadata
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_deposits')
    
    class Meta:
        verbose_name = 'Deposit Request'
        verbose_name_plural = 'Deposit Requests'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.status}"


class WithdrawalRequest(models.Model):
    """User withdrawal requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Bank details
    bank_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    account_holder_name = models.CharField(max_length=200)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    
    # Related transaction
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='withdrawal_request')
    
    # Metadata
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_withdrawals')
    
    class Meta:
        verbose_name = 'Withdrawal Request'
        verbose_name_plural = 'Withdrawal Requests'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.status}"
