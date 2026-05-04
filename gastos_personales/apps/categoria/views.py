from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Categoria, Color, Icono
from .forms import CategoriaForm
from apps.utils.categoria.sincronizar_color_icono import initialize_default_colors_and_icons
from django.urls import reverse_lazy
from apps.utils.calculations import (
    procesar_categorias,
)
from django.db.models import Sum
from apps.utils.currency_mixins import ListViewCurrencyMixin


class UserCategoriaQuerysetMixin:
    """Filtra las categorías para que cada usuario solo vea las suyas."""
    
    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)


from decimal import Decimal

class CategoriaListView(LoginRequiredMixin, UserCategoriaQuerysetMixin, ListView, ListViewCurrencyMixin):
    model = Categoria
    template_name = 'categoria/categoria.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return super().get_queryset().select_related('icono', 'color')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categorias = self.get_queryset()
        user_currency = self.get_user_currency()

        context["categorias"] = procesar_categorias(categorias)

        top_categorias_qs = (
            categorias
            .annotate(total=Sum('gasto__monto'))
            .order_by("-total")[:3]
            .select_related("color", "icono")
        )

        for cat in top_categorias_qs:
            gastos = cat.gasto_set.all().select_related('moneda')
            total_convertido = Decimal('0.00')
            for gasto in gastos:
                from_currency = gasto.moneda.abreviatura if gasto.moneda else 'ARS'

                monto_convertido = (
                    gasto.monto if from_currency == user_currency else self.convert_to_user_currency(gasto.monto, from_currency)
                )

                total_convertido += monto_convertido
                print(total_convertido, flush=True)
            cat.total = total_convertido

        context["top_categorias"] = top_categorias_qs
        context["user_currency"] = user_currency

        return context


class CategoriaFieldsMixin:
    fields = ['nombre', 'icono', 'color']


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    """Permite crear una nueva categoría asignada al usuario logueado."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Inicializar colores e íconos si no existen
        initialize_default_colors_and_icons()
        
        # Traer listados generales desde BD
        iconos_qs = Icono.objects.all()
        colores_qs = Color.objects.all()
        
        context['iconos'] = iconos_qs
        context['colores'] = colores_qs
        
        return context

    def form_valid(self, form):
        # Asignar el usuario autenticado
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('categorias')


class CategoriaUpdateView(LoginRequiredMixin, UserCategoriaQuerysetMixin, UpdateView):
    """Permite editar una categoría existente del usuario logueado."""
    model = Categoria
    form_class = CategoriaForm 
    template_name = 'categoria/categoria_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Asegurar que existan los datos básicos
        initialize_default_colors_and_icons()
        
        iconos_qs = Icono.objects.all()
        colores_qs = Color.objects.all()
        
        context["iconos"] = iconos_qs
        context["colores"] = colores_qs
        
        return context

    def get_success_url(self):
        return reverse_lazy('categorias')


class CategoriaDeleteView(LoginRequiredMixin, UserCategoriaQuerysetMixin, DeleteView):
    """Permite eliminar una categoría existente del usuario logueado."""
    model = Categoria
    template_name = 'categoria/categoria_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('categorias')