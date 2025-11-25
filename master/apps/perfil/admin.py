from django.contrib import admin
from .models import Perfil

# Register your models here.

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "avatar")
    search_fields = ("usuario__username", "usuario__email")
