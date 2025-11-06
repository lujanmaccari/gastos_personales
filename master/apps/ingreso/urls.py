from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import ingresos

urlpatterns = [
    path('ingresos/', login_required(ingresos), name='ingresos'),
]
