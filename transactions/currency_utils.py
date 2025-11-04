"""
Utility functions for currency management and conversion
"""
from decimal import Decimal
from django.core.cache import cache
from .currency_models import Currency, ExchangeRate, CurrencyConversionLog


class CurrencyManager:
    """Helper class for currency operations"""
    
    @staticmethod
    def get_base_currency():
        """Get the platform's base currency"""
        cache_key = 'base_currency'
        base_currency = cache.get(cache_key)
        
        if not base_currency:
            base_currency = Currency.objects.filter(is_base_currency=True, is_active=True).first()
            if base_currency:
                cache.set(cache_key, base_currency, 3600)  # Cache for 1 hour
        
        return base_currency
    
    @staticmethod
    def get_active_currencies():
        """Get all active currencies"""
        cache_key = 'active_currencies'
        currencies = cache.get(cache_key)
        
        if not currencies:
            currencies = list(Currency.objects.filter(is_active=True).order_by('display_order', 'code'))
            cache.set(cache_key, currencies, 3600)
        
        return currencies
    
    @staticmethod
    def get_currency_by_code(code):
        """Get currency by code"""
        cache_key = f'currency_{code}'
        currency = cache.get(cache_key)
        
        if not currency:
            try:
                currency = Currency.objects.get(code=code, is_active=True)
                cache.set(cache_key, currency, 3600)
            except Currency.DoesNotExist:
                return None
        
        return currency
    
    @staticmethod
    def convert(amount, from_currency, to_currency, user=None, transaction_type=None, transaction_id=None):
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Currency object or currency code
            to_currency: Currency object or currency code
            user: User object (for logging)
            transaction_type: Type of transaction (for logging)
            transaction_id: Related transaction ID (for logging)
        
        Returns:
            Converted amount as Decimal
        """
        # Handle currency code strings
        if isinstance(from_currency, str):
            from_currency = CurrencyManager.get_currency_by_code(from_currency)
        if isinstance(to_currency, str):
            to_currency = CurrencyManager.get_currency_by_code(to_currency)
        
        if not from_currency or not to_currency:
            raise ValueError("Invalid currency")
        
        # If same currency, no conversion needed
        if from_currency == to_currency:
            return Decimal(str(amount))
        
        # Get exchange rate and convert
        converted_amount = ExchangeRate.convert_amount(amount, from_currency, to_currency)
        
        # Log the conversion
        if user or transaction_type:
            rate = ExchangeRate.get_current_rate(from_currency, to_currency)
            CurrencyConversionLog.objects.create(
                from_currency=from_currency,
                to_currency=to_currency,
                from_amount=Decimal(str(amount)),
                to_amount=converted_amount,
                exchange_rate_used=rate,
                user=user,
                transaction_type=transaction_type or 'manual',
                transaction_id=transaction_id
            )
        
        return converted_amount
    
    @staticmethod
    def format_amount(amount, currency):
        """Format amount according to currency settings"""
        if isinstance(currency, str):
            currency = CurrencyManager.get_currency_by_code(currency)
        
        if not currency:
            return str(amount)
        
        return currency.format_amount(amount)
    
    @staticmethod
    def get_user_currency(user):
        """Get user's preferred currency or default to base currency"""
        if hasattr(user, 'profile') and user.profile.preferred_currency:
            return user.profile.preferred_currency
        return CurrencyManager.get_base_currency()
    
    @staticmethod
    def clear_cache():
        """Clear all currency-related cache"""
        cache.delete('base_currency')
        cache.delete('active_currencies')
        # Also clear individual currency caches
        for currency in Currency.objects.all():
            cache.delete(f'currency_{currency.code}')


def initialize_default_currencies():
    """Initialize default currencies - run this once during setup"""
    default_currencies = [
        {
            'code': 'INR',
            'name': 'Indian Rupee',
            'symbol': '₹',
            'symbol_position': 'before',
            'is_base_currency': True,
            'display_order': 1,
        },
        {
            'code': 'USD',
            'name': 'US Dollar',
            'symbol': '$',
            'symbol_position': 'before',
            'display_order': 2,
        },
        {
            'code': 'EUR',
            'name': 'Euro',
            'symbol': '€',
            'symbol_position': 'before',
            'display_order': 3,
        },
        {
            'code': 'GBP',
            'name': 'British Pound',
            'symbol': '£',
            'symbol_position': 'before',
            'display_order': 4,
        },
        {
            'code': 'AUD',
            'name': 'Australian Dollar',
            'symbol': 'A$',
            'symbol_position': 'before',
            'display_order': 5,
        },
        {
            'code': 'CAD',
            'name': 'Canadian Dollar',
            'symbol': 'C$',
            'symbol_position': 'before',
            'display_order': 6,
        },
        {
            'code': 'SGD',
            'name': 'Singapore Dollar',
            'symbol': 'S$',
            'symbol_position': 'before',
            'display_order': 7,
        },
        {
            'code': 'AED',
            'name': 'UAE Dirham',
            'symbol': 'د.إ',
            'symbol_position': 'before',
            'display_order': 8,
        },
    ]
    
    created_currencies = []
    for curr_data in default_currencies:
        currency, created = Currency.objects.get_or_create(
            code=curr_data['code'],
            defaults=curr_data
        )
        if created:
            created_currencies.append(currency)
    
    return created_currencies


def set_exchange_rates_to_inr():
    """Set sample exchange rates (1 INR = X currency)"""
    # Get INR as base currency
    try:
        inr = Currency.objects.get(code='INR')
    except Currency.DoesNotExist:
        print("INR currency not found. Please run initialize_default_currencies() first.")
        return
    
    # Sample exchange rates (as of example - you should use real-time rates)
    rates = {
        'USD': Decimal('0.012'),      # 1 INR = 0.012 USD
        'EUR': Decimal('0.011'),      # 1 INR = 0.011 EUR
        'GBP': Decimal('0.0095'),     # 1 INR = 0.0095 GBP
        'AUD': Decimal('0.018'),      # 1 INR = 0.018 AUD
        'CAD': Decimal('0.016'),      # 1 INR = 0.016 CAD
        'SGD': Decimal('0.016'),      # 1 INR = 0.016 SGD
        'AED': Decimal('0.044'),      # 1 INR = 0.044 AED
    }
    
    created_rates = []
    for code, rate in rates.items():
        try:
            to_currency = Currency.objects.get(code=code)
            
            # Create rate from INR to other currency
            exchange_rate, created = ExchangeRate.objects.get_or_create(
                from_currency=inr,
                to_currency=to_currency,
                defaults={
                    'rate': rate,
                    'source': 'manual',
                    'is_active': True,
                }
            )
            
            if created:
                created_rates.append(exchange_rate)
            
            # Also create reverse rate
            reverse_rate, created = ExchangeRate.objects.get_or_create(
                from_currency=to_currency,
                to_currency=inr,
                defaults={
                    'rate': Decimal('1.0') / rate,
                    'source': 'manual',
                    'is_active': True,
                }
            )
            
            if created:
                created_rates.append(reverse_rate)
                
        except Currency.DoesNotExist:
            print(f"Currency {code} not found")
            continue
    
    return created_rates
