from django.urls import path
from .views import PerfilDetailView, PerfilUpdateView

app_name = "perfil"

urlpatterns = [
    path("", PerfilDetailView.as_view(), name="perfil_detail"),
    path("editar/", PerfilUpdateView.as_view(), name="perfil_edit"),
]
