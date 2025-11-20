"""Utilidades para cálculos comunes."""
from apps.ingreso.models import Ingreso
from apps.gasto.models import Gasto
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
from django.db.models import Count

def calcular_total_mensual(model, usuario, mes=None, año=None):
    """
    Calcula el total mensual de un modelo (Ingreso o Gasto).
    
    Args:
        model: Clase del modelo
        usuario: Usuario autenticado
        mes: Mes a calcular (por defecto: mes actual)
        año: Año a calcular (por defecto: año actual)
    
    Returns:
        Decimal: Total del mes
    """
    hoy = datetime.now()
    mes = mes or hoy.month
    año = año or hoy.year
    
    total = model.objects.filter(
        usuario=usuario,
        fecha__month=mes,
        fecha__year=año
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
    
    return total


def calcular_variacion_mensual(model, usuario):
    """
    Calcula la variación porcentual entre el mes actual y el anterior.
    
    Args:
        model: Clase del modelo
        usuario: Usuario autenticado
    
    Returns:
        dict: {
            'total_mes_actual': Decimal,
            'total_mes_anterior': Decimal,
            'variacion_porcentual': float
        }
    """
    hoy = datetime.now()
    mes_actual = hoy.month
    año_actual = hoy.year
    
    # Calcular mes anterior
    mes_anterior = mes_actual - 1 if mes_actual > 1 else 12
    año_mes_anterior = año_actual if mes_actual > 1 else año_actual - 1
    
    # Totales
    total_mes_actual = calcular_total_mensual(model, usuario, mes_actual, año_actual)
    total_mes_anterior = calcular_total_mensual(model, usuario, mes_anterior, año_mes_anterior)
    
    # Calcular variación porcentual
    if total_mes_anterior > 0:
        variacion = ((total_mes_actual - total_mes_anterior) / total_mes_anterior) * 100
    else:
        variacion = 100 if total_mes_actual > 0 else 0
    
    return {
        'total_mes_actual': total_mes_actual,
        'total_mes_anterior': total_mes_anterior,
        'variacion_porcentual': round(variacion, 1)
    }


def calcular_distribucion_por_campo(model, usuario, campo, mes_actual=True):
    """
    Calcula la distribución y porcentajes por un campo específico.
    
    Args:
        model: Clase del modelo
        usuario: Usuario autenticado
        campo: Campo a agrupar (ej: 'fuente__nombre', 'categoria__nombre')
        mes_actual: Si True, solo calcula del mes actual. Si False, total general.
    
    Returns:
        list: Lista de diccionarios con distribución y porcentajes
    """
    queryset = model.objects.filter(usuario=usuario)
    
    # Filtrar por mes actual si se requiere
    if mes_actual:
        hoy = datetime.now()
        queryset = queryset.filter(
            fecha__month=hoy.month,
            fecha__year=hoy.year
        )
    
    # Agrupar y sumar
    distribucion = queryset.values(campo).annotate(
        total=Sum('monto'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Calcular total general
    total_general = sum(item['total'] for item in distribucion)
    
    # Agregar porcentajes
    resultado = []
    clave = 'categoria' if 'categoria' in campo else 'fuente'

    for item in distribucion:
        porcentaje = (item['total'] / total_general * 100) if total_general > 0 else 0
        resultado.append({
            clave: item[campo],
            'total': item['total'],
            'cantidad': item['cantidad'],
            'porcentaje': round(porcentaje, 1)
        })
    
    return resultado, total_general


def calcular_saldo_mensual(usuario, mes=None, año=None):
    """
    Calcula el saldo mensual: Ingresos - Gastos.
    
    Args:
        usuario: Usuario autenticado
        mes: Mes a calcular (por defecto: mes actual)
        año: Año a calcular (por defecto: año actual)
    
    Returns:
        dict: {
            'total_ingresos': Decimal,
            'total_gastos': Decimal,
            'saldo': Decimal
        }
    """
    total_ingresos = calcular_total_mensual(Ingreso, usuario, mes, año)
    total_gastos = calcular_total_mensual(Gasto, usuario, mes, año)
    saldo = total_ingresos - total_gastos
    
    return {
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
        'saldo': saldo
    }


def asignar_colores(items, colores_predefinidos=None):
    """
    Asigna colores a una lista de items.
    
    Args:
        items: Lista de diccionarios
        colores_predefinidos: Lista de colores hexadecimales
    
    Returns:
        list: Lista con el campo 'color' agregado
    """
    if colores_predefinidos is None:
        colores_predefinidos = [
            '#F97316',  # Naranja
            '#3B82F6',  # Azul
            '#10B981',  # Verde
            '#A855F7',  # Violeta
            '#EF4444',  # Rojo
            '#F59E0B',  # Amarillo
            '#06B6D4',  # Cian
            '#EC4899',  # Rosa
        ]
    
    for i, item in enumerate(items):
        item['color'] = colores_predefinidos[i % len(colores_predefinidos)]
    
    return items