
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import categoria

urlpatterns = [
    path('categoria/', login_required(categoria), name='categoria'),
]
