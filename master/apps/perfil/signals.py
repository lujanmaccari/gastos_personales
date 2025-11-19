from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Perfil

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_auto(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)


# hace que al guardar el usuario, se guarde su perfil asociado