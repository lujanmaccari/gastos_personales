from django.urls import path
from django.contrib.auth.views import LoginView
from .views import RegisterView, LogoutView 

urlpatterns = [
    path("login/", LoginView.as_view(template_name="usuario/login.html"), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),  
]