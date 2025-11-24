from django.core.management.base import BaseCommand
from apps.utils.currency_service import CurrencyService
from decimal import Decimal


class Command(BaseCommand):
    help = 'Actualiza las tasas de cambio manualmente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Limpia el caché antes de actualizar',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            from django.core.cache import cache
            cache.clear()
            self.stdout.write(
                self.style.WARNING('○ Caché limpiado')
            )
        
        self.stdout.write('Actualizando tasas de cambio...\n')
        
        # Obtener todas las tasas
        try:
            rates = CurrencyService.get_all_rates()
            
            if rates:
                self.stdout.write(
                    self.style.SUCCESS('✓ Tasas actualizadas:')
                )
                
                for currency, rate in rates.items():
                    self.stdout.write(f'  • 1 ARS = {rate:.6f} {currency}')
                
                # Calcular inversa
                self.stdout.write('\n' + self.style.SUCCESS('Conversión inversa:'))
                for currency, rate in rates.items():
                    inverse = Decimal('1') / rate
                    self.stdout.write(f'  • 1 {currency} = {inverse:.2f} ARS')
            else:
                self.stdout.write(
                    self.style.ERROR('✗ No se pudieron obtener las tasas')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error: {str(e)}')
            )
