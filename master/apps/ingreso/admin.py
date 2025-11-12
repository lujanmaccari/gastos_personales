from django.contrib import admin
from apps.ingreso.models import Fuente, Ingreso

# Register your models here.
@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fuente', 'monto', 'fecha', 'descripcion')
    list_filter = ('usuario', 'fuente', 'fecha')
    search_fields = ('usuario__username', 'descripcion',)
    
@admin.register(Fuente)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)