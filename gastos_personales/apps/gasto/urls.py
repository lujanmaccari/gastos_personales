from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import GastoListView, GastoCreateView, GastoUpdateView, GastoDeleteView

urlpatterns = [
    # Listado de gastos
    path('gastos/', login_required(GastoListView.as_view()), name='gastos'),
    # Crear nuevo gasto
    path('gastos/nuevo/', login_required(GastoCreateView.as_view()), name='gastos_create'),
    # Editar gasto
    path('gastos/<int:pk>/editar/', login_required(GastoUpdateView.as_view()), name='gastos_update'),
    # Eliminar gasto
    path('gastos/<int:pk>/eliminar/', login_required(GastoDeleteView.as_view()), name='gastos_delete'),
]
