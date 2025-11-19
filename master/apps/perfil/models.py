from django.conf import settings
from django.db import models

# Create your models here.

class Perfil(models.Model):
    MONEDAS = [
        ("ARS", "ARS $"),
        ("USD", "USD $"),
        ("EUR", "EUR €"),
    ]

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil"
    )
    moneda = models.CharField(max_length=3, choices=MONEDAS, default="ARS")
    limite_gasto_mensual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"
