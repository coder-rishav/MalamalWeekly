from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'  # Specify which foreign key to use
    fields = (
        ('phone_number', 'date_of_birth'),
        'address',
        ('city', 'state'),
        ('postal_code', 'country'),
        ('wallet_balance', 'is_verified'),
        ('total_deposits', 'total_withdrawals'),
        ('total_winnings', 'total_spent'),
        ('is_blocked', 'blocked_reason'),
    )
    readonly_fields = ('total_deposits', 'total_withdrawals', 'total_winnings', 'total_spent')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_wallet_balance', 'get_is_verified', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'profile__is_verified', 'profile__is_blocked')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone_number')
    
    def get_wallet_balance(self, obj):
        return f"₹{obj.profile.wallet_balance}" if hasattr(obj, 'profile') else 'N/A'
    get_wallet_balance.short_description = 'Wallet Balance'
    get_wallet_balance.admin_order_field = 'profile__wallet_balance'
    
    def get_is_verified(self, obj):
        return obj.profile.is_verified if hasattr(obj, 'profile') else False
    get_is_verified.boolean = True
    get_is_verified.short_description = 'Verified'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'wallet_balance', 'total_winnings', 'is_verified', 'is_blocked', 'created_at')
    list_filter = ('is_verified', 'is_blocked', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('total_deposits', 'total_withdrawals', 'total_winnings', 'total_spent', 'created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone_number', 'date_of_birth')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Wallet & Statistics', {
            'fields': (
                'wallet_balance',
                ('total_deposits', 'total_withdrawals'),
                ('total_winnings', 'total_spent')
            )
        }),
        ('Account Status', {
            'fields': ('is_verified', 'is_blocked', 'blocked_reason')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_users', 'block_users', 'unblock_users', 'add_bonus_credits']
    
    def verify_users(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} user(s) verified successfully.')
    verify_users.short_description = "Verify selected users"
    
    def block_users(self, request, queryset):
        updated = queryset.update(is_blocked=True)
        self.message_user(request, f'{updated} user(s) blocked successfully.')
    block_users.short_description = "Block selected users"
    
    def unblock_users(self, request, queryset):
        updated = queryset.update(is_blocked=False, blocked_reason='')
        self.message_user(request, f'{updated} user(s) unblocked successfully.')
    unblock_users.short_description = "Unblock selected users"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
