from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, View
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

User = get_user_model()


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "usuario/register.html"
    success_url = reverse_lazy("login")

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class._meta.model = User
        return form_class


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Sesión cerrada correctamente.")
        return redirect("login")

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "Sesión cerrada correctamente.")
        return redirect("login")
