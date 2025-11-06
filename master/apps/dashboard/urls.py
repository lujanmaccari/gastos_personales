from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import home

urlpatterns = [
    path('dashboard/', login_required(home), name='dashboard'),
]
