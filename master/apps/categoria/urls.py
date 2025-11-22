
from django.urls import path
from .views import CategoriaListView, CategoriaCreateView

urlpatterns = [
    path('categoria/', CategoriaListView.as_view(), name='categoria'),
    path('categoria/create/', CategoriaCreateView.as_view(), name='categoria_create'),
]
