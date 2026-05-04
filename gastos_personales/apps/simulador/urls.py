from django.urls import path
from .views import SimuladorView, SimuladorCalculoView

urlpatterns = [
    path("simulador/", SimuladorView.as_view(), name="simulador"),
    path("calcular/", SimuladorCalculoView.as_view(), name="simulador-calcular"),
]
