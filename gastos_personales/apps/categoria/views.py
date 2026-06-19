from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.shortcuts import redirect
from decimal import Decimal
from django.db.models import Q
from .models import Categoria
from .forms import CategoriaForm
from django.urls import reverse_lazy
from django.db.models import Sum
from apps.utils.calculations import procesar_categorias
from apps.utils.currency_mixins import CurrencyConversionMixin


class UserCategoriaQuerysetMixin:
    """Filtra las categorías para que cada usuario solo vea las suyas."""

    def get_queryset(self):
        return Categoria.objects.filter(usuario=self.request.user)


class CategoriaListView(LoginRequiredMixin, UserCategoriaQuerysetMixin, CurrencyConversionMixin, ListView):
    model = Categoria
    template_name = 'categoria/categoria.html'
    context_object_name = 'categorias'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related('icono', 'color')
        search = self.request.GET.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(nombre__icontains=search) | Q(descripcion__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_currency = self.get_user_currency()
        context['search_query'] = self.request.GET.get('search', '')
        context['user_currency'] = user_currency

        # Procesar solo la página actual (ya paginada por ListView)
        context["categorias"] = procesar_categorias(list(context["categorias"]))

        # Top categorías usa el queryset completo filtrado (no paginado)
        full_qs = self.get_queryset()
        top_categorias_qs = (
            full_qs
            .annotate(total=Sum('gasto__monto'))
            .order_by("-total")[:3]
            .select_related("color", "icono")
        )

        top_categorias_procesadas = []
        for cat in top_categorias_qs:
            gastos = cat.gasto_set.all().select_related('moneda')
            total_convertido = Decimal('0.00')
            for gasto in gastos:
                from_currency = gasto.moneda.abreviatura if gasto.moneda else 'ARS'
                monto_convertido = (
                    gasto.monto if from_currency == user_currency
                    else self.convert_to_user_currency(gasto.monto, from_currency)
                )
                total_convertido += monto_convertido

            color_hex = cat.color.codigo_hex if cat.color else '#9CA3AF'
            top_categorias_procesadas.append({
                'nombre': cat.nombre,
                'total': total_convertido,
                'icono': cat.icono.icono if cat.icono else 'fas fa-circle',
                'color_icono': f"color: {color_hex};",
                'color_hex': color_hex,
            })

        context["top_categorias"] = top_categorias_procesadas

        return context


class CategoriaFieldsMixin:
    fields = ['nombre', 'icono', 'color']


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    """Permite crear una nueva categoría asignada al usuario logueado."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'

    def _nombre_normalizado(self, nombre):
        """Trim + colapsar espacios + lowercase para comparación."""
        return ' '.join(nombre.lower().split())

    def form_valid(self, form):
        nombre = form.cleaned_data.get('nombre', '')
        nombre_norm = self._nombre_normalizado(nombre)

        # Bloqueo duro: no permitir categorías con el mismo nombre (case-insensitive)
        ya_existe = any(
            self._nombre_normalizado(cat.nombre) == nombre_norm
            for cat in Categoria.objects.filter(usuario=self.request.user)
        )
        if ya_existe:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(
                    {'status': 'error', 'errors': {'nombre': ['Ya existe una categoría con ese nombre.']}},
                    status=400
                )
            form.add_error('nombre', 'Ya existe una categoría con ese nombre.')
            return self.form_invalid(form)

        form.instance.usuario = self.request.user
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('categorias')


class CategoriaUpdateView(LoginRequiredMixin, UserCategoriaQuerysetMixin, UpdateView):
    """Permite editar una categoría existente del usuario logueado."""
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('categorias')


class CategoriaDeleteView(LoginRequiredMixin, UserCategoriaQuerysetMixin, DeleteView):
    """Permite eliminar una categoría existente del usuario logueado."""
    model = Categoria

    def get(self, request, *args, **kwargs):
        return redirect('categorias')

    def get_success_url(self):
        return reverse_lazy('categorias')
