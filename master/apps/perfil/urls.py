from django.urls import path
from .views import (
    PerfilDetailView, PerfilUpdateView,
    PerfilDeleteView, MonedaCreateView, 
    MonedaDeleteView, FuenteCreateView,
    FuenteDeleteView,
)

urlpatterns = [
    path("perfil/", PerfilDetailView.as_view(), name="perfil_detail"),
    path("perfil/update/", PerfilUpdateView.as_view(), name="perfil_update"),
    path("perfil/delete/", PerfilDeleteView.as_view(), name="perfil_delete"),

    path("perfil/moneda/create/", MonedaCreateView.as_view(), name="moneda_create"),
    path("perfil/moneda/delete/<int:pk>/", MonedaDeleteView.as_view(), name="moneda_delete"),

    path("perfil/fuente/create/", FuenteCreateView.as_view(), name="fuente_create"),
    path("perfil/fuente/delete/<int:pk>/", FuenteDeleteView.as_view(), name="fuente_delete"),
]
