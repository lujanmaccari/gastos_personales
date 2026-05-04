from django.core.management.base import BaseCommand
from apps.gasto.models import Gasto
from apps.ingreso.models import Ingreso
from apps.usuario.models import Moneda


class Command(BaseCommand):
    help = '''Asigna moneda a gastos e ingresos que no la tienen.
    Usa la moneda del usuario o ARS por defecto.'''

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se haría sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('○ Modo DRY RUN - No se harán cambios\n')
            )
        
        # Obtener moneda ARS por defecto
        try:
            moneda_default = Moneda.objects.get(abreviatura='ARS')
        except Moneda.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('✗ Error: Moneda ARS no existe. Ejecuta crear_monedas primero.')
            )
            return
        
        # Procesar Gastos
        gastos_sin_moneda = Gasto.objects.filter(moneda__isnull=True)
        gastos_count = gastos_sin_moneda.count()
        
        self.stdout.write(f'Gastos sin moneda: {gastos_count}')
        
        if gastos_count > 0 and not dry_run:
            for gasto in gastos_sin_moneda:
                # Intentar usar la moneda del usuario
                moneda = gasto.usuario.moneda or moneda_default
                gasto.moneda = moneda
                gasto.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ {gastos_count} gastos actualizados')
            )
        
        # Procesar Ingresos
        ingresos_sin_moneda = Ingreso.objects.filter(moneda__isnull=True)
        ingresos_count = ingresos_sin_moneda.count()
        
        self.stdout.write(f'Ingresos sin moneda: {ingresos_count}')
        
        if ingresos_count > 0 and not dry_run:
            for ingreso in ingresos_sin_moneda:
                moneda = ingreso.usuario.moneda or moneda_default
                ingreso.moneda = moneda
                ingreso.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ {ingresos_count} ingresos actualizados')
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '\n○ Ejecuta sin --dry-run para aplicar los cambios'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Proceso completado: {gastos_count + ingresos_count} registros actualizados'
                )
            )