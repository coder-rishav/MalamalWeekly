from django.contrib import admin
from .currency_models import Currency, ExchangeRate, CurrencyConversionLog


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'is_active', 'is_base_currency', 'display_order']
    list_filter = ['is_active', 'is_base_currency']
    search_fields = ['code', 'name']
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', 'code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'symbol')
        }),
        ('Display Settings', {
            'fields': ('symbol_position', 'decimal_places', 'thousand_separator', 'decimal_separator')
        }),
        ('Status', {
            'fields': ('is_active', 'is_base_currency', 'display_order')
        }),
    )


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate', 'is_active', 'source', 'effective_from', 'effective_until']
    list_filter = ['is_active', 'source', 'effective_from']
    search_fields = ['from_currency__code', 'to_currency__code']
    list_editable = ['is_active']
    ordering = ['-effective_from']
    date_hierarchy = 'effective_from'
    
    fieldsets = (
        ('Currency Pair', {
            'fields': ('from_currency', 'to_currency', 'rate')
        }),
        ('Validity', {
            'fields': ('is_active', 'effective_from', 'effective_until')
        }),
        ('Source', {
            'fields': ('source',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.source or obj.source == 'manual':
            obj.source = f'manual_by_{request.user.username}'
        super().save_model(request, obj, form, change)


@admin.register(CurrencyConversionLog)
class CurrencyConversionLogAdmin(admin.ModelAdmin):
    list_display = ['converted_at', 'user', 'from_amount', 'from_currency', 'to_amount', 'to_currency', 'exchange_rate_used', 'transaction_type']
    list_filter = ['transaction_type', 'from_currency', 'to_currency', 'converted_at']
    search_fields = ['user__username', 'user__email', 'transaction_id']
    readonly_fields = ['converted_at', 'from_currency', 'to_currency', 'from_amount', 'to_amount', 'exchange_rate_used', 'user']
    date_hierarchy = 'converted_at'
    ordering = ['-converted_at']
    
    def has_add_permission(self, request):
        return False  # Logs are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # Logs should not be modified
