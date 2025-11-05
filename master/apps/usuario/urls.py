from django.urls import path
from django.contrib.auth.views import LoginView 
from apps.usuario.views import RegisterView, logout_view 

urlpatterns = [
    path("login/",  LoginView.as_view(template_name="usuario/login.html"), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout_view/", logout_view, name="logout_view"), 
]
