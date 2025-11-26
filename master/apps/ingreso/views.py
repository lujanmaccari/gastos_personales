from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.ingreso.models import Ingreso, Fuente
from apps.usuario.models import Moneda
from datetime import datetime
from decimal import Decimal

# Importar utilidades
from apps.utils.calculations import calcular_variacion_mensual, asignar_iconos_y_colores_fuentes_ingresos
from apps.utils.filters import aplicar_filtros_basicos, obtener_valores_filtros
from apps.utils.currency_mixins import ListViewCurrencyMixin

class UserIngresoQuerysetMixin:
    """Filtra los ingresos para que cada usuario solo vea los suyos."""
    def get_queryset(self):
        return Ingreso.objects.filter(usuario=self.request.user)

class IngresoListView(LoginRequiredMixin, UserIngresoQuerysetMixin, ListViewCurrencyMixin, ListView):
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
        
        # Aplicar todos los filtros de una vez
        queryset = aplicar_filtros_basicos(queryset, self.request)
        
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
        user_currency = self.get_user_currency()
        
        # Una consulta base para ingresos del mes
        ingresos_mes = Ingreso.objects.filter(
            usuario=usuario,
            fecha__month=hoy.month,
            fecha__year=hoy.year
        ).select_related('moneda', 'fuente')
        
        # Calcular total y distribución en una iteración
        total_ingresos_convertido = Decimal('0.00')
        ingresos_por_fuente = {}
        
        for ingreso in ingresos_mes:
            # Conversión de moneda
            ingreso_currency = ingreso.moneda.abreviatura if ingreso.moneda else 'ARS'
            monto_convertido = (
                ingreso.monto 
                if ingreso_currency == user_currency 
                else self.convert_to_user_currency(ingreso.monto, ingreso_currency)
            )
            
            total_ingresos_convertido += monto_convertido
            
            # Acumular por fuente al mismo tiempo
            fuente_nombre = ingreso.fuente.nombre if ingreso.fuente else 'Sin fuente'
            if fuente_nombre not in ingresos_por_fuente:
                ingresos_por_fuente[fuente_nombre] = Decimal('0.00')
            ingresos_por_fuente[fuente_nombre] += monto_convertido
        
        # Calcular porcentajes
        ingresos_por_fuente_list = [
            {
                'fuente': fuente,
                'total': monto,
                'porcentaje': round((monto / total_ingresos_convertido * 100), 2) if total_ingresos_convertido > 0 else 0
            }
            for fuente, monto in ingresos_por_fuente.items()
        ]
        
        # Ordenar por porcentaje (de mayor a menor)
        ingresos_por_fuente_list.sort(key=lambda x: x['porcentaje'], reverse=True)
        
        # Asignar iconos y colores
        ingresos_por_fuente_list = asignar_iconos_y_colores_fuentes_ingresos(ingresos_por_fuente_list)
        
        # Calcular variación solo si es necesario
        variacion = calcular_variacion_mensual(Ingreso, usuario)
        
        # Filtros
        valores_filtros = obtener_valores_filtros(
            self.request, 
            ['fuente', 'fecha', 'moneda', 'monto_min', 'monto_max']
        )
        
        # Obtener moneda del usuario
        moneda_usuario = usuario.moneda.abreviatura if hasattr(usuario, 'moneda') and usuario.moneda else '$'
        
        context.update({
            'total_ingresos_mensual': total_ingresos_convertido,
            'variacion_porcentual': variacion['variacion_porcentual'],
            'mes_nombre': hoy.strftime('%B'),
            'ingresos_por_fuente': ingresos_por_fuente_list,
            'total_general': total_ingresos_convertido,
            'fuentes_disponibles': Fuente.objects.all(),
            'monedas_disponibles': Moneda.objects.all(),
            'moneda': moneda_usuario,
            'user_currency': user_currency,
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