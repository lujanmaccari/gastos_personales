from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.usuario.models import Usuario, Moneda

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email")}),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser",
                       "groups", "user_permissions")
        }),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    ordering = ("username",)

@admin.register(Moneda)
class MonedaAdmin(admin.ModelAdmin):
    list_display = ('moneda', 'abreviatura')
