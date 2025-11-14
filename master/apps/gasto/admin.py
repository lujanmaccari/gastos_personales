from django.contrib import admin
from .models import Gasto
from apps.utils.admin_helpers import descripcion_resumida

# Register your models here.
@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'categoria', 'moneda', 'fecha', 'monto', descripcion_resumida)
    search_fields = ('usuario__username','descripcion',)
    list_filter = ('usuario', 'categoria', 'fecha', 'moneda')
    ordering = ('-fecha',)