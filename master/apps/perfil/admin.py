from django.contrib import admin
from .models import Perfil

# Register your models here.

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "moneda", "limite_gasto_mensual")
    search_fields = ("usuario__username", "usuario__email")
    list_filter = ("moneda",)
