
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Perfil

User = get_user_model()

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(usuario=instance)

# hace que al guardar el usuario, se guarde su perfil asociado





# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# from .models import Perfil

# User = get_user_model()

# @receiver(post_save, sender=User)
# def crear_perfil(sender, instance, created, **kwargs):
#     if created:
#         Perfil.objects.get_or_create(usuario=instance)
