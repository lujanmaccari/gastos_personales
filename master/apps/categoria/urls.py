from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import CategoriaDeleteView, CategoriaListView, CategoriaCreateView, CategoriaUpdateView

urlpatterns = [
    # Listado de categorías
    path('categoria/', login_required(CategoriaListView.as_view()), name='categorias'),
    # Crear nueva categoría
    path('categoria/create/', login_required(CategoriaCreateView.as_view()), name='categoria_create'),
    # Editar categoría
    path('categoria/<int:pk>/edit/', login_required(CategoriaUpdateView.as_view()), name='categoria_update'),
    # Eliminar categoría
    path('categoria/<int:pk>/delete/', login_required(CategoriaDeleteView.as_view()), name='categoria_delete'),
]
