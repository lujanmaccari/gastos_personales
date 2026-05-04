from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.ingreso.models import Ingreso
from apps.gasto.models import Gasto
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import calendar
from django.views.generic import TemplateView
from apps.utils.currency_mixins import DashboardCurrencyMixin

# Create your views here.

class UserIngresoQuerysetMixin:
    '''se crea get_ingresos para no sobreescribir el metodo get_queryset de la clase ListView'''
    def get_ingresos(self):
        return Ingreso.objects.filter(usuario=self.request.user)

class UserGastoQuerysetMixin:
    '''se crea get_gastos para no sobreescribir el metodo get_queryset de la clase ListView'''
    def get_gastos(self):
        return Gasto.objects.filter(usuario=self.request.user)



class DashboardCalculatorMixin:

    def get_last_30_days(self):
        return timezone.now() - timedelta(days=30)

    def get_last_60_days(self):
        return timezone.now() - timedelta(days=60)

    def calculate_growth(self, current, previous):
        if previous == 0:
            return 0
        return round((current - previous) / previous * 100, 2)

    # ----------- INGRESOS -----------
    def total_ingresos_mes(self):
        """Ingresos últimos 30 días"""
        return (
            self.get_ingresos()
            .filter(fecha__gte=self.get_last_30_days())
            .aggregate(total=Sum('monto'))['total'] or 0
        )

    def total_ingresos_mes_pasado(self):
        """Ingresos desde 60 a 30 días atrás"""
        return (
            self.get_ingresos()
            .filter(
                fecha__gte=self.get_last_60_days(),
                fecha__lt=self.get_last_30_days()
            )
            .aggregate(total=Sum('monto'))['total'] or 0
        )

    def crecimiento_ingresos(self):
        return self.calculate_growth(
            self.total_ingresos_mes(),
            self.total_ingresos_mes_pasado()
        )

    # ----------- GASTOS -----------
    def total_gastos_mes(self):
        return (
            self.get_gastos()
            .filter(fecha__gte=self.get_last_30_days())
            .aggregate(total=Sum('monto'))['total'] or 0
        )

    def total_gastos_mes_pasado(self):
        return (
            self.get_gastos()
            .filter(
                fecha__gte=self.get_last_60_days(),
                fecha__lt=self.get_last_30_days()
            )
            .aggregate(total=Sum('monto'))['total'] or 0
        )

    def crecimiento_gastos(self):
        return self.calculate_growth(
            self.total_gastos_mes(),
            self.total_gastos_mes_pasado()
        )

    # -----------BALANCE MENSUAL-----------
    def balance_mensual(self):
        return self.total_ingresos_mes() - self.total_gastos_mes()

    def balance_mensual_pasado(self):
        return self.total_ingresos_mes_pasado() - self.total_gastos_mes_pasado()
    
    def crecimiento_balance(self):
        return self.calculate_growth(
            self.balance_mensual(),
            self.balance_mensual_pasado()
        )

    def top_categoria_mes(self):
        top=(
            self.get_gastos()
            .filter(fecha__gte=self.get_last_30_days())
            .values('categoria__nombre')
            .annotate(total=Sum('monto'))
            .order_by('-total')
            .first()
        )
        return top['categoria__nombre'] if top else None
    
    # -----------GRAFICO GASTOS MENSUALES-----------
    def get_6_meses_gastos_chart(self):
        hoy = timezone.now()
        hace_6_meses = hoy - timedelta(days=180)

        gastos = (
            self.get_gastos()
            .filter(fecha__gte=hace_6_meses)
            .annotate(mes=TruncMonth('fecha'))
            .values('mes')
            .annotate(total=Sum('monto'))
            .order_by('mes')
        )

        meses_labels = []
        valores = []

        for g in gastos:
            mes_num = g['mes'].month
            meses_labels.append(calendar.month_abbr[mes_num])  
            valores.append(float(g['total'])) 

        return meses_labels, valores

class DashboardView(
    LoginRequiredMixin,
    UserIngresoQuerysetMixin,
    UserGastoQuerysetMixin,
    DashboardCalculatorMixin,
    DashboardCurrencyMixin,
    TemplateView
):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Usar métodos con conversión
        ingresos_actual = self.total_ingresos_mes_converted()
        gastos_actual = self.total_gastos_mes_converted()
        balance_mensual = self.balance_mensual_converted()
        balance_mensual_pasado = self.balance_mensual_pasado_converted()
        
        # Calcular crecimiento con valores convertidos
        crecimiento_ingresos = self.calculate_growth(
            ingresos_actual,
            self.total_ingresos_mes_pasado_converted()
        )
        
        crecimiento_gastos = self.calculate_growth(
            gastos_actual,
            self.total_gastos_mes_pasado_converted()
        )
        
        crecimiento_balance = self.calculate_growth(
            balance_mensual,
            balance_mensual_pasado
        )
        
        top_categoria_mes = self.top_categoria_mes()
        meses, valores = self.get_6_meses_gastos_chart_converted()

        context.update({
            'total_ingresos_mes': ingresos_actual,
            'crecimiento_ingresos': crecimiento_ingresos,
            'total_gastos_mes': gastos_actual,
            'crecimiento_gastos': crecimiento_gastos,
            'balance_mensual': balance_mensual,
            'crecimiento_balance': crecimiento_balance,
            'balance_mensual_pasado': balance_mensual_pasado,
            'top_categoria_mes': top_categoria_mes,
            'ultimos_meses': meses,
            'valores_gastos_mensuales': valores,
            'user_currency': self.get_user_currency(),
        })

        return context
