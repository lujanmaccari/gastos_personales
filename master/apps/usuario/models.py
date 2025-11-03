from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    # Si se borra la moneda, no se elimina el usuario
    moneda = models.ForeignKey('usuario.Moneda', on_delete=models.SET_NULL, null=True, blank=True)
    limite_gasto_mensual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    borrado = models.BooleanField(default=False)
    
    def __str__(self):
        nombre = f"{self.first_name} {self.last_name}".strip()
        return nombre if nombre else self.username
    
class Moneda(models.Model):
    moneda = models.CharField(max_length=50)
    abreviatura = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.moneda} ({self.abreviatura})"