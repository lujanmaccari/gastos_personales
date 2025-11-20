from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.ingreso.models import Ingreso, Fuente
from apps.usuario.models import Moneda
from datetime import datetime

# Importar utilidades
from apps.utils.calculations import calcular_variacion_mensual, calcular_distribucion_por_campo, asignar_colores
from apps.utils.filters import aplicar_filtros_basicos, obtener_valores_filtros

class UserIngresoQuerysetMixin:
    """Filtra los ingresos para que cada usuario solo vea los suyos."""
    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user)

class IngresoListView(LoginRequiredMixin, UserIngresoQuerysetMixin, ListView):
    """ Vista principal de Ingresos con:
    - Total mensual de ingresos.
    - Distribución de ingresos por fuente.
    - Lista de ingresos recientes con filtros.
    """
    model = Ingreso
    template_name = 'ingreso/ingreso.html'
    context_object_name = 'ingresos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('fuente', 'moneda', 'usuario')
        
        # Aplicar filtros básicos (fecha, monto)
        queryset = aplicar_filtros_basicos(queryset, self.request)
        
        # Filtros específicos de Ingreso
        fuente_id = self.request.GET.get('fuente')
        if fuente_id:
            queryset = queryset.filter(fuente_id=fuente_id)
        
        moneda = self.request.GET.get('moneda')
        if moneda:
            queryset = queryset.filter(moneda__abreviatura=moneda)
        
        return queryset.order_by('-fecha')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        hoy = datetime.now()
        
        # Calcular variación mensual
        variacion = calcular_variacion_mensual(Ingreso, usuario)
        
        # Calcular distribución por fuente (total general, no mensual)
        ingresos_por_fuente, total_general = calcular_distribucion_por_campo(
            Ingreso, 
            usuario, 
            'fuente__nombre',
            mes_actual=False  # Total general
        )
        
        # Asignar colores
        ingresos_por_fuente = asignar_colores(ingresos_por_fuente, [
            '#06B6D4',  # Cyan
            '#F59E0B',  # Amarillo
            '#84CC16',  # Lima
            '#3B82F6',  # Azul
            '#8B5CF6',  # Violeta
            '#EF4444',  # Rojo
        ])
        
        # Obtener valores de filtros
        valores_filtros = obtener_valores_filtros(
            self.request, 
            ['fuente', 'fecha', 'moneda', 'monto_min', 'monto_max']
        )
        
        context.update({
            'total_ingresos_mensual': variacion['total_mes_actual'],
            'variacion_porcentual': variacion['variacion_porcentual'],
            'mes_nombre': hoy.strftime('%B'),
            'ingresos_por_fuente': ingresos_por_fuente,
            'total_general': total_general,
            'fuentes_disponibles': Fuente.objects.all(),
            'monedas_disponibles': Moneda.objects.all(),
            'moneda': usuario.moneda.abreviatura if usuario.moneda else '$',
            **valores_filtros
        })

        return context

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