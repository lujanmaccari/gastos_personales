
from django.urls import path
from .views import CategoriaView, CategoriaCreateView

urlpatterns = [
    path('categoria/', CategoriaView.as_view(), name='categoria'),
    path('categoria/create/', CategoriaCreateView.as_view(), name='categoria_create'),
]
