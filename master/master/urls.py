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
from django.contrib.auth.views import LoginView
from apps.usuario.views import RegisterView, logout_view
from apps.perfil.views import PerfilDetailView, PerfilUpdateView
from django.conf.urls.static import static
from django.conf import settings
from apps.gasto.views import GastoListView, GastoCreateView
from apps.ingreso.views import IngresoListView, IngresoCreateView
from api.api import api
from apps.dashboard.views import DashboardView 

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("", include("apps.categoria.urls")),
    path("", include("apps.dashboard.urls")),
    path("", include("apps.gasto.urls")),
    path("", include("apps.ingreso.urls")),
    path("perfil/", PerfilDetailView.as_view(), name="perfil_detail"),
    path("perfil/editar/", PerfilUpdateView.as_view(), name="perfil_edit"),
    path("", include("apps.simulador.urls")),
    path("", include("apps.usuario.urls")),
    
    path("login/", LoginView.as_view(template_name="usuario/login.html"), name="login"),
    path("logout/", logout_view, name="logout"), 
    path("register/", RegisterView.as_view(), name="register"),
    
    path('gastos/', GastoListView.as_view(), name='gastos'),
    path('gastos/nuevo/', GastoCreateView.as_view(), name='gastos_create'),
    path('ingresos/', IngresoListView.as_view(), name='ingresos'),
    path('ingresos/nuevo/', IngresoCreateView.as_view(), name='ingresos_create'),
    
    # API
    path('api/', api.urls)
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# las subidas de avatar redirigen a media/avatars/lalala.jpg y django las busca en MEDIA_ROOT = base_dir/media