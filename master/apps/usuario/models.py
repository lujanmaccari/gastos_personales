from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class Usuario(AbstractUser):
    email = models.EmailField(unique=True) 
    moneda = models.ForeignKey('usuario.Moneda', on_delete=models.SET_NULL, null=True, blank=True, related_name="usuarios_usan_moneda")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True) 


    def __str__(self):
        nombre = f"{self.first_name} {self.last_name}".strip()
        return nombre if nombre else self.username


class Moneda(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monedas"
    )
    moneda = models.CharField(max_length=50)
    abreviatura = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.moneda} ({self.abreviatura})"