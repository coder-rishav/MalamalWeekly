# Multi-Currency System for Malamal Weekly

## Overview
Complete multi-currency support system for your lottery platform with:
- Multiple currency support (INR, USD, EUR, GBP, AUD, CAD, SGD, AED, etc.)
- Real-time currency conversion
- User currency preferences
- Exchange rate management
- Conversion audit logging

## Installation

### 1. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Initialize Default Currencies
```bash
# Initialize currencies only
python manage.py init_currencies

# Initialize currencies with sample exchange rates
python manage.py init_currencies --with-rates
```

## Features

### Currency Model
- ISO 4217 currency codes (USD, EUR, INR, etc.)
- Customizable symbol position (before/after amount)
- Configurable decimal places and separators
- Base currency designation
- Active/inactive status

### Exchange Rate Model
- Bidirectional conversion rates
- Time-effective rates (effective_from, effective_until)
- Multiple rate sources (manual, API)
- Automatic reverse rate calculation

### Currency Conversion Log
- Full audit trail of all conversions
- User tracking
- Transaction linking
- Exchange rate used for each conversion

## Usage

### In Python Code

```python
from transactions.currency_utils import CurrencyManager

# Get user's preferred currency
user_currency = CurrencyManager.get_user_currency(request.user)

# Convert amount between currencies
converted = CurrencyManager.convert(
    amount=1000,
    from_currency='INR',
    to_currency='USD',
    user=request.user,
    transaction_type='deposit'
)

# Format amount with currency symbol
formatted = CurrencyManager.format_amount(1000, 'USD')
# Output: $1,000.00
```

### In Templates

```django
{% load currency_tags %}

{# Format amount in base currency #}
{{ amount|currency_format }}

{# Format amount in specific currency #}
{{ amount|currency_format:"USD" }}

{# Convert and format #}
{{ amount|convert_currency:"INR,USD" }}

{# Format in user's preferred currency #}
{% format_user_amount 1000 request.user %}

{# Currency selector dropdown #}
{% currency_selector user.profile.preferred_currency %}
```

### In Admin Panel

1. **Currencies Management** (`/admin/transactions/currency/`)
   - Add/edit currencies
   - Set base currency
   - Enable/disable currencies
   - Configure display settings

2. **Exchange Rates** (`/admin/transactions/exchangerate/`)
   - Add/update exchange rates
   - Set validity periods
   - Track rate sources

3. **Conversion Logs** (`/admin/transactions/currencyconversionlog/`)
   - View all currency conversions
   - Audit trail
   - User activity tracking

## Database Schema

### Currency
- `code`: ISO 4217 code (e.g., USD, EUR)
- `name`: Full name
- `symbol`: Currency symbol
- `symbol_position`: before/after
- `decimal_places`: Number of decimals
- `is_active`: Enable/disable
- `is_base_currency`: Base currency flag

### ExchangeRate
- `from_currency`: Source currency (FK)
- `to_currency`: Target currency (FK)
- `rate`: Exchange rate value
- `effective_from`: When rate becomes active
- `effective_until`: When rate expires
- `source`: Rate source (manual, API, etc.)

### CurrencyConversionLog
- `from_currency`: Source currency (FK)
- `to_currency`: Target currency (FK)
- `from_amount`: Original amount
- `to_amount`: Converted amount
- `exchange_rate_used`: Rate used
- `user`: User who made conversion
- `transaction_type`: deposit/withdrawal/etc.
- `transaction_id`: Related transaction

## API Integration (Future Enhancement)

You can integrate with exchange rate APIs like:
- Open Exchange Rates API
- Fixer.io
- CurrencyLayer
- Exchange Rates API

Example integration structure:
```python
# In currency_utils.py
def update_rates_from_api():
    # Fetch latest rates from API
    # Update ExchangeRate records
    pass
```

## User Currency Preference

Users can set their preferred currency in their profile:
```python
# In views
user.profile.preferred_currency = Currency.objects.get(code='USD')
user.profile.save()
```

All amounts will be automatically converted and displayed in their preferred currency.

## Best Practices

1. **Set Base Currency**: Always have one base currency (usually your local currency)
2. **Update Rates Regularly**: Keep exchange rates up-to-date
3. **Cache Currencies**: Currencies are cached for performance
4. **Log Conversions**: All conversions are logged for audit purposes
5. **Handle Errors**: Always handle currency conversion errors gracefully

## Clearing Cache

```python
from transactions.currency_utils import CurrencyManager

# Clear all currency cache
CurrencyManager.clear_cache()
```

## Sample Exchange Rates (as initialized)

| From | To  | Rate   |
|------|-----|--------|
| INR  | USD | 0.012  |
| INR  | EUR | 0.011  |
| INR  | GBP | 0.0095 |
| INR  | AUD | 0.018  |
| INR  | CAD | 0.016  |
| INR  | SGD | 0.016  |
| INR  | AED | 0.044  |

**Note**: These are sample rates. Update them with real-time rates in production.

## Troubleshooting

### No exchange rate found error
- Make sure exchange rates are initialized
- Check if currencies are active
- Verify rates are within validity period

### Currency not displaying correctly
- Check symbol_position setting
- Verify decimal_places configuration
- Clear cache: `CurrencyManager.clear_cache()`

### Conversion not logged
- Ensure user and transaction_type are provided
- Check database permissions

## Support

For any issues or questions:
1. Check admin panel for currency and rate configuration
2. Review conversion logs for audit trail
3. Clear cache if displaying old data
4. Ensure migrations are applied

## Future Enhancements

- [ ] Automatic rate updates via API
- [ ] Multi-currency wallet support
- [ ] Currency-specific payment gateways
- [ ] Historical rate tracking and charts
- [ ] Bulk rate updates
- [ ] Rate change notifications
