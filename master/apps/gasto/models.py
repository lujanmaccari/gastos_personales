from django.db import models
from apps.categoria.models import Categoria

# Create your models here.
class Gasto(models.Model):
    # Falta agregar campo moneda como FK
    
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.categoria} - ${self.monto} - {self.fecha}"