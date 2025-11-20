from django.apps import AppConfig

class PerfilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.perfil'
    verbose_name = 'Perfil'

    def ready(self):
    # importa las señales para q se conecten al arrancar
        from . import signals  
