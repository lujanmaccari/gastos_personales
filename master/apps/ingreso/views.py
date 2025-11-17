from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Ingreso

class UserIngresoQuerysetMixin:
    """Filtra los ingresos para que cada usuario solo vea los suyos."""
    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user)

class IngresoListView(LoginRequiredMixin, UserIngresoQuerysetMixin, ListView):
    """Lista los ingresos del usuario logueado, ordenados por fecha."""
    model = Ingreso
    template_name = 'ingreso/ingreso.html'
    context_object_name = 'ingresos'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-fecha') 

class IngresoFieldsMixin:
    fields = ['fecha', 'fuente', 'monto', 'descripcion']

class IngresoCreateView(LoginRequiredMixin, IngresoFieldsMixin, CreateView):
    """Permite crear un nuevo ingreso asignado al usuario logueado."""
    model = Ingreso
    template_name = 'ingreso/ingreso_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.moneda = self.request.user.moneda
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('ingresos')

class IngresoUpdateView(LoginRequiredMixin, UserIngresoQuerysetMixin, IngresoFieldsMixin, UpdateView):
    """Permite editar un ingreso existente del usuario logueado."""
    model = Ingreso
    template_name = 'ingreso/ingreso_form.html'

    def get_success_url(self):
        return reverse_lazy('ingresos')

class IngresoDeleteView(LoginRequiredMixin, UserIngresoQuerysetMixin, DeleteView):
    """Permite eliminar un ingreso existente del usuario logueado."""
    model = Ingreso
    template_name = 'ingreso/ingreso_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('ingresos')