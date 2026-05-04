from django.db import models

# Create your models here.
class Gasto(models.Model):
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE)
    categoria = models.ForeignKey('categoria.Categoria', on_delete=models.CASCADE)
    moneda = models.ForeignKey('usuario.Moneda', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.categoria} - ${self.monto} - {self.fecha}"