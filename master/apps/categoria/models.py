from django.db import models

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    usuario = models.ForeignKey('usuario.Usuario', on_delete=models.CASCADE , null=True, blank=True)
    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True)
    icono = models.ForeignKey('Icono', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Color(models.Model):
    nombre = models.CharField(max_length=30)
    codigo_hex = models.CharField(max_length=7) 

    def __str__(self):
        return self.nombre

class Icono(models.Model):
    nombre = models.CharField(max_length=50)
    icono = models.CharField(max_length=30)

    def __str__(self):
        return self.icono