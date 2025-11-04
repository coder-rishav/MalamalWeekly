from django.db import models
from django.utils import timezone
from decimal import Decimal


class Currency(models.Model):
    """Supported currencies for the platform"""
    code = models.CharField(max_length=3, unique=True, help_text="ISO 4217 currency code (e.g., USD, EUR, INR)")
    name = models.CharField(max_length=100, help_text="Full currency name")
    symbol = models.CharField(max_length=10, help_text="Currency symbol (e.g., $, €, ₹)")
    
    # Display settings
    symbol_position = models.CharField(
        max_length=10,
        choices=[('before', 'Before Amount'), ('after', 'After Amount')],
        default='before',
        help_text="Where to display the symbol"
    )
    decimal_places = models.IntegerField(default=2, help_text="Number of decimal places")
    thousand_separator = models.CharField(max_length=1, default=',', help_text="Separator for thousands")
    decimal_separator = models.CharField(max_length=1, default='.', help_text="Decimal separator")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Enable/disable this currency")
    is_base_currency = models.BooleanField(default=False, help_text="Is this the base currency for exchange rates?")
    display_order = models.IntegerField(default=0, help_text="Order in currency selection dropdown")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ['display_order', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.symbol})"
    
    def format_amount(self, amount):
        """Format amount according to currency settings"""
        # Round to specified decimal places
        amount = round(Decimal(str(amount)), self.decimal_places)
        
        # Format with separators
        amount_str = f"{amount:,.{self.decimal_places}f}"
        
        # Replace separators if custom
        if self.thousand_separator != ',':
            amount_str = amount_str.replace(',', self.thousand_separator)
        if self.decimal_separator != '.':
            amount_str = amount_str.replace('.', self.decimal_separator)
        
        # Add symbol
        if self.symbol_position == 'before':
            return f"{self.symbol}{amount_str}"
        else:
            return f"{amount_str} {self.symbol}"
    
    def save(self, *args, **kwargs):
        # Ensure only one base currency
        if self.is_base_currency:
            Currency.objects.filter(is_base_currency=True).exclude(pk=self.pk).update(is_base_currency=False)
        super().save(*args, **kwargs)


class ExchangeRate(models.Model):
    """Exchange rates between currencies"""
    from_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='rates_from',
        help_text="Convert from this currency"
    )
    to_currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
        related_name='rates_to',
        help_text="Convert to this currency"
    )
    rate = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        help_text="Exchange rate (1 from_currency = X to_currency)"
    )
    
    # Rate source and validity
    source = models.CharField(
        max_length=100,
        default='manual',
        help_text="Source of exchange rate (manual, API, etc.)"
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    effective_from = models.DateTimeField(default=timezone.now, help_text="When this rate becomes effective")
    effective_until = models.DateTimeField(null=True, blank=True, help_text="When this rate expires")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency', 'effective_from']
        ordering = ['-effective_from']
        indexes = [
            models.Index(fields=['from_currency', 'to_currency', 'is_active']),
            models.Index(fields=['effective_from', 'effective_until']),
        ]
    
    def __str__(self):
        return f"1 {self.from_currency.code} = {self.rate} {self.to_currency.code}"
    
    @classmethod
    def get_current_rate(cls, from_currency, to_currency):
        """Get current active exchange rate"""
        # If same currency, return 1
        if from_currency == to_currency:
            return Decimal('1.0')
        
        now = timezone.now()
        rate = cls.objects.filter(
            from_currency=from_currency,
            to_currency=to_currency,
            is_active=True,
            effective_from__lte=now
        ).filter(
            models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=now)
        ).first()
        
        if rate:
            return rate.rate
        
        # Try reverse rate
        reverse_rate = cls.objects.filter(
            from_currency=to_currency,
            to_currency=from_currency,
            is_active=True,
            effective_from__lte=now
        ).filter(
            models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=now)
        ).first()
        
        if reverse_rate:
            return Decimal('1.0') / reverse_rate.rate
        
        return None
    
    @classmethod
    def convert_amount(cls, amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        rate = cls.get_current_rate(from_currency, to_currency)
        if rate is None:
            raise ValueError(f"No exchange rate found for {from_currency.code} to {to_currency.code}")
        return Decimal(str(amount)) * rate


class CurrencyConversionLog(models.Model):
    """Log of currency conversions for audit trail"""
    from_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='conversions_from')
    to_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='conversions_to')
    from_amount = models.DecimalField(max_digits=15, decimal_places=2)
    to_amount = models.DecimalField(max_digits=15, decimal_places=2)
    exchange_rate_used = models.DecimalField(max_digits=20, decimal_places=8)
    
    # Context
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=50, help_text="deposit, withdrawal, game_entry, etc.")
    transaction_id = models.IntegerField(null=True, blank=True, help_text="Related transaction ID")
    
    # Metadata
    converted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-converted_at']
        indexes = [
            models.Index(fields=['user', 'converted_at']),
            models.Index(fields=['transaction_type', 'transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.from_amount} {self.from_currency.code} → {self.to_amount} {self.to_currency.code}"
