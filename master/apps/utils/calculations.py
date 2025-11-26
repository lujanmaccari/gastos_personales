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
    from apps.utils.currency_service import CurrencyService
    from decimal import Decimal
    from datetime import datetime
    
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
    """Retorna colores específicos para categorías de gasto"""
    colores = {
        'comida': "#FFFB1C",      # Amarillo
        'amarillo': "#FFFB1C",    
        'hogar': '#EF4444',       # Rojo
        'rojo': '#EF4444',        
        'transporte': '#3B82F6',  # Azul
        'azul': '#3B82F6',        
        'compras': '#8B5CF6',     # Violeta
        'violeta': '#8B5CF6',     
        'servicios': '#06B6D4',   # Cyan
        'ocio': "#12CA31",        # Verde
        'verde': "#12CA31",       
        'salud': "#A4E2FF",       # Celeste
        'educación': '#D946EF',   # Rosa 
        'rosa': '#D946EF',        
        'viaje': '#FFA500',       # Naranja
        'naranja': '#FFA500',     
        'otro': '#9CA3AF',        # Gris
        'gris': '#9CA3AF',        
    }
    return colores
def asignar_iconos_y_colores_categorias_gastos(items):
    """
    Asigna íconos y colores a fuentes de ingreso basándose en el nombre.

    Args:
        items: Lista de diccionarios con la clave 'fuente'

    Returns:
        list: Items con las claves 'icono', 'color_badge', y 'colores' agregadas
    """
    colores_categorias = asignar_colores_categorias_gastos()
    
    for i, item in enumerate(items):
        # Obtener el nombre de la categoria (puede venir como 'categoria' o 'nombre')
        nombre = item.get("categoria", item.get("nombre", ""))
        
        if nombre is None:
            nombre = "otro"
        else:
            nombre = nombre.lower()
            
        # Asignar color del gráfico
        item['color'] = colores_categorias.get(nombre, colores_categorias['otro'])
        
        # Asignar ícono y color del badge según el nombre
        if "comida" in nombre or "alimentos" in nombre:
            item["icono"] = "fas fa-utensils"
            item["color_icono"] = "text-yellow-500"
            item["color_badge"] = "text-yellow-800 bg-yellow-100"
        elif "hogar" in nombre or "alquiler" in nombre:
            item["icono"] = "fas fa-home"
            item["color_icono"] = "text-red-500"
            item["color_badge"] = "text-red-800 bg-red-100"
        elif "transporte" in nombre or "movilidad"in nombre:
            item["icono"] = "fas fa-bus"
            item["color_icono"] = "text-blue-500"
            item["color_badge"] = "text-blue-800 bg-blue-100"
        elif "compras" in nombre or "shopping" in nombre:
            item["icono"] = "fas fa-shopping-bag"
            item["color_icono"] = "text-purple-500"
            item["color_badge"] = "text-purple-800 bg-purple-100"
        elif "servicios" in nombre:
            item["icono"] = "fas fa-concierge-bell"
            item["color_icono"] = "text-cyan-500"
            item["color_badge"] = "text-cyan-800 bg-cyan-100"
        elif "ocio" in nombre or "entretenimiento" in nombre:
            item["icono"] = "fas fa-film"
            item["color_icono"] = "text-green-500"
            item["color_badge"] = "text-green-800 bg-green-100"
        elif "salud" in nombre:
            item["icono"] = "fas fa-heartbeat"
            item["color_icono"] = "text-sky-500"
            item["color_badge"] = "text-sky-800 bg-sky-100"
        elif "educación" in nombre:
            item["icono"] = "fas fa-book"
            item["color_icono"] = "text-pink-500"
            item["color_badge"] = "text-pink-800 bg-pink-100"
        elif "viaje" in nombre or "vacaciones" in nombre:
            item["icono"] = "fas fa-plane"
            item["color_icono"] = "text-orange-500"
            item["color_badge"] = "text-orange-800 bg-orange-100"
        else:
            item["icono"] = "fas fa-dollar-sign"
            item["color_icono"] = "text-gray-500"
            item["color_badge"] = "text-gray-800 bg-gray-100"
    
    return items

def procesar_categorias(items):
    """
        Procesa categorías para agregar estilos CSS inline.
        
        Args:
            items: QuerySet de Categoria con .select_related('color', 'icono')
        
        Returns:
            list: Lista de diccionarios con estilos procesados
        """
        
    def darken_hex(hex_code, factor=0.75):
        """Oscurece un color hexadecimal"""
        hex_code = hex_code.lstrip("#")
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)

        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)

        return f"#{r:02x}{g:02x}{b:02x}"

    def rgba_from_hex(hex_code, opacity=0.15):
        """Convierte hex a rgba con opacidad"""
        hex_code = hex_code.lstrip("#")
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)

        return f"rgba({r},{g},{b},{opacity})"

    # Mapeo de nombres a íconos FontAwesome
    ICON_MAP = {
        "comida": "fas fa-utensils",
        "alimentación": "fas fa-utensils",
        "alimentacion": "fas fa-utensils",

        "transporte": "fas fa-bus",

        "hogar": "fas fa-home",
        "casa": "fas fa-home",

        "entretenimiento": "fas fa-film",
        "ocio": "fas fa-film",

        "gimnasio": "fas fa-dumbbell",
        "gym": "fas fa-dumbbell",

        "viaje": "fas fa-plane",
        "viajes": "fas fa-plane",

        "educacion": "fas fa-book",
        "educación": "fas fa-book",

        "salud": "fas fa-heartbeat",

        "mascotas": "fas fa-paw",
        "mascota": "fas fa-paw",

        "regalo": "fas fa-gift",
        "regalos": "fas fa-gift",

        "compras": "fas fa-shopping-bag",
        "compra": "fas fa-shopping-bag",
        }

    procesadas = []

    for cat in items:
        # Obtener el código hex del color
        base = cat.color.codigo_hex if cat.color else "#9CA3AF"
        darker = darken_hex(base)
        bg = rgba_from_hex(base, 0.15)
            
        # Obtener la clase del ícono
        # Primero intentar del objeto icono.icono, sino del mapeo
        if cat.icono:
            icon_class = cat.icono.icono
        else:
            icon_class = ICON_MAP.get(cat.nombre.lower(), "fas fa-circle")

        # Crear diccionario con todos los atributos del objeto original
        cat_dict = {
            'id': cat.id,
            'nombre': cat.nombre,
            'descripcion': cat.descripcion,
            'usuario_id': cat.usuario_id,
            'color_id': cat.color_id,
            'icono_id': cat.icono_id,
            # Agregar el total si existe (para top_categorias)
            'total': getattr(cat, 'total', None),
            # Estilos procesados
            'icono': icon_class,
            'color_icono': f"color: {base};",       
            'color_bg': f"background-color: {bg};",  
            'color_texto': f"color: {darker};",
            }
        
        procesadas.append(cat_dict)

    return procesadas