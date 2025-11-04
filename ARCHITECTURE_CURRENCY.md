# Multi-Currency System Architecture

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        MALAMAL WEEKLY LOTTERY                            │
│                      Multi-Currency System v1.0                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────┐      ┌───────────────────────────────┐   │
│  │   User Currency Page     │      │   Admin Currency Management   │   │
│  ├──────────────────────────┤      ├───────────────────────────────┤   │
│  │ • View all currencies    │      │ • Currencies List             │   │
│  │ • Select preference      │      │ • Currency Create/Edit        │   │
│  │ • Save selection         │      │ • Toggle Status               │   │
│  │ • Visual currency cards  │      │ • Exchange Rates List         │   │
│  │                          │      │ • Rate Create/Edit/Delete     │   │
│  │ Route:                   │      │ • Statistics Dashboard        │   │
│  │ /accounts/profile/       │      │ • Advanced Filters            │   │
│  │   currency/              │      │                               │   │
│  └──────────────────────────┘      │ Routes:                       │   │
│                                     │ /admin/currencies/*           │   │
│                                     │ /admin/exchange-rates/*       │   │
│                                     └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         VIEW & CONTROLLER LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────┐      ┌───────────────────────────────┐   │
│  │   accounts/views.py      │      │   custom_admin/views.py       │   │
│  ├──────────────────────────┤      ├───────────────────────────────┤   │
│  │ change_currency()        │      │ currencies_list()             │   │
│  │  • GET: Display form     │      │ currency_create()             │   │
│  │  • POST: Save preference │      │ currency_edit()               │   │
│  │  • Clear cache           │      │ currency_toggle_status()      │   │
│  │  • Show messages         │      │ exchange_rates_list()         │   │
│  └──────────────────────────┘      │ exchange_rate_create()        │   │
│                                     │ exchange_rate_edit()          │   │
│                                     │ exchange_rate_delete()        │   │
│                                     └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               CurrencyManager Class                              │   │
│  │              (currency_utils.py)                                 │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  Core Methods:                                                   │   │
│  │  • convert(amount, from_currency, to_currency, user)            │   │
│  │  • format_amount(amount, currency_code)                         │   │
│  │  • get_user_currency(user)                                      │   │
│  │  • get_active_currencies()                                       │   │
│  │  • get_cached_currency(code)                                    │   │
│  │  • clear_cache()                                                │   │
│  │                                                                   │   │
│  │  Helper Functions:                                               │   │
│  │  • initialize_default_currencies()                              │   │
│  │  • set_exchange_rates_to_inr()                                  │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │               Template Tags                                      │   │
│  │              (currency_tags.py)                                  │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │  • currency_format(amount, code)                                │   │
│  │  • convert_currency(amount, from_to)                            │   │
│  │  • user_currency(user)                                          │   │
│  │  • format_user_amount(amount, user)                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA ACCESS LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐   │
│  │   Currency Model         │  │   ExchangeRate Model              │   │
│  ├──────────────────────────┤  ├──────────────────────────────────┤   │
│  │ • code (PK)              │  │ • from_currency (FK)              │   │
│  │ • name                   │  │ • to_currency (FK)                │   │
│  │ • symbol                 │  │ • rate (Decimal)                  │   │
│  │ • symbol_position        │  │ • source                          │   │
│  │ • decimal_places         │  │ • is_active                       │   │
│  │ • thousand_separator     │  │ • effective_from                  │   │
│  │ • decimal_separator      │  │ • effective_until                 │   │
│  │ • is_active              │  │                                   │   │
│  │ • is_base_currency       │  │ Methods:                          │   │
│  │ • display_order          │  │ • get_current_rate()              │   │
│  │                          │  │ • convert_amount()                │   │
│  │ Methods:                 │  │                                   │   │
│  │ • format_amount()        │  └──────────────────────────────────┘   │
│  └──────────────────────────┘                                           │
│                                                                           │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐   │
│  │ UserProfile Model        │  │ CurrencyConversionLog Model       │   │
│  ├──────────────────────────┤  ├──────────────────────────────────┤   │
│  │ • preferred_currency (FK)│  │ • user (FK)                       │   │
│  │ • ... other fields       │  │ • from_currency (FK)              │   │
│  └──────────────────────────┘  │ • to_currency (FK)                │   │
│                                 │ • amount                          │   │
│                                 │ • converted_amount                │   │
│                                 │ • rate_used                       │   │
│                                 │ • timestamp                       │   │
│                                 └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                            CACHE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Django Cache Framework                        │   │
│  │                    (1 Hour Expiration)                           │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  Cached Items:                                                   │   │
│  │  • currencies_all          → All Currency objects               │   │
│  │  • currency_{code}         → Single Currency object             │   │
│  │  • exchange_rate_{from}_{to} → Exchange rate value              │   │
│  │  • user_currency_{user_id} → User's preferred currency          │   │
│  │                                                                   │   │
│  │  Auto-Clear Events:                                              │   │
│  │  • Currency created/updated/deleted                              │   │
│  │  • Exchange rate created/updated/deleted                         │   │
│  │  • User currency preference changed                              │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATABASE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                       MySQL Database                             │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  Tables:                                                         │   │
│  │  • transactions_currency                                         │   │
│  │  • transactions_exchangerate                                     │   │
│  │  • transactions_currencyconversionlog                            │   │
│  │  • accounts_userprofile (with preferred_currency FK)             │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. User Selects Currency Flow

```
┌─────────┐
│  User   │
└────┬────┘
     │
     │ 1. Navigate to /accounts/profile/currency/
     ↓
┌────────────────┐
│ change_currency│
│     View       │
└────┬───────────┘
     │
     │ 2. GET Request - Display form
     ↓
┌────────────────┐
│ CurrencyManager│
│.get_active_    │
│  currencies()  │
└────┬───────────┘
     │
     │ 3. Check cache
     ↓
┌────────────────┐         Cache Miss
│     Cache      ├──────────────────┐
└────┬───────────┘                  │
     │                               ↓
     │ Cache Hit            ┌────────────────┐
     ↓                      │    Database    │
┌────────────────┐          │  Query Active  │
│  Return cached │          │   Currencies   │
│   currencies   │          └────┬───────────┘
└────┬───────────┘               │
     │                            │ 4. Store in cache
     │ ←──────────────────────────┘
     │
     │ 5. Render template with currencies
     ↓
┌────────────────┐
│  User sees     │
│  currency      │
│  selection UI  │
└────┬───────────┘
     │
     │ 6. User selects currency and submits
     ↓
┌────────────────┐
│ POST Request   │
└────┬───────────┘
     │
     │ 7. Save to UserProfile
     ↓
┌────────────────┐
│   Database     │
│   UPDATE       │
│  UserProfile   │
└────┬───────────┘
     │
     │ 8. Clear user's currency cache
     ↓
┌────────────────┐
│  Cache.delete  │
│ ('user_currency│
│    _{id}')     │
└────┬───────────┘
     │
     │ 9. Redirect with success message
     ↓
┌────────────────┐
│  User Profile  │
│      Page      │
└────────────────┘
```

### 2. Admin Creates Exchange Rate Flow

```
┌─────────┐
│  Admin  │
└────┬────┘
     │
     │ 1. Navigate to /admin/exchange-rates/create/
     ↓
┌────────────────────┐
│ exchange_rate_     │
│    create View     │
└────┬───────────────┘
     │
     │ 2. GET - Display form with active currencies
     ↓
┌────────────────────┐
│  Admin sees form   │
│  • From Currency   │
│  • To Currency     │
│  • Rate            │
│  • Status          │
└────┬───────────────┘
     │
     │ 3. Admin fills form and submits
     ↓
┌────────────────────┐
│   POST Request     │
└────┬───────────────┘
     │
     │ 4. Validate
     ├─→ From ≠ To?
     ├─→ Rate > 0?
     ├─→ Currencies exist?
     │
     │ 5. Create ExchangeRate object
     ↓
┌────────────────────┐
│    Database        │
│    INSERT INTO     │
│  ExchangeRate      │
└────┬───────────────┘
     │
     │ 6. Clear cache
     ↓
┌────────────────────┐
│ CurrencyManager    │
│   .clear_cache()   │
└────┬───────────────┘
     │
     │ 7. Delete all currency-related cache keys
     ↓
┌────────────────────┐
│  Cache cleared:    │
│  • currencies_all  │
│  • exchange_rate_* │
│  • user_currency_* │
└────┬───────────────┘
     │
     │ 8. Redirect with success message
     ↓
┌────────────────────┐
│ Exchange Rates     │
│    List Page       │
└────────────────────┘
```

### 3. Currency Conversion Flow

```
┌─────────────┐
│ Application │
│  Needs to   │
│  Convert    │
└──────┬──────┘
       │
       │ 1. Call CurrencyManager.convert()
       ↓
┌───────────────────┐
│ CurrencyManager   │
│   .convert()      │
└──────┬────────────┘
       │
       │ 2. Get exchange rate
       ↓
┌───────────────────┐
│  Check cache for  │
│  exchange_rate_   │
│  {from}_{to}      │
└──────┬────────────┘
       │
       ├─→ Cache Hit ─────────────┐
       │                          │
       │ Cache Miss               │
       ↓                          │
┌───────────────────┐             │
│ ExchangeRate.     │             │
│ get_current_rate()│             │
└──────┬────────────┘             │
       │                          │
       │ 3. Query database        │
       ↓                          │
┌───────────────────┐             │
│   Check FROM→TO   │             │
│   If not found,   │             │
│   try TO→FROM     │             │
│   (reverse)       │             │
└──────┬────────────┘             │
       │                          │
       │ 4. Store in cache        │
       ↓                          │
┌───────────────────┐             │
│  Cache.set()      │             │
│  (1 hour)         │             │
└──────┬────────────┘             │
       │                          │
       │ ←────────────────────────┘
       │
       │ 5. Calculate: amount × rate
       ↓
┌───────────────────┐
│  converted_amount │
└──────┬────────────┘
       │
       │ 6. Log conversion (if user provided)
       ↓
┌───────────────────┐
│ CurrencyConversion│
│     Log.create()  │
└──────┬────────────┘
       │
       │ 7. Return converted amount
       ↓
┌───────────────────┐
│   Application     │
└───────────────────┘
```

### 4. Template Tag Usage Flow

```
┌────────────────┐
│   Template     │
│   Rendering    │
└───────┬────────┘
        │
        │ {% load currency_tags %}
        │ {{ amount|currency_format:"USD" }}
        ↓
┌────────────────┐
│ currency_format│
│   filter       │
└───────┬────────┘
        │
        │ 1. Get currency from cache/DB
        ↓
┌────────────────┐
│ CurrencyManager│
│.get_cached_    │
│  currency()    │
└───────┬────────┘
        │
        │ 2. Format amount
        ↓
┌────────────────┐
│   Currency     │
│ .format_amount │
│      ()        │
└───────┬────────┘
        │
        │ 3. Apply formatting rules:
        │    • Add thousand separators
        │    • Set decimal places
        │    • Add currency symbol
        │    • Position symbol
        ↓
┌────────────────┐
│  Return        │
│  "$1,234.56"   │
└───────┬────────┘
        │
        │ 4. Insert into template
        ↓
┌────────────────┐
│  Rendered HTML │
└────────────────┘
```

---

## Component Relationships

```
                    ┌──────────────────────────┐
                    │    UserProfile Model     │
                    │  (accounts app)          │
                    └────────┬─────────────────┘
                             │
                             │ preferred_currency (FK)
                             ↓
    ┌────────────────────────────────────────────────┐
    │           Currency Model                       │
    │        (transactions app)                      │
    └────────┬───────────────────────┬───────────────┘
             │                       │
             │ from_currency (FK)    │ to_currency (FK)
             ↓                       ↓
    ┌────────────────────────────────────────────────┐
    │         ExchangeRate Model                     │
    │        (transactions app)                      │
    └────────┬───────────────────────────────────────┘
             │
             │ Used by conversion
             ↓
    ┌────────────────────────────────────────────────┐
    │     CurrencyConversionLog Model                │
    │        (transactions app)                      │
    │  • Logs all conversions                        │
    │  • Links to User                               │
    │  • Links to FROM/TO currencies                 │
    └────────────────────────────────────────────────┘
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MALAMAL WEEKLY MODULES                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Accounts    │    │     Games    │    │ Transactions │
│   Module     │    │    Module    │    │    Module    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       │ User currency     │ Prize amounts      │ Deposits/
       │ preference        │ Ticket prices      │ Withdrawals
       │                   │                    │
       └───────────────────┴────────────────────┘
                           │
                           │ All use
                           ↓
              ┌────────────────────────┐
              │   Currency System      │
              │   (Multi-Currency)     │
              └────────────────────────┘
                           │
                           │ Provides
                           ↓
                ┌──────────────────────┐
                │  • Currency list     │
                │  • Conversion        │
                │  • Formatting        │
                │  • User preference   │
                └──────────────────────┘
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                         │
└─────────────────────────────────────────────────────────────┘

Layer 1: Authentication
┌─────────────────────────────────────────────────────────────┐
│  @login_required                                             │
│  • User must be logged in                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
Layer 2: Authorization
┌─────────────────────────────────────────────────────────────┐
│  @user_passes_test(is_admin)                                 │
│  • Only admin can access currency management                 │
│  • Users can only modify their own currency                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
Layer 3: Validation
┌─────────────────────────────────────────────────────────────┐
│  • Currency code format (3 uppercase letters)                │
│  • Exchange rate > 0                                         │
│  • FROM ≠ TO currency                                        │
│  • Decimal places 0-8                                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓
Layer 4: Audit Trail
┌─────────────────────────────────────────────────────────────┐
│  CurrencyConversionLog                                       │
│  • Track all conversions                                     │
│  • Log user, amount, rate                                    │
│  • Timestamp all operations                                  │
└─────────────────────────────────────────────────────────────┘
```

---

*This architecture documentation provides a visual representation of the multi-currency system structure and data flows.*
