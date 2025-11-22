from django.contrib import admin
from .models import Categoria, Color, Icono
from apps.utils.admin_helpers import descripcion_resumida

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', descripcion_resumida, 'color', 'icono', 'usuario',)
    search_fields = ('nombre',)
    # ¿list_filter por usuario?
    ordering = ('nombre',)
    list_filter = ('usuario', 'nombre')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_hex',)
    search_fields = ('nombre',)
    ordering = ('nombre',)

@admin.register(Icono)
class IconoAdmin(admin.ModelAdmin):
    list_display = ('icono',)
    search_fields = ('icono',)
    ordering = ('icono',)