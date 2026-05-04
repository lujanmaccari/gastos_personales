from django.core.management.base import BaseCommand
from apps.usuario.models import Moneda

class Command(BaseCommand):
    help = 'Crea las monedas iniciales en la base de datos'

    def handle(self, *args, **kwargs):
        monedas = [
            {'moneda': 'Peso Argentino', 'abreviatura': 'ARS'},
            {'moneda': 'Dólar Estadounidense', 'abreviatura': 'USD'},
            {'moneda': 'Euro', 'abreviatura': 'EUR'},
        ]
        
        created_count = 0
        
        for m in monedas:
            moneda, created = Moneda.objects.get_or_create(
                abreviatura=m['abreviatura'],
                defaults={'moneda': m['moneda']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Moneda {m["abreviatura"]} ({m["moneda"]}) creada'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'○ Moneda {m["abreviatura"]} ya existe'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {created_count} monedas nuevas creadas'
            )
        )
