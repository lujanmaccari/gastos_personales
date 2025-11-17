from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Gasto

# Create your views here.
class UserGastoQuerysetMixin:
    """Filtra los gastos para que cada usuario solo vea los suyos."""
    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user)

class GastoListView(LoginRequiredMixin, UserGastoQuerysetMixin, ListView):
    """Lista los gastos del usuario logueado, ordenados por fecha."""
    model = Gasto
    template_name = 'gasto/gasto.html'
    context_object_name = 'gastos'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('-fecha') 

class GastoFieldsMixin:
    fields = ['fecha', 'monto', 'descripcion', 'categoria']

class GastoCreateView(LoginRequiredMixin, GastoFieldsMixin, CreateView):
    """Permite crear un nuevo gasto asignado al usuario logueado."""
    model = Gasto
    template_name = 'gasto/gasto_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.moneda = self.request.user.moneda
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('gastos')

class GastoUpdateView(LoginRequiredMixin, UserGastoQuerysetMixin, GastoFieldsMixin, UpdateView):
    """Permite editar un gasto existente del usuario logueado."""
    model = Gasto
    template_name = 'gasto/gasto_form.html'

    def get_success_url(self):
        return reverse_lazy('gastos')

class GastoDeleteView(LoginRequiredMixin, UserGastoQuerysetMixin, DeleteView):
    """Permite eliminar un gasto existente del usuario logueado."""
    model = Gasto
    template_name = 'gasto/gasto_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('gastos')