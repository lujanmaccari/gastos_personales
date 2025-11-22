from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Gasto
from apps.categoria.models import Categoria
from datetime import datetime

# Importar utilidades
from apps.utils.calculations import calcular_variacion_mensual, calcular_distribucion_por_campo, calcular_saldo_mensual, asignar_iconos_y_colores_categorias_gastos
from apps.utils.filters import aplicar_filtros_basicos, aplicar_busqueda, obtener_valores_filtros


class UserGastoQuerysetMixin:
    """Filtra los gastos para que cada usuario solo vea los suyos."""
    def get_queryset(self):
        return Gasto.objects.filter(usuario=self.request.user)


class GastoListView(LoginRequiredMixin, UserGastoQuerysetMixin, ListView):
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
        
        # Calcular variación mensual de gastos
        variacion = calcular_variacion_mensual(Gasto, usuario)
        
        # Calcular distribución por categoría (solo mes actual)
        gastos_por_categoria, total_grafico = calcular_distribucion_por_campo(
            Gasto,
            usuario,
            'categoria__nombre',
            mes_actual=True
        )
        
        # Asignar colores específicos para gastos
        gastos_por_categoria = asignar_iconos_y_colores_categorias_gastos(gastos_por_categoria)
        
        # Procesar cada gasto individual para agregarle iconos y colores
        gastos_lista = list(context['gastos'])  # Convertir QuerySet a lista
        gastos_con_estilos = []
        
        for gasto in gastos_lista:
            # Crear un diccionario temporal con el nombre de la categoría
            if gasto.categoria:
                temp_item = [{'categoria': gasto.categoria.nombre}]
                
                # Asignar iconos y colores
                item_procesado = asignar_iconos_y_colores_categorias_gastos(temp_item)[0]
                
                # Agregar los atributos al objeto gasto
                gasto.icono = item_procesado.get('icono', 'fas fa-circle')
                gasto.color_icono = item_procesado.get('color_icono', 'text-gray-500')
                gasto.color_badge = item_procesado.get('color_badge', 'text-gray-800 bg-gray-100')
            else:
                # Si no tiene categoría, valores por defecto
                gasto.icono = 'fas fa-circle'
                gasto.color_icono = 'text-gray-500'
                gasto.color_badge = 'text-gray-800 bg-gray-100'
            
            gastos_con_estilos.append(gasto)
        
        context['gastos'] = gastos_con_estilos
        
        # Calcular saldo mensual
        saldo_info = calcular_saldo_mensual(usuario)
        
        # Obtener valores de filtros
        valores_filtros = obtener_valores_filtros(
            self.request,
            ['categoria', 'fecha', 'monto_min', 'monto_max']
        )
        
        context.update({
            'total_gastos_mensual': variacion['total_mes_actual'],
            'variacion_porcentual': variacion['variacion_porcentual'],
            'mes_nombre': hoy.strftime('%B'),
            'gastos_por_categoria': gastos_por_categoria,
            'total_general_grafico': total_grafico,
            'categorias_disponibles': Categoria.objects.all(),
            'cantidad_gastos': self.get_queryset().count(),
            'saldo_restante': saldo_info['saldo'],
            'total_ingresos_mensual': saldo_info['total_ingresos'],
            'moneda': usuario.moneda.abreviatura if usuario.moneda else 'ARS',
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