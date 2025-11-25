"""
Servicio para conversión de monedas usando dolarapi.com
Ubicación: apps/utils/currency_service.py
"""
import requests
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.cache import cache
from typing import Optional, Dict

class CurrencyService:
    """
    Servicio para obtener tasas de cambio y convertir monedas.
    Usa la API de dolarapi.com y caché para optimizar requests.
    """
    
    BASE_URL = "https://dolarapi.com"
    CACHE_TIMEOUT = 3600  # 1 hora en segundos
    
    # Mapeo de monedas a endpoints de la API
    CURRENCY_ENDPOINTS = {
        'USD': '/v1/dolares/oficial',  # Dólar oficial
        'EUR': '/v1/cotizaciones/eur',  # Euro
    }
    
    @classmethod
    def get_exchange_rate(cls, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Obtiene la tasa de cambio entre dos monedas.
        
        Args:
            from_currency: Moneda origen (ARS, USD, EUR)
            to_currency: Moneda destino (ARS, USD, EUR)
            
        Returns:
            Decimal con la tasa de cambio o None si hay error
        """
        # Si son la misma moneda, retornar 1
        if from_currency == to_currency:
            return Decimal('1.0')
        
        # Verificar caché primero
        cache_key = f"exchange_rate_{from_currency}_to_{to_currency}"
        cached_rate = cache.get(cache_key)
        
        if cached_rate:
            return Decimal(str(cached_rate))
        
        try:
            # Obtener tasa de cambio
            rate = cls._fetch_rate(from_currency, to_currency)
            
            if rate:
                # Guardar en caché
                cache.set(cache_key, float(rate), cls.CACHE_TIMEOUT)
                return rate
                
        except Exception as e:
            print(f"Error obteniendo tasa de cambio: {e}")
            return None
    
    @classmethod
    def _fetch_rate(cls, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Obtiene la tasa desde la API.
        Maneja conversiones ARS <-> USD/EUR.
        """
        # Caso 1: De ARS a USD/EUR
        if from_currency == 'ARS' and to_currency in cls.CURRENCY_ENDPOINTS:
            endpoint = cls.CURRENCY_ENDPOINTS[to_currency]
            response = requests.get(f"{cls.BASE_URL}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # Usar promedio de compra y venta
                compra = Decimal(str(data.get('compra', 0)))
                venta = Decimal(str(data.get('venta', 0)))
                
                if compra > 0 and venta > 0:
                    # Tasa para convertir ARS a moneda extranjera
                    return Decimal('1') / ((compra + venta) / Decimal('2'))
        
        # Caso 2: De USD/EUR a ARS
        elif from_currency in cls.CURRENCY_ENDPOINTS and to_currency == 'ARS':
            endpoint = cls.CURRENCY_ENDPOINTS[from_currency]
            response = requests.get(f"{cls.BASE_URL}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                compra = Decimal(str(data.get('compra', 0)))
                venta = Decimal(str(data.get('venta', 0)))
                
                if compra > 0 and venta > 0:
                    # Tasa para convertir moneda extranjera a ARS
                    return (compra + venta) / Decimal('2')
        
        # Caso 3: Entre USD y EUR (conversión indirecta vía ARS)
        elif from_currency in cls.CURRENCY_ENDPOINTS and to_currency in cls.CURRENCY_ENDPOINTS:
            # Primero convertir a ARS
            rate_to_ars = cls._fetch_rate(from_currency, 'ARS')
            # Luego de ARS a la moneda destino
            rate_from_ars = cls._fetch_rate('ARS', to_currency)
            
            if rate_to_ars and rate_from_ars:
                return rate_to_ars * rate_from_ars
        
        return None
    
    @classmethod
    def convert_amount(cls, amount: Decimal, from_currency: str, to_currency: str) -> Optional[Decimal]:
        """
        Convierte un monto de una moneda a otra.
        
        Args:
            amount: Monto a convertir
            from_currency: Moneda origen
            to_currency: Moneda destino
            
        Returns:
            Monto convertido o None si hay error
        """
        if amount == 0:
            return Decimal('0.00')
        
        rate = cls.get_exchange_rate(from_currency, to_currency)
        
        if rate:
            converted = amount * rate
            return converted.quantize(Decimal('0.01'))
        
        return None
    
    @classmethod
    def get_all_rates(cls) -> Dict[str, Decimal]:
        """
        Obtiene todas las tasas disponibles desde ARS.
        Útil para mostrar en el dashboard.
        
        Returns:
            Dict con tasas: {'USD': Decimal('1050.50'), 'EUR': ...}
        """
        rates = {}
        
        for currency in cls.CURRENCY_ENDPOINTS.keys():
            rate = cls.get_exchange_rate('ARS', currency)
            if rate:
                rates[currency] = rate
        
        return rates
    
    @classmethod
    def clear_cache(cls):
        """Limpia el caché de tasas de cambio."""