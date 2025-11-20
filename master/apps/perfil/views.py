# apps/perfil/views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from .models import Perfil
from .forms import PerfilForm

class PerfilDetailView(LoginRequiredMixin, DetailView):
    model = Perfil
    template_name = "perfil/perfil.html"
    context_object_name = "perfil"

    def get_object(self, queryset=None):
        perfil, created = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil

class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = "perfil/perfil_form.html"
    success_url = reverse_lazy("perfil_detail")

    def get_object(self, queryset=None):
        perfil, created = Perfil.objects.get_or_create(usuario=self.request.user)
        return perfil

    def get_initial(self): # rellena input de form con los valores del user y perfil

        initial = super().get_initial()
        user = self.request.user
        initial.update({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "limite_gasto_mensual": getattr(self.request.user.perfil, "limite_gasto_mensual", 0),
        })
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)  # esto guarda el perfil
        user = self.request.user # actualiza el usuario con los campos del POST
        # ... se toma get para evitar sobrescribir si no vienen
        user.first_name = self.request.POST.get("first_name", user.first_name)
        user.last_name  = self.request.POST.get("last_name", user.last_name)
        user.email      = self.request.POST.get("email", user.email)
        user.save(update_fields=["first_name", "last_name", "email"])

        return response
