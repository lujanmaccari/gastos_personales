from django.db import models

# Create your models here.
class Ingreso(models.Model):
    # Falta agregar campo moneda como FK
    
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE)
    fuente = models.ForeignKey('ingreso.Fuente', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.fuente} - {self.monto} - {self.fecha}"

class Fuente(models.Model):
    nombre = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre