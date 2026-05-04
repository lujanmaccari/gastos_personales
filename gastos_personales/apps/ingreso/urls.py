from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import IngresoListView, IngresoCreateView, IngresoUpdateView, IngresoDeleteView

urlpatterns = [
    # Listado de ingresos
    path('ingresos/', login_required(IngresoListView.as_view()), name='ingresos'),
    # Crear nuevo ingreso
    path('ingresos/nuevo/', login_required(IngresoCreateView.as_view()), name='ingresos_create'),
    # Editar ingreso
    path('ingresos/<int:pk>/editar/', login_required(IngresoUpdateView.as_view()), name='ingresos_update'),
    # Eliminar ingreso
    path('ingresos/<int:pk>/eliminar/', login_required(IngresoDeleteView.as_view()), name='ingresos_delete'),
]