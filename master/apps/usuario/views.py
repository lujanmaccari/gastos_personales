from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from .forms import CustomUserCreationForm

User = get_user_model()

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "usuario/register.html"
    success_url = reverse_lazy("login")

    def get_form_class(self):  # el form usa el model Usuario en vez d auth.User
        form_class = super().get_form_class()
        form_class._meta.model = User
        return form_class


def logout_view(request):
    logout(request)                           # cierra la sesión siempre
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("login")                  # redirige al login


