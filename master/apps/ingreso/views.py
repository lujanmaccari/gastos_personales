from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.ingreso.models import Ingreso, Fuente
from apps.usuario.models import Moneda
from django.db.models import Sum, Count
from datetime import datetime
from decimal import Decimal

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
        
        # Obtener parámetros de filtrado
        fuente_id = self.request.GET.get('fuente')
        fecha = self.request.GET.get('fecha')
        moneda = self.request.GET.get('moneda')
        monto_min = self.request.GET.get('monto_min')
        monto_max = self.request.GET.get('monto_max')
        
        # Filtros
        if fuente_id: 
            queryset = queryset.filter(fuente_id=fuente_id)
        
        if fecha:
            queryset = queryset.filter(fecha=fecha)
            
        if moneda:
            queryset = queryset.filter(moneda__abreviatura=moneda)
            
        if monto_min:
            queryset = queryset.filter(monto__gte=monto_min)
            
        if monto_max:
            queryset = queryset.filter(monto__lte=monto_max)
        
        # Ordenar por fecha descendente
        return queryset.order_by('-fecha') 
    
    def get_context_data(self, **kwargs):
        """Agrega datos para el dashboard de ingresos"""
        context = super().get_context_data(**kwargs)
        usuario = self.request.user

        # Obtener mes y año actual
        hoy = datetime.now()
        mes_actual = hoy.month
        año_actual = hoy.year
        
        # TOTAL INGRESOS MENSUAL
        ingresos_mes_actual = Ingreso.objects.filter(
            usuario=usuario,
            fecha__month=mes_actual,
            fecha__year=año_actual
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        # Calcular mes anterior para comparación
        mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
        año_mes_anterior = año_actual if mes_actual > 1 else año_actual - 1
        
        ingresos_mes_anterior = Ingreso.objects.filter(
            usuario=usuario,
            fecha__month=mes_anterior,
            fecha__year=año_mes_anterior
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        # Calcular porcentaje de variación
        if ingresos_mes_anterior > 0:
            variacion_porcentual = ((ingresos_mes_actual - ingresos_mes_anterior) / ingresos_mes_anterior) * 100
        else:
            variacion_porcentual = 100 if ingresos_mes_actual > 0 else 0
            
        # INGRESOS POR FUENTE
        ingresos_por_fuente = Ingreso.objects.filter(
            usuario=usuario
        ).values('fuente__nombre').annotate(
            total=Sum('monto'),
            cantidad=Count('id')
        ).order_by('-total')
        
        # Calcular total general para porcentajes
        total_general = sum(item['total'] for item in ingresos_por_fuente)
        
        # Agregar porcentajes
        ingresos_por_fuente_con_porcentaje = []
        for item in ingresos_por_fuente:
            porcentaje = (item['total'] / total_general * 100) if total_general > 0 else 0
            ingresos_por_fuente_con_porcentaje.append({
                'fuente': item['fuente__nombre'],
                'total': item['total'],
                'cantidad': item['cantidad'],
                'porcentaje': round(porcentaje, 1)
            })
        
        # LISTA DE FUENTES PARA EL FILTRO
        fuentes_disponibles = Fuente.objects.all()
        
        # LISTA DE MONEDAS PARA EL FILTRO
        monedas_disponibles = Moneda.objects.all()
        
        # AGREGAR TODO AL CONTEXTO
        context.update({
            'total_ingresos_mensual': ingresos_mes_actual,
            'variacion_porcentual': round(variacion_porcentual, 1),
            'mes_nombre': hoy.strftime('%B'),
            'ingresos_por_fuente': ingresos_por_fuente_con_porcentaje,
            'total_general': total_general or Decimal('0.00'),
            'fuentes_disponibles': fuentes_disponibles,
            'moneda': usuario.moneda.abreviatura if usuario.moneda else '$',
            'monedas_disponibles': monedas_disponibles,
            
            # Mantener los valores de los filtros en el template
            'filtro_fuente': self.request.GET.get('fuente', ''),
            'filtro_fecha': self.request.GET.get('fecha', ''),
            'filtro_moneda': self.request.GET.get('moneda', ''),
            'filtro_monto_min': self.request.GET.get('monto_min', ''),
            'filtro_monto_max': self.request.GET.get('monto_max', ''),
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