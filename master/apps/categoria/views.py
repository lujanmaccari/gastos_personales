from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, CreateView
from .models import Categoria, Color, Icono
from django.urls import reverse_lazy
from apps.utils.calculations import procesar_categorias, asignar_iconos_y_colores_categorias_gastos
from django.db.models import Sum


class UserCategoriaQuerysetMixin:
    """Filtra las categorías para que cada usuario solo vea las suyas."""
    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)


class CategoriaListView(LoginRequiredMixin, UserCategoriaQuerysetMixin, TemplateView):
    model = Categoria
    template_name = 'categoria/categoria.html'
    context_object_name = 'categoria'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categorias = self.get_queryset()
        context["categorias"] = procesar_categorias(categorias)

        top_categorias = (
            self.get_queryset()
            .filter(gasto__usuario=self.request.user)
            .annotate(total=Sum('gasto__monto'))
            .order_by('-total')[:3]
            .select_related('color', 'icono')
        )

        context["top_categorias"] = procesar_categorias(top_categorias)

        return context

      

class CategoriaFieldsMixin:
    fields = ['nombre','descripcion', 'color', 'icono']


class CategoriaCreateView(LoginRequiredMixin, CategoriaFieldsMixin, CreateView):
    model = Categoria
    template_name = 'categoria/categoria_form.html'
    fields = ['nombre', 'color', 'icono']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # traer listados generales desde BD
        iconos_qs = Icono.objects.all()
        colores_qs = Color.objects.all()

        # convertir a formato esperado por la función
        iconos_list = [{"nombre": i.icono} for i in iconos_qs]
        iconos_validos = asignar_iconos_y_colores_categorias_gastos(iconos_list)

        context['iconos'] = iconos_validos
        context['colores'] = colores_qs

        return context

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('categoria')
