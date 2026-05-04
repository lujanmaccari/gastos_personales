from decimal import Decimal
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Gasto
from apps.categoria.models import Categoria
from datetime import datetime
from .forms import GastoForm
# Importar utilidades
from apps.utils.calculations import calcular_variacion_mensual, calcular_saldo_mensual
from apps.utils.filters import aplicar_filtros_basicos, aplicar_busqueda, obtener_valores_filtros
from apps.utils.currency_mixins import ListViewCurrencyMixin
from apps.utils.categoria.style_helpers import get_badge_styles_from_hex


class UserGastoQuerysetMixin:
    """Filtra los gastos para que cada usuario solo vea los suyos."""
    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user)


class GastoListView(LoginRequiredMixin, UserGastoQuerysetMixin, ListViewCurrencyMixin, ListView):
    """Vista principal de Gastos con:
    - Búsqueda de gastos, 
    - Lista de gastos con filtros,
    - Distribución de gastos por categoría."""
    model = Gasto
    template_name = 'gasto/gasto.html'
    context_object_name = 'gastos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'categoria', 'moneda', 'usuario', 
            'categoria__color', 'categoria__icono'
        )
        
        # Aplicar búsqueda
        queryset = aplicar_busqueda(
            queryset, 
            self.request, 
            ['descripcion', 'categoria__nombre']
        )
        
        # Aplicar filtros básicos (fecha, monto)
        queryset = aplicar_filtros_basicos(queryset, self.request)
        
        # Filtro específico de Gasto: categoría
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        return queryset.order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        hoy = datetime.now()
        user_currency = self.get_user_currency()
        
        # Consulta para gastos del mes
        gastos_mes = Gasto.objects.filter(
            usuario=usuario,
            fecha__month=hoy.month,
            fecha__year=hoy.year
        ).select_related('moneda', 'categoria', 'categoria__color', 'categoria__icono')
        
        # Calcular distribución por categoría
        gastos_por_categoria_dict = self._calcular_distribucion_categorias(
            gastos_mes, user_currency
        )
        
        total_gastos_convertido = gastos_por_categoria_dict['total']
        gastos_por_categoria_list = gastos_por_categoria_dict['items']
        
        # Asignar estilos a gastos individuales
        self._asignar_estilos_gastos(context['gastos'])
        
        # Calcular variación y saldo
        variacion = calcular_variacion_mensual(Gasto, usuario)
        saldo_info = calcular_saldo_mensual(usuario)
        
        # Obtener valores de filtros
        valores_filtros = obtener_valores_filtros(
            self.request,
            ['categoria', 'fecha', 'monto_min', 'monto_max']
        )
        
        context.update({
            'total_gastos_mensual': total_gastos_convertido,
            'variacion_porcentual': variacion['variacion_porcentual'],
            'mes_nombre': hoy.strftime('%B'),
            'gastos_por_categoria': gastos_por_categoria_list,
            'total_general_grafico': total_gastos_convertido,
            'categorias_disponibles': Categoria.objects.all(),
            'cantidad_gastos': self.get_queryset().count(),
            'saldo_restante': saldo_info['saldo'],
            'total_ingresos_mensual': saldo_info['total_ingresos'],
            'moneda': user_currency,
            **valores_filtros
        })
        
        return context
    
    def _calcular_distribucion_categorias(self, gastos_mes, user_currency):
        """
        Calcula la distribución de gastos por categoría con colores e íconos de la BD.
        """
        total_convertido = Decimal('0.00')
        gastos_por_categoria = {}
        
        for gasto in gastos_mes:
            # Conversión de moneda
            gasto_currency = gasto.moneda.abreviatura if gasto.moneda else 'ARS'
            monto_convertido = (
                gasto.monto 
                if gasto_currency == user_currency 
                else self.convert_to_user_currency(gasto.monto, gasto_currency)
            )
            
            total_convertido += monto_convertido
            
            # Acumular por categoría
            categoria_nombre = gasto.categoria.nombre if gasto.categoria else 'Sin categoría'
            if categoria_nombre not in gastos_por_categoria:
                gastos_por_categoria[categoria_nombre] = {
                    'monto': Decimal('0.00'),
                    'color': gasto.categoria.color.codigo_hex if gasto.categoria and gasto.categoria.color else '#9CA3AF',
                    'icono': gasto.categoria.icono.icono if gasto.categoria and gasto.categoria.icono else 'fas fa-circle',
                }
            gastos_por_categoria[categoria_nombre]['monto'] += monto_convertido
        
        # Crear lista con porcentajes
        items = [
            {
                'categoria': categoria,
                'total': data['monto'],
                'porcentaje': round((data['monto'] / total_convertido * 100), 2) if total_convertido > 0 else 0,
                'color': data['color'],
                'icono': data['icono'],
            }
            for categoria, data in gastos_por_categoria.items()
        ]
        
        items.sort(key=lambda x: x['porcentaje'], reverse=True)
        
        return {
            'total': total_convertido,
            'items': items
        }
    
    def _asignar_estilos_gastos(self, gastos_queryset):
        """
        Asigna estilos inline a cada gasto basándose en su categoría.
        """
        # Obtener categorías únicas
        categorias_ids = {gasto.categoria.id for gasto in gastos_queryset if gasto.categoria}
        
        # Cargar estilos de categorías desde la BD
        estilos_categorias = {}
        if categorias_ids:
            categorias = Categoria.objects.filter(
                id__in=categorias_ids
            ).select_related('color', 'icono')
            
            for cat in categorias:
                color_hex = cat.color.codigo_hex if cat.color else '#9CA3AF'
                icono_class = cat.icono.icono if cat.icono else 'fas fa-circle'
                
                estilos_categorias[cat.nombre] = {
                    'icono': icono_class,
                    'color_icono': f"color: {color_hex};",
                    'color_badge': get_badge_styles_from_hex(color_hex)
                }
        
        # Estilos por defecto
        estilos_default = {
            'icono': 'fas fa-circle',
            'color_icono': 'color: #9CA3AF;',
            'color_badge': 'background-color: rgba(156,163,175,0.15); color: rgb(75,85,99);'
        }
        
        # Asignar estilos a cada gasto
        for gasto in gastos_queryset:
            if gasto.categoria and gasto.categoria.nombre in estilos_categorias:
                estilos = estilos_categorias[gasto.categoria.nombre]
            else:
                estilos = estilos_default
            
            gasto.icono = estilos['icono']
            gasto.color_icono = estilos['color_icono']
            gasto.color_badge = estilos['color_badge']


class GastoFieldsMixin:
    fields = ['fecha', 'categoria', 'monto', 'descripcion']


class GastoCreateView(LoginRequiredMixin, CreateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'gasto/gasto_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.moneda = self.request.user.moneda
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('gastos')


class GastoUpdateView(LoginRequiredMixin, UserGastoQuerysetMixin, UpdateView):
    model = Gasto
    form_class = GastoForm
    template_name = 'gasto/gasto_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('gastos')

class GastoDeleteView(LoginRequiredMixin, UserGastoQuerysetMixin, DeleteView):
    model = Gasto
    template_name = 'gasto/gasto_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('gastos')