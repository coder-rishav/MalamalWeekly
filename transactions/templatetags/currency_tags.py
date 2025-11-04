from django import template
from decimal import Decimal
from transactions.currency_utils import CurrencyManager

register = template.Library()


@register.filter(name='currency_format')
def currency_format(amount, currency_code=None):
    """
    Format amount with currency symbol
    Usage: {{ amount|currency_format:"USD" }}
    """
    if currency_code:
        currency = CurrencyManager.get_currency_by_code(currency_code)
    else:
        currency = CurrencyManager.get_base_currency()
    
    if not currency:
        return f"{amount}"
    
    return currency.format_amount(amount)


@register.filter(name='convert_currency')
def convert_currency(amount, currencies):
    """
    Convert amount from one currency to another
    Usage: {{ amount|convert_currency:"USD,EUR" }}
    """
    try:
        from_code, to_code = currencies.split(',')
        converted = CurrencyManager.convert(amount, from_code.strip(), to_code.strip())
        to_currency = CurrencyManager.get_currency_by_code(to_code.strip())
        return to_currency.format_amount(converted) if to_currency else converted
    except Exception as e:
        return amount


@register.simple_tag(name='user_currency')
def user_currency(user):
    """
    Get user's preferred currency
    Usage: {% user_currency request.user as currency %}
    """
    return CurrencyManager.get_user_currency(user)


@register.simple_tag(name='format_user_amount')
def format_user_amount(amount, user):
    """
    Format amount in user's preferred currency
    Usage: {% format_user_amount 1000 request.user %}
    """
    currency = CurrencyManager.get_user_currency(user)
    if currency:
        return currency.format_amount(amount)
    return str(amount)


@register.inclusion_tag('transactions/currency_selector.html')
def currency_selector(selected_currency=None):
    """
    Render currency selector dropdown
    Usage: {% currency_selector user.profile.preferred_currency %}
    """
    currencies = CurrencyManager.get_active_currencies()
    return {
        'currencies': currencies,
        'selected': selected_currency,
    }
