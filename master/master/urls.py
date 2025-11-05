"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView # usuario
from apps.usuario.views import RegisterView, HomeView, logout_view # usuario

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("", include("apps.categoria.urls")),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.gasto.urls")),
    path("", include("apps.ingreso.urls")),
    path("", include("apps.perfil.urls")),
    path("", include("apps.simulador.urls")),
    path("", include("apps.usuario.urls")),



]
