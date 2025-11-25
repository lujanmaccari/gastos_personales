"""
Template tags para conversión de monedas en templates
Ubicación: apps/utils/templatetags/currency_filters.py
"""
from django import template
from decimal import Decimal
from apps.utils.currency_service import CurrencyService

register = template.Library()

@register.filter
def convert_currency(amount, currencies):
    """
    Convierte un monto de una moneda a otra.
    
    Uso en template:
    {{ gasto.monto|convert_currency:"ARS,USD" }}
    {{ ingreso.monto|convert_currency:from_to_currencies }}
    
    Args:
        amount: Monto a convertir
        currencies: String "FROM,TO" (ej: "ARS,USD")
    """
    if not amount or not currencies:
        return amount
    
    try:
        from_currency, to_currency = currencies.split(',')
        from_currency = from_currency.strip()
        to_currency = to_currency.strip()
        
        if isinstance(amount, (int, float, Decimal)):
            amount = Decimal(str(amount))
        else:
            amount = Decimal(str(amount))
        
        converted = CurrencyService.convert_amount(
            amount, 
            from_currency, 
            to_currency
        )
        
        return converted if converted else amount
        
    except Exception as e:
        print(f"Error en convert_currency: {e}")
        return amount


@register.filter
def format_currency(amount, currency='ARS'):
    """
    Formatea un monto con el símbolo de la moneda.
    
    Uso:
    {{ monto|format_currency:"USD" }}  -> $1,234.56
    {{ monto|format_currency:"ARS" }}  -> $1.234,56
    {{ monto|format_currency:"EUR" }}  -> €1,234.56
    """
    if not amount:
        return f"0.00"
    
    try:
        amount = Decimal(str(amount))
        
        # Símbolos de moneda
        symbols = {
            'ARS': '$',
            'USD': 'USD $',
            'EUR': '€'
        }
        
        symbol = symbols.get(currency, '$')
        
        # Formato según moneda
        if currency == 'ARS':
            # Formato argentino: 1.234,56
            formatted = f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        else:
            # Formato internacional: 1,234.56
            formatted = f"{amount:,.2f}"
        
        return f"{symbol}{formatted}"
        
    except Exception as e:
        return str(amount)


@register.simple_tag
def exchange_rate(from_currency, to_currency):
    """
    Obtiene la tasa de cambio actual.
    
    Uso:
    {% exchange_rate "ARS" "USD" as rate %}
    Tasa: {{ rate }}
    """
    rate = CurrencyService.get_exchange_rate(from_currency, to_currency)
    return rate if rate else Decimal('0')