from django.core.management.base import BaseCommand
from apps.utils.currency_service import CurrencyService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Prueba el sistema de conversión de monedas'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS('=== TEST DE CONVERSIÓN DE MONEDAS ===\n')
        )
        
        # Test 1: Obtener tasas
        self.stdout.write('Test 1: Obtener tasas de cambio')
        self.stdout.write('-' * 40)
        
        conversions = [
            ('ARS', 'USD'),
            ('ARS', 'EUR'),
            ('USD', 'ARS'),
            ('EUR', 'ARS'),
            ('USD', 'EUR'),
        ]
        
        for from_curr, to_curr in conversions:
            rate = CurrencyService.get_exchange_rate(from_curr, to_curr)
            if rate:
                self.stdout.write(
                    f'  ✓ 1 {from_curr} = {rate:.6f} {to_curr}'
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error obteniendo tasa {from_curr} -> {to_curr}'
                    )
                )
        
        # Test 2: Convertir montos
        self.stdout.write('\n\nTest 2: Convertir montos')
        self.stdout.write('-' * 40)
        
        test_amounts = [
            (Decimal('1000'), 'ARS', 'USD'),
            (Decimal('100'), 'USD', 'ARS'),
            (Decimal('50'), 'EUR', 'ARS'),
            (Decimal('1000'), 'ARS', 'EUR'),
        ]
        
        for amount, from_curr, to_curr in test_amounts:
            converted = CurrencyService.convert_amount(
                amount, from_curr, to_curr
            )
            if converted:
                self.stdout.write(
                    f'  ✓ {amount} {from_curr} = {converted:.2f} {to_curr}'
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error convirtiendo {amount} {from_curr} -> {to_curr}'
                    )
                )
        
        # Test 3: Verificar caché
        self.stdout.write('\n\nTest 3: Verificar caché')
        self.stdout.write('-' * 40)
        
        from django.core.cache import cache
        import time
        
        # Primera llamada
        start = time.time()
        rate1 = CurrencyService.get_exchange_rate('ARS', 'USD')
        time1 = (time.time() - start) * 1000
        
        # Segunda llamada (debería usar caché)
        start = time.time()
        rate2 = CurrencyService.get_exchange_rate('ARS', 'USD')
        time2 = (time.time() - start) * 1000
        
        self.stdout.write(f'  • Primera llamada: {time1:.2f}ms')
        self.stdout.write(f'  • Segunda llamada (caché): {time2:.2f}ms')
        
        if time2 < time1:
            self.stdout.write(
                self.style.SUCCESS('  ✓ Caché funcionando correctamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('  ⚠ Caché puede no estar funcionando')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n\n=== TESTS COMPLETADOS ===')
        )
