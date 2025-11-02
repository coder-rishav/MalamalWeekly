from django.contrib import admin
from django.utils import timezone
from .models import Transaction, DepositRequest, WithdrawalRequest


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference_id', 'user', 'transaction_type', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('transaction_type', 'status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'reference_id', 'payment_id', 'description')
    readonly_fields = ('reference_id', 'balance_before', 'balance_after', 'created_at', 'completed_at')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('reference_id', 'user', 'transaction_type', 'amount', 'status')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_id')
        }),
        ('Balance', {
            'fields': ('balance_before', 'balance_after')
        }),
        ('Additional Information', {
            'fields': ('description', 'game_entry')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'payment_method', 'status', 'requested_at', 'processed_by')
    list_filter = ('status', 'payment_method', 'requested_at')
    search_fields = ('user__username', 'payment_reference')
    readonly_fields = ('requested_at', 'processed_at', 'transaction')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'amount', 'payment_method', 'status')
        }),
        ('Payment Proof', {
            'fields': ('transaction_screenshot', 'payment_reference')
        }),
        ('Admin Action', {
            'fields': ('admin_notes', 'processed_by', 'processed_at')
        }),
        ('Related Transaction', {
            'fields': ('transaction',)
        }),
        ('Metadata', {
            'fields': ('requested_at',)
        }),
    )
    
    actions = ['approve_deposits', 'reject_deposits']
    
    def approve_deposits(self, request, queryset):
        approved_count = 0
        for deposit_request in queryset.filter(status='pending'):
            user = deposit_request.user
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=user,
                transaction_type='deposit',
                amount=deposit_request.amount,
                payment_method=deposit_request.payment_method,
                status='completed',
                balance_before=user.profile.wallet_balance,
                balance_after=user.profile.wallet_balance + deposit_request.amount,
                description=f'Deposit approved by {request.user.username}',
                completed_at=timezone.now()
            )
            
            # Add credits to user wallet
            user.profile.add_credits(deposit_request.amount)
            
            # Update deposit request
            deposit_request.status = 'approved'
            deposit_request.processed_by = request.user
            deposit_request.processed_at = timezone.now()
            deposit_request.transaction = transaction
            deposit_request.save()
            
            approved_count += 1
        
        self.message_user(request, f'{approved_count} deposit(s) approved successfully.')
    approve_deposits.short_description = "Approve selected deposit requests"
    
    def reject_deposits(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} deposit(s) rejected.')
    reject_deposits.short_description = "Reject selected deposit requests"


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'account_number', 'status', 'requested_at', 'processed_by')
    list_filter = ('status', 'requested_at')
    search_fields = ('user__username', 'account_number', 'account_holder_name')
    readonly_fields = ('requested_at', 'processed_at', 'transaction')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'amount', 'status')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'ifsc_code', 'account_holder_name')
        }),
        ('Admin Action', {
            'fields': ('admin_notes', 'processed_by', 'processed_at')
        }),
        ('Related Transaction', {
            'fields': ('transaction',)
        }),
        ('Metadata', {
            'fields': ('requested_at',)
        }),
    )
    
    actions = ['approve_withdrawals', 'complete_withdrawals', 'reject_withdrawals']
    
    def approve_withdrawals(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='approved', processed_by=request.user, processed_at=timezone.now())
        self.message_user(request, f'{updated} withdrawal(s) approved.')
    approve_withdrawals.short_description = "Approve selected withdrawal requests"
    
    def complete_withdrawals(self, request, queryset):
        completed_count = 0
        for withdrawal_request in queryset.filter(status='approved'):
            user = withdrawal_request.user
            
            # Check if user has sufficient balance
            if user.profile.wallet_balance < withdrawal_request.amount:
                continue
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=user,
                transaction_type='withdrawal',
                amount=withdrawal_request.amount,
                payment_method='wallet',
                status='completed',
                balance_before=user.profile.wallet_balance,
                balance_after=user.profile.wallet_balance - withdrawal_request.amount,
                description=f'Withdrawal completed by {request.user.username}',
                completed_at=timezone.now()
            )
            
            # Deduct from user wallet
            user.profile.wallet_balance -= withdrawal_request.amount
            user.profile.total_withdrawals += withdrawal_request.amount
            user.profile.save()
            
            # Update withdrawal request
            withdrawal_request.status = 'completed'
            withdrawal_request.processed_by = request.user
            withdrawal_request.processed_at = timezone.now()
            withdrawal_request.transaction = transaction
            withdrawal_request.save()
            
            completed_count += 1
        
        self.message_user(request, f'{completed_count} withdrawal(s) completed successfully.')
    complete_withdrawals.short_description = "Complete selected withdrawal requests"
    
    def reject_withdrawals(self, request, queryset):
        updated = queryset.exclude(status='completed').update(
            status='rejected',
            processed_by=request.user,
            processed_at=timezone.now()
        )
        self.message_user(request, f'{updated} withdrawal(s) rejected.')
    reject_withdrawals.short_description = "Reject selected withdrawal requests"
