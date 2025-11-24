from decimal import Decimal
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Gasto
from apps.categoria.models import Categoria
from datetime import datetime

# Importar utilidades
from apps.utils.calculations import calcular_variacion_mensual, calcular_distribucion_por_campo, calcular_saldo_mensual, asignar_iconos_y_colores_categorias_gastos
from apps.utils.filters import aplicar_filtros_basicos, aplicar_busqueda, obtener_valores_filtros
from apps.utils.currency_mixins import ListViewCurrencyMixin


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
        queryset = super().get_queryset().select_related('categoria', 'moneda', 'usuario')
        
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
        ).select_related('moneda', 'categoria')
        
        # Calcular total y distribución
        total_gastos_convertido = Decimal('0.00')
        gastos_por_categoria = {}
        
        for gasto in gastos_mes:
            # Conversión de moneda
            gasto_currency = gasto.moneda.abreviatura if gasto.moneda else 'ARS'
            monto_convertido = (
                gasto.monto 
                if gasto_currency == user_currency 
                else self.convert_to_user_currency(gasto.monto, gasto_currency)
            )
            
            total_gastos_convertido += monto_convertido
            
            # Acumular por categoría simultáneamente
            categoria_nombre = gasto.categoria.nombre if gasto.categoria else 'Sin categoría'
            if categoria_nombre not in gastos_por_categoria:
                gastos_por_categoria[categoria_nombre] = Decimal('0.00')
            gastos_por_categoria[categoria_nombre] += monto_convertido
        
        # Calcular porcentajes para el gráfico
        gastos_por_categoria_list = [
            {
                'categoria': categoria,
                'total': monto,
                'porcentaje': round((monto / total_gastos_convertido * 100), 2) if total_gastos_convertido > 0 else 0
            }
            for categoria, monto in gastos_por_categoria.items()
        ]
        
        gastos_por_categoria_list.sort(key=lambda x: x['porcentaje'], reverse=True)
        
        # Asignar iconos y colores al gráfico
        gastos_por_categoria_list = asignar_iconos_y_colores_categorias_gastos(gastos_por_categoria_list)
        
        # Pre-calcular estilos de categorías
        # Crear un diccionario de estilos por categoría
        categorias_unicas = set()
        for gasto in context['gastos']:
            if gasto.categoria:
                categorias_unicas.add(gasto.categoria.nombre)
        
        # Procesar todas las categorías
        estilos_categorias = {}
        if categorias_unicas:
            temp_items = [{'categoria': cat} for cat in categorias_unicas]
            items_procesados = asignar_iconos_y_colores_categorias_gastos(temp_items)
            
            for item in items_procesados:
                estilos_categorias[item['categoria']] = {
                    'icono': item.get('icono', 'fas fa-circle'),
                    'color_icono': item.get('color_icono', 'text-gray-500'),
                    'color_badge': item.get('color_badge', 'text-gray-800 bg-gray-100')
                }
        
        # Estilos por defecto
        estilos_default = {
            'icono': 'fas fa-circle',
            'color_icono': 'text-gray-500',
            'color_badge': 'text-gray-800 bg-gray-100'
        }
        
        # Asignar estilos
        for gasto in context['gastos']:
            if gasto.categoria and gasto.categoria.nombre in estilos_categorias:
                estilos = estilos_categorias[gasto.categoria.nombre]
            else:
                estilos = estilos_default
            
            gasto.icono = estilos['icono']
            gasto.color_icono = estilos['color_icono']
            gasto.color_badge = estilos['color_badge']
        
        # Calcular variación
        variacion = calcular_variacion_mensual(Gasto, usuario)
        
        # Calcular saldo mensual
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


class GastoFieldsMixin:
    fields = ['fecha', 'categoria', 'monto', 'descripcion']


class GastoCreateView(LoginRequiredMixin, GastoFieldsMixin, CreateView):
    model = Gasto
    template_name = 'gasto/gasto_form.html'

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.moneda = self.request.user.moneda
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('gastos')


class GastoUpdateView(LoginRequiredMixin, UserGastoQuerysetMixin, GastoFieldsMixin, UpdateView):
    model = Gasto
    template_name = 'gasto/gasto_form.html'

    def get_success_url(self):
        return reverse_lazy('gastos')


class GastoDeleteView(LoginRequiredMixin, UserGastoQuerysetMixin, DeleteView):
    model = Gasto
    template_name = 'gasto/gasto_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('gastos')