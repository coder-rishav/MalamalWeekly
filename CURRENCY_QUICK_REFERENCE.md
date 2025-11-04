# Currency Management - Quick Reference

## 🚀 Quick Start

### Initialize Currencies (First Time Only)
```bash
python manage.py init_currencies
```
This creates 8 default currencies with exchange rates.

---

## 👤 For Users

**Change Currency Preference:**
1. Go to your Profile
2. Click "Change Currency" or visit: `/accounts/profile/currency/`
3. Select your preferred currency
4. Click "Save Preference"

**Supported Currencies:**
- 🇮🇳 INR - Indian Rupee (Base)
- 🇺🇸 USD - US Dollar
- 🇪🇺 EUR - Euro
- 🇬🇧 GBP - British Pound
- 🇦🇺 AUD - Australian Dollar
- 🇨🇦 CAD - Canadian Dollar
- 🇸🇬 SGD - Singapore Dollar
- 🇦🇪 AED - UAE Dirham

---

## 👨‍💼 For Admins

### Access Currency Management
**URL:** `/admin/currencies/` or click "Currencies" in admin sidebar

### Common Tasks

#### 1️⃣ Add New Currency
```
Navigate to: Currencies → Add New Currency
Fill in:
  - Code (3 letters, e.g., JPY)
  - Name (e.g., Japanese Yen)
  - Symbol (e.g., ¥)
  - Symbol Position (before/after)
  - Decimal Places (usually 2, some like JPY use 0)
  - Separators (thousand & decimal)
  - Active status ✓
  - Base currency (only one should be marked)
Click: Create Currency
```

#### 2️⃣ Edit Currency
```
Navigate to: Currencies → Edit icon
Modify: Any field
Watch: Live preview updates
Click: Update Currency
```

#### 3️⃣ Activate/Deactivate Currency
```
Navigate to: Currencies → Toggle icon
Confirm: Yes/No
Result: Status changes immediately
```

#### 4️⃣ Add Exchange Rate
```
Navigate to: Exchange Rates → Add New Rate
Select:
  - FROM Currency (e.g., USD)
  - TO Currency (e.g., EUR)
Enter: Rate (e.g., 0.85 means 1 USD = 0.85 EUR)
Watch: Preview shows conversion
Check: Active status ✓
Click: Create Exchange Rate
```

#### 5️⃣ Update Exchange Rate
```
Navigate to: Exchange Rates → Edit icon
Note: FROM/TO currencies cannot be changed
Modify: Rate value only
Watch: Preview updates
Click: Update Exchange Rate
```

#### 6️⃣ Delete Exchange Rate
```
Navigate to: Exchange Rates → Delete icon
Confirm: Yes
Result: Rate removed permanently
```

---

## 📊 Admin Dashboard Features

### Currencies Page
- **Statistics Cards:**
  - Total Currencies
  - Active Currencies
  - Inactive Currencies
  
- **Table Columns:**
  - Code, Name, Symbol
  - Symbol Position
  - Decimal Places
  - Thousand/Decimal Separators
  - Base Currency Flag
  - Active Status
  - Display Order
  - Actions (Edit, Toggle)

### Exchange Rates Page
- **Statistics Cards:**
  - Total Exchange Rates
  - Active Rates
  
- **Filters:**
  - From Currency
  - To Currency
  - Status (Active/Inactive)
  
- **Table Columns:**
  - From → To Currencies
  - Exchange Rate
  - Reverse Rate
  - Source
  - Effective Date
  - Status
  - Actions (Edit, Delete)
  
- **Quick Reference:**
  - Top 6 active rates for quick lookup

---

## 🔧 Technical Reference

### Template Tags (Use in Templates)
```django
{% load currency_tags %}

<!-- Format amount with specific currency -->
{{ amount|currency_format:"USD" }}
<!-- Output: $1,234.56 -->

<!-- Convert amount between currencies -->
{{ amount|convert_currency:"USD,EUR" }}
<!-- Output: Converted amount -->

<!-- Get user's preferred currency -->
{% user_currency user as user_currency %}
{{ user_currency.code }}
<!-- Output: INR -->

<!-- Format amount in user's currency -->
{% format_user_amount amount user as formatted %}
{{ formatted }}
<!-- Output: ₹1,234.56 -->
```

### Python API (Use in Views)
```python
from transactions.currency_utils import CurrencyManager

# Convert amount
manager = CurrencyManager()
converted = manager.convert(
    amount=100,
    from_currency='USD',
    to_currency='INR',
    user=request.user  # Optional, for logging
)

# Format amount
formatted = manager.format_amount(
    amount=1234.56,
    currency_code='USD'
)
# Output: $1,234.56

# Get user's currency
user_currency = manager.get_user_currency(request.user)

# Get active currencies
currencies = manager.get_active_currencies()

# Clear cache (after manual updates)
CurrencyManager.clear_cache()
```

### Database Queries
```python
from transactions.currency_models import Currency, ExchangeRate

# Get all active currencies
currencies = Currency.objects.filter(is_active=True)

# Get base currency
base = Currency.objects.get(is_base_currency=True)

# Get exchange rate
rate = ExchangeRate.get_current_rate('USD', 'INR')

# Convert amount
converted = ExchangeRate.convert_amount(100, 'USD', 'EUR')
```

---

## ⚠️ Important Notes

### Currency Codes
- Must be 3 letters (ISO 4217 standard)
- Automatically converted to UPPERCASE
- Common codes: USD, EUR, GBP, INR, JPY, CNY, AUD, CAD, CHF, SEK, NZD, MXN, SGD, HKD, NOK, KRW, TRY, RUB, BRL, ZAR

### Base Currency
- **Only ONE currency should be marked as base**
- Base currency is used as reference for conversions
- Currently: INR (Indian Rupee)
- Changing base requires updating all exchange rates

### Exchange Rates
- FROM and TO currencies must be different
- Rate represents: 1 FROM = X TO
- Example: 1 USD = 83.50 INR means rate is 83.50
- Reverse conversion calculated automatically
- Use 6 decimal places for accuracy

### Decimal Places
- Most currencies: 2 decimal places (USD, EUR, INR)
- Some currencies: 0 decimal places (JPY, KRW)
- Some currencies: 3 decimal places (KWD, BHD, OMR)

### Symbol Position
- Most Western: Before amount ($100, €100, £100)
- Some currencies: After amount (100₹, 100¥)

### Caching
- All currency data cached for 1 hour
- Cache auto-cleared on CRUD operations
- Manual clear: `CurrencyManager.clear_cache()`

---

## 🐛 Troubleshooting

### Problem: Currency not showing in user dropdown
**Solution:** Check if currency is marked as Active in admin panel

### Problem: Exchange rate not working
**Solution:** 
1. Check if both currencies are Active
2. Check if exchange rate is Active
3. Verify rate is > 0
4. Clear cache: `CurrencyManager.clear_cache()`

### Problem: Wrong conversion amount
**Solution:**
1. Verify exchange rate value is correct
2. Check if correct FROM/TO currency order
3. Remember: Rate is always "1 FROM = X TO"

### Problem: Symbol showing in wrong position
**Solution:** Edit currency and change "Symbol Position" setting

### Problem: Wrong decimal places
**Solution:** Edit currency and adjust "Decimal Places" value

### Problem: Changes not reflecting immediately
**Solution:** Cache may be active. Wait 1 hour or clear cache manually

---

## 📞 Admin Quick Links

When logged in as admin:

| Feature | URL |
|---------|-----|
| Currencies List | `/admin/currencies/` |
| Add Currency | `/admin/currencies/create/` |
| Exchange Rates | `/admin/exchange-rates/` |
| Add Rate | `/admin/exchange-rates/create/` |
| User Currency Change | `/accounts/profile/currency/` |

---

## 💡 Pro Tips

1. **Regular Updates:** Update exchange rates regularly for accuracy
2. **Active Management:** Keep only actively used currencies active
3. **Display Order:** Use display order to prioritize common currencies
4. **Testing:** Test conversions after adding new rates
5. **Backup:** Backup currency data before major changes
6. **Monitoring:** Check conversion logs periodically
7. **User Experience:** Ensure user's selected currency is respected across all pages

---

## 📈 Best Practices

✅ **DO:**
- Keep exchange rates updated
- Use ISO 4217 standard codes
- Test conversions before going live
- Provide clear currency selection UI
- Cache currency data for performance
- Log all conversions for audit trail

❌ **DON'T:**
- Mark multiple currencies as base
- Use non-standard currency codes
- Forget to activate new currencies
- Delete currencies with transaction history
- Ignore cache clearing after updates
- Use overly complex currency symbols

---

*For detailed documentation, see: CURRENCY_SYSTEM_README.md*
*For implementation details, see: CURRENCY_IMPLEMENTATION_SUMMARY.md*
