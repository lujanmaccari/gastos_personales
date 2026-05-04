"""Utilidades para cálculos comunes."""
from apps.ingreso.models import Ingreso
from apps.gasto.models import Gasto
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
from django.db.models import Count
from apps.utils.currency_service import CurrencyService
from decimal import Decimal
from datetime import datetime
from apps.utils.categoria.style_helpers import darken_hex, rgba_from_hex


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

def calcular_total_mensual_convertido(model, usuario, user_currency, mes=None, año=None):
    """
    Calcula el total mensual con conversión de monedas.
    
    Args:
        model: Clase del modelo (Ingreso o Gasto)
        usuario: Usuario autenticado
        user_currency: Moneda preferida del usuario
        mes: Mes a calcular
        año: Año a calcular
    """
    
    hoy = datetime.now()
    mes = mes or hoy.month
    año = año or hoy.year
    
    items = model.objects.filter(
        usuario=usuario,
        fecha__month=mes,
        fecha__year=año
    ).select_related('moneda')
    
    total_convertido = Decimal('0.00')
    
    for item in items:
        item_currency = item.moneda.abreviatura if item.moneda else 'ARS'
        
        if item_currency == user_currency:
            total_convertido += item.monto
        else:
            converted = CurrencyService.convert_amount(
                item.monto,
                item_currency,
                user_currency
            )
            if converted:
                total_convertido += converted
    
    return total_convertido

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


def asignar_colores_fuentes_ingresos():
    """Retorna colores específicos para fuentes de ingreso"""
    colores = {
        'sueldo': '#06B6D4',  # Cyan
        'freelance': '#F59E0B',  # Naranja 
        'devolución': '#84CC16',  # Lima 
        'inversión': '#3B82F6',  # Azul 
        'bonificación': '#8B5CF6',  # Violeta 
        'venta': '#EF4444',  # Rojo 
        'otro': '#9CA3AF',  # Gris 
    }
    return colores

def asignar_iconos_y_colores_fuentes_ingresos(items):
    """
    Asigna íconos y colores a fuentes de ingreso basándose en el nombre.

    Args:
        items: Lista de diccionarios con la clave 'fuente'

    Returns:
        list: Items con las claves 'icono', 'color_badge', y 'colores' agregadas
    """
    colores_fuentes = asignar_colores_fuentes_ingresos()
    
    for i, item in enumerate(items):
        # Obtener el nombre de la fuente (puede venir como 'fuente' o 'nombre')
        nombre = item.get("fuente", item.get("nombre", ""))
        
        if nombre is None:
            nombre = "otro"
        else:
            nombre = nombre.lower()
        
        # Asignar color del gráfico
        item['color'] = colores_fuentes.get(nombre, colores_fuentes['otro'])
        
        # Asignar ícono y color del badge según el nombre
        if "sueldo" in nombre or "salario" in nombre:
            item["icono"] = "fas fa-briefcase"
            item["color_icono"] = "text-cyan-500"
            item["color_badge"] = "text-cyan-800 bg-cyan-100"
        elif "freelance" in nombre:
            item["icono"] = "fas fa-laptop-code"
            item["color_icono"] = "text-amber-500"
            item["color_badge"] = "text-amber-800 bg-amber-100"
        elif "devolución" in nombre or "devoluciones" in nombre:
            item["icono"] = "fas fa-undo"
            item["color_icono"] = "text-lime-500"
            item["color_badge"] = "text-lime-800 bg-lime-100"
        elif "inversión" in nombre or "inversiones" in nombre:
            item["icono"] = "fas fa-chart-line"
            item["color_icono"] = "text-blue-500"
            item["color_badge"] = "text-blue-800 bg-blue-100"
        elif "bonificación" in nombre or "bono" in nombre:
            item["icono"] = "fas fa-gift"
            item["color_icono"] = "text-purple-500"
            item["color_badge"] = "text-purple-800 bg-purple-100"
        elif "venta" in nombre:
            item["icono"] = "fas fa-shopping-cart"
            item["color_icono"] = "text-red-500"
            item["color_badge"] = "text-red-800 bg-red-100"
        else:
            item["icono"] = "fas fa-dollar-sign"
            item["color_icono"] = "text-gray-500"
            item["color_badge"] = "text-gray-800 bg-gray-100"
    
    return items

def asignar_colores_categorias_gastos():
    """
    Retorna colores predeterminados para categorías de gasto.
    Usado SOLO para inicializar la BD cuando no hay colores.
    """
    colores = {
        'comida': "#FFFB1C",
        'amarillo': "#FFFB1C",
        'hogar': '#EF4444',
        'rojo': '#EF4444',
        'transporte': '#3B82F6',
        'azul': '#3B82F6',
        'compras': '#8B5CF6',
        'violeta': '#8B5CF6',
        'servicios': '#06B6D4',
        'ocio': "#12CA31",
        'verde': "#12CA31",
        'salud': "#A4E2FF",
        'educación': '#D946EF',
        'rosa': '#D946EF',
        'viaje': '#FFA500',
        'naranja': '#FFA500',
        'otro': '#9CA3AF',
        'gris': '#9CA3AF',
    }
    return colores

def asignar_iconos_y_colores_categorias_gastos(items):
    """
        Se mantiene solo para compatibilidad con código legacy.
        Los colores e íconos ahora vienen directamente de la BD.
        """
    colores_categorias = asignar_colores_categorias_gastos()
    
    ICON_MAP = {
        "comida": "fas fa-utensils",
        "hogar": "fas fa-home",
        "transporte": "fas fa-bus",
        "compras": "fas fa-shopping-bag",
        "servicios": "fas fa-concierge-bell",
        "ocio": "fas fa-film",
        "salud": "fas fa-heartbeat",
        "educación": "fas fa-book",
        "viaje": "fas fa-plane",
    }
    
    for item in items:
        nombre = item.get("categoria", item.get("nombre", "")).lower()
        item['color'] = colores_categorias.get(nombre, colores_categorias.get('otro', '#9CA3AF'))
        item['icono'] = ICON_MAP.get(nombre, "fas fa-dollar-sign")
    
    return items

def procesar_categorias(items):
    """
    Procesa categorías para agregar estilos CSS inline.
    Usado SOLO en CategoriaListView para mostrar la lista de categorías.
    
    Args:
        items: QuerySet de Categoria con .select_related('color', 'icono')
    
    Returns:
        list: Lista de diccionarios con estilos procesados
    """    
    # Mapeo de nombres a íconos FontAwesome
    ICON_MAP = {
        "comida": "fas fa-utensils",
        "alimentación": "fas fa-utensils",
        "transporte": "fas fa-bus",
        "hogar": "fas fa-home",
        "entretenimiento": "fas fa-film",
        "ocio": "fas fa-film",
        "gimnasio": "fas fa-dumbbell",
        "viaje": "fas fa-plane",
        "educacion": "fas fa-book",
        "educación": "fas fa-book",
        "salud": "fas fa-heartbeat",
        "mascotas": "fas fa-paw",
        "regalo": "fas fa-gift",
        "compras": "fas fa-shopping-bag",
    }

    procesadas = []

    for cat in items:
        # Obtener color
        base = cat.color.codigo_hex if cat.color else "#9CA3AF"
        darker = darken_hex(base)
        bg = rgba_from_hex(base, 0.15)
        
        # Obtener ícono (primero de BD, sino del mapeo)
        if cat.icono:
            icon_class = cat.icono.icono
        else:
            icon_class = ICON_MAP.get(cat.nombre.lower(), "fas fa-circle")

        # Crear diccionario
        cat_dict = {
            'id': cat.id,
            'nombre': cat.nombre,
            'descripcion': cat.descripcion,
            'usuario_id': cat.usuario_id,
            'color_id': cat.color_id,
            'icono_id': cat.icono_id,
            'total': getattr(cat, 'total', None),  # Para top_categorias
            # Estilos procesados
            'icono': icon_class,
            'color_icono': f"color: {base};",
            'color_bg': f"background-color: {bg};",
            'color_texto': f"color: {darker};",
        }
        
        procesadas.append(cat_dict)

    return procesadas
