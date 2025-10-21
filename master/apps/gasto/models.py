from django.db import models
from apps.categoria.models import Categoria
from apps.presupuesto.models import Presupuesto

# Create your models here.
class Item(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
    
class Gasto(models.Model):
    TIPO_CHOICES = [
        ('fijo', 'Fijo'),
        ('variable', 'Variable'),
    ]

    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.categoria} - ${self.monto} - {self.fecha}"