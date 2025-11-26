from django.db import models
from django.conf import settings


class Perfil(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
   

    def __str__(self):
        return f"Perfil de {self.usuario.username}"



# moneda en cualquier template -> {{ request.user.moneda.abreviatura }}
# en cualquier vista -> moneda_usuario = request.user.moneda