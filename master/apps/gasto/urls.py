from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import gastos

urlpatterns = [
    path('gastos/', login_required(gastos), name='gastos'),
]
