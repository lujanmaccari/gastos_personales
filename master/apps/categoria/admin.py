from django.contrib import admin
from .models import Categoria
from apps.utils.admin_helpers import descripcion_resumida

# Register your models here.
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', descripcion_resumida)
    search_fields = ('nombre',)
    # ¿list_filter por usuario?
    ordering = ('nombre',)