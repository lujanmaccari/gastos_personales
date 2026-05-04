"""Utilidades para aplicar filtros a querysets."""
from django.db.models import Q
from decimal import Decimal

def aplicar_filtros_basicos(queryset, request):
    """
    Aplica filtros básicos de fecha y monto a un queryset.
    
    Args:
        queryset: QuerySet a filtrar
        request: Objeto HttpRequest con parámetros GET
    
    Returns:
        QuerySet filtrado
    """
    # Filtro por fecha
    fecha = request.GET.get('fecha')
    if fecha:
        queryset = queryset.filter(fecha=fecha)
    
    # Filtro por monto mínimo
    monto_min = request.GET.get('monto_min')
    if monto_min:
        try:
            queryset = queryset.filter(monto__gte=Decimal(monto_min))
        except:
            pass
    
    # Filtro por monto máximo
    monto_max = request.GET.get('monto_max')
    if monto_max:
        try:
            queryset = queryset.filter(monto__lte=Decimal(monto_max))
        except:
            pass
    
    return queryset


def aplicar_busqueda(queryset, request, campos_busqueda):
    """
    Aplica búsqueda en múltiples campos.
    
    Args:
        queryset: QuerySet a filtrar
        request: Objeto HttpRequest con parámetros GET
        campos_busqueda: Lista de campos donde buscar (ej: ['descripcion', 'categoria__nombre'])
    
    Returns:
        QuerySet filtrado
    """
    search = request.GET.get('search', '').strip()
    
    if search:
        q_objects = Q()
        for campo in campos_busqueda:
            q_objects |= Q(**{f'{campo}__icontains': search})
        queryset = queryset.filter(q_objects)
    
    return queryset


def obtener_valores_filtros(request, campos):
    """
    Obtiene los valores de los filtros del request para mantenerlos en el formulario.
    
    Args:
        request: Objeto HttpRequest
        campos: Lista de nombres de campos (ej: ['fecha', 'categoria', 'monto_min'])
    
    Returns:
        dict: Diccionario con valores de filtros
    """
    valores = {}
    for campo in campos:
        valores[f'filtro_{campo}'] = request.GET.get(campo, '')
    
    # Agregar búsqueda si existe
    valores['search_query'] = request.GET.get('search', '')
    
    return valores