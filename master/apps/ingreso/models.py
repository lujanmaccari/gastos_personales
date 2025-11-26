from django.db import models
from django.conf import settings
from apps.usuario.models import Usuario

# Create your models here.
class Ingreso(models.Model):
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE)
    fuente = models.ForeignKey('ingreso.Fuente', on_delete=models.SET_NULL, null=True)
    moneda = models.ForeignKey('usuario.Moneda', on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    def _str_(self):
        return f"{self.fuente} - {self.monto} - {self.fecha}"

class Fuente(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fuentes"
    )
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre