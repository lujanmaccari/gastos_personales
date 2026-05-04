from django.contrib import admin
from apps.ingreso.models import Fuente, Ingreso
from apps.utils.admin_helpers import descripcion_resumida

# Register your models here.
@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fuente', 'monto', 'fecha', descripcion_resumida)
    list_filter = ('usuario', 'fuente', 'fecha')
    search_fields = ('usuario__username', 'descripcion',)
    ordering = ('-fecha',)
    
@admin.register(Fuente)
class FuenteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)