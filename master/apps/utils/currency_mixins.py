"""
Mixins para aplicar conversión de monedas en vistas
Ubicación: apps/utils/currency_mixins.py

Estos mixins extienden la funcionalidad de las vistas existentes
para convertir automáticamente los montos a la moneda preferida del usuario.
"""
from decimal import Decimal
from django.db.models import Sum, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from apps.utils.currency_service import CurrencyService
from django.db.models import Count


class CurrencyConversionMixin:
    """
    Mixin que agrega conversión de monedas a las vistas.
    Convierte todos los montos a la moneda preferida del usuario.
    """
    
    def get_user_currency(self):
        """Obtiene la moneda preferida del usuario."""
        return self.request.user.moneda.abreviatura if self.request.user.moneda else 'ARS'
    
    def convert_to_user_currency(self, amount, from_currency):
        """
        Convierte un monto a la moneda del usuario.
        
        Args:
            amount: Monto a convertir
            from_currency: Moneda origen del monto
            
        Returns:
            Monto convertido como Decimal
        """
        user_currency = self.get_user_currency()
        
        if not amount or amount == 0:
            return Decimal('0.00')
        
        if from_currency == user_currency:
            return amount
        
        converted = CurrencyService.convert_amount(
            Decimal(str(amount)),
            from_currency,
            user_currency
        )
        
        return converted if converted else amount
    
    def convert_queryset_amounts(self, queryset):
        """
        Convierte los montos de un queryset a la moneda del usuario.
        Agrega el campo 'monto_convertido' a cada objeto.
        
        Args:
            queryset: QuerySet de Gasto o Ingreso
            
        Returns:
            Lista de objetos con monto_convertido
        """
        user_currency = self.get_user_currency()
        items_convertidos = []
        
        for item in queryset:
            item_currency = item.moneda.abreviatura if item.moneda else 'ARS'
            
            if item_currency == user_currency:
                item.monto_convertido = item.monto
                item.moneda_original = item_currency
                item.fue_convertido = False
            else:
                converted = self.convert_to_user_currency(item.monto, item_currency)
                item.monto_convertido = converted
                item.moneda_original = item_currency
                item.fue_convertido = True
            
            items_convertidos.append(item)
        
        return items_convertidos

    def calculate_distribution_converted(self, model, usuario, field_name):
        """
        Calcula la distribución por un campo específico CON conversión de monedas.
        
        Args:
            model: Modelo (Ingreso o Gasto)
            usuario: Usuario actual
            field_name: Campo por el que agrupar ('fuente' o 'categoria')
            
        Returns:
            tuple: (lista_distribucion, total_general_convertido)
        """

        user_currency = self.get_user_currency()
        
        # Obtener todos los items
        items = model.objects.filter(usuario=usuario).select_related('moneda')
        
        # Agrupar manualmente por el campo
        grupos = {}
        total_general = Decimal('0.00')
        
        for item in items:
            # Obtener el valor del campo (ej: 'Sueldo', 'Comida')
            field_value = item
            for field in field_name.split('__'):
                field_value = getattr(field_value, field, None)
                if field_value is None:
                    break
            
            if field_value is None:
                continue
                
            field_value = str(field_value)
            
            # Convertir monto
            item_currency = item.moneda.abreviatura if item.moneda else 'ARS'
            
            if item_currency == user_currency:
                monto_convertido = item.monto
            else:
                monto_convertido = self.convert_to_user_currency(item.monto, item_currency)
            
            # Acumular en grupos
            if field_value not in grupos:
                grupos[field_value] = {
                    'total': Decimal('0.00'),
                    'cantidad': 0
                }
            
            grupos[field_value]['total'] += monto_convertido
            grupos[field_value]['cantidad'] += 1
            total_general += monto_convertido
        
        # Formatear resultado
        resultado = []
        clave = 'categoria' if 'categoria' in field_name else 'fuente'
        
        for nombre, datos in sorted(grupos.items(), key=lambda x: x[1]['total'], reverse=True):
            porcentaje = (datos['total'] / total_general * 100) if total_general > 0 else 0
            resultado.append({
                clave: nombre,
                'total': datos['total'],
                'cantidad': datos['cantidad'],
                'porcentaje': round(porcentaje, 1)
            })
        
        return resultado, total_general


class DashboardCurrencyMixin(CurrencyConversionMixin):
    """
    Mixin especializado para el Dashboard que convierte todos los totales.
    """
    
    def total_ingresos_mes_converted(self):
        """Ingresos del mes convertidos a moneda del usuario."""
        ingresos = self.get_ingresos().filter(fecha__gte=self.get_last_30_days())
        return self._sum_with_conversion(ingresos)
    
    def total_gastos_mes_converted(self):
        """Gastos del mes convertidos a moneda del usuario."""
        gastos = self.get_gastos().filter(fecha__gte=self.get_last_30_days())
        return self._sum_with_conversion(gastos)
    
    def total_ingresos_mes_pasado_converted(self):
        """Ingresos del mes pasado convertidos."""
        ingresos = self.get_ingresos().filter(
            fecha__gte=self.get_last_60_days(),
            fecha__lt=self.get_last_30_days()
        )
        return self._sum_with_conversion(ingresos)
    
    def total_gastos_mes_pasado_converted(self):
        """Gastos del mes pasado convertidos."""
        gastos = self.get_gastos().filter(
            fecha__gte=self.get_last_60_days(),
            fecha__lt=self.get_last_30_days()
        )
        return self._sum_with_conversion(gastos)
    
    def _sum_with_conversion(self, queryset):
        """
        Suma los montos de un queryset convirtiendo cada uno a la moneda del usuario.
        
        Args:
            queryset: QuerySet de Ingreso o Gasto
            
        Returns:
            Decimal con el total convertido
        """
        user_currency = self.get_user_currency()
        total = Decimal('0.00')
        
        # Agrupar por moneda para optimizar conversiones
        items_by_currency = {}
        
        for item in queryset.select_related('moneda'):
            item_currency = item.moneda.abreviatura if item.moneda else 'ARS'
            
            if item_currency not in items_by_currency:
                items_by_currency[item_currency] = Decimal('0.00')
            
            items_by_currency[item_currency] += item.monto
        
        # Convertir cada total por moneda
        for currency, amount in items_by_currency.items():
            if currency == user_currency:
                total += amount
            else:
                converted = self.convert_to_user_currency(amount, currency)
                total += converted
        
        return total
    
    def balance_mensual_converted(self):
        """Balance mensual en moneda del usuario."""
        return self.total_ingresos_mes_converted() - self.total_gastos_mes_converted()
    
    def balance_mensual_pasado_converted(self):
        """Balance mensual pasado en moneda del usuario."""
        return self.total_ingresos_mes_pasado_converted() - self.total_gastos_mes_pasado_converted()
    
    def get_6_meses_gastos_chart_converted(self):
        """
        Gráfico de 6 meses con gastos convertidos.
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models.functions import TruncMonth
        import calendar
        
        hoy = timezone.now()
        hace_6_meses = hoy - timedelta(days=180)
        user_currency = self.get_user_currency()
        
        # Obtener gastos agrupados por mes
        gastos = (
            self.get_gastos()
            .filter(fecha__gte=hace_6_meses)
            .annotate(mes=TruncMonth('fecha'))
            .select_related('moneda')
        )
        
        # Agrupar manualmente y convertir
        meses_data = {}
        
        for gasto in gastos:
            mes_key = gasto.mes
            item_currency = gasto.moneda.abreviatura if gasto.moneda else 'ARS'
            
            if mes_key not in meses_data:
                meses_data[mes_key] = Decimal('0.00')
            
            if item_currency == user_currency:
                meses_data[mes_key] += gasto.monto
            else:
                converted = self.convert_to_user_currency(gasto.monto, item_currency)
                meses_data[mes_key] += converted
        
        # Formatear para el gráfico
        meses_labels = []
        valores = []
        
        for mes, total in sorted(meses_data.items()):
            mes_num = mes.month
            meses_labels.append(calendar.month_abbr[mes_num])
            valores.append(float(total))
        
        return meses_labels, valores


class ListViewCurrencyMixin(CurrencyConversionMixin):
    """
    Mixin para ListView que convierte los items mostrados.
    """
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Convertir los items del queryset
        items = list(context[self.context_object_name])
        items_convertidos = self.convert_queryset_amounts(items)
        
        context[self.context_object_name] = items_convertidos
        context['user_currency'] = self.get_user_currency()
        context['conversion_enabled'] = True
        
        return context

