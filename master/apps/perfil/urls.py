from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import perfil

urlpatterns = [    
    path('perfil/', login_required(perfil), name='perfil'),
]
