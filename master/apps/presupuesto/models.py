from django.db import models
from apps.usuario.models import Usuario

# Create your models here.
class Presupuesto(models.Model):
    MESES_CHOICES = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"), (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"), (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    monto_disponible = models.DecimalField(max_digits=10, decimal_places=2)
    mes = models.IntegerField(choices=MESES_CHOICES)
    anio = models.IntegerField()
    
    def __str__(self):
        return f"{self.usuario} - {self.monto_disponible} - {self.mes}/{self.anio}"