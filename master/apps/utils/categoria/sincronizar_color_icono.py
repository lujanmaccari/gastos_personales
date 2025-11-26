"""
Utilidades para sincronizar Color e Icono
"""
from apps.categoria.models import Color, Icono
from apps.utils.calculations import (
    asignar_colores_categorias_gastos,
    asignar_iconos_y_colores_categorias_gastos
)


def get_icon_class_from_name(nombre_categoria):
    """
    Obtiene la clase de FontAwesome usando la lógica de calculations.py
    
    Args:
        nombre_categoria: str - Nombre de la categoría (ej: 'comida', 'transporte')
    
    Returns:
        str - Clase de FontAwesome (ej: 'fas fa-utensils')
    """
    
    item_procesado = asignar_iconos_y_colores_categorias_gastos([
        {"categoria": nombre_categoria}
    ])
    
    return item_procesado[0].get("icono", "fas fa-dollar-sign")


def get_color_hex_from_name(nombre_color_o_categoria):
    """
    Obtiene el código hexadecimal usando la lógica de calculations.py
    
    Args:
        nombre_color_o_categoria: str - Nombre del color o categoría
    
    Returns:
        str - Código hexadecimal (ej: '#FFFB1C')
    """
    # Primero intentar obtener directamente del diccionario de colores
    colores = asignar_colores_categorias_gastos()
    nombre_lower = nombre_color_o_categoria.lower().strip()
    
    # Si está en el diccionario, retornar directamente
    if nombre_lower in colores:
        return colores[nombre_lower]
    
    # Si no, usar la función que procesa categorías
    item_procesado = asignar_iconos_y_colores_categorias_gastos([
        {"categoria": nombre_lower}
    ])
    
    return item_procesado[0].get("color", colores.get('otro', '#9CA3AF'))


def get_or_create_icono(nombre_categoria):
    """
    Obtiene o crea un Icono usando la lógica de calculations.py
    
    Args:
        nombre_categoria: str - Nombre que identifica el ícono (ej: 'comida')
    
    Returns:
        Icono - Instancia del modelo Icono
    """
    # Obtener la clase del ícono usando la función existente
    icon_class = get_icon_class_from_name(nombre_categoria)
    
    # Obtener o crear el ícono en la BD
    icono, created = Icono.objects.get_or_create(
        icono=icon_class,
        defaults={
            'nombre': nombre_categoria.capitalize()
        }
    )
    
    if created:
        print(f"✅ Ícono creado: {icono.nombre} - {icono.icono}")
    
    return icono


def get_or_create_color(nombre_color):
    """
    Obtiene o crea un Color usando la lógica de calculations.py
    
    Args:
        nombre_color: str - Nombre del color (ej: 'amarillo', 'azul')
    
    Returns:
        Color - Instancia del modelo Color
    """
    # Obtener el código hex usando la función existente
    codigo_hex = get_color_hex_from_name(nombre_color)
    
    nombre_lower = nombre_color.lower().strip()
    
    # Obtener o crear el color en la BD
    color, created = Color.objects.get_or_create(
        nombre=nombre_lower,
        defaults={
            'codigo_hex': codigo_hex
        }
    )
    
    if created:
        print(f"✅ Color creado: {color.nombre} - {color.codigo_hex}")
    
    return color




def initialize_default_colors_and_icons():
    """
    Inicializa los colores e íconos predeterminados usando calculations.py
    Se ejecuta automáticamente la primera vez que se carga el formulario.
    """
    # Obtener colores desde la función existente
    colores_dict = asignar_colores_categorias_gastos()
    
    for nombre, hex_code in colores_dict.items():
        Color.objects.get_or_create(
            nombre=nombre,
            defaults={'codigo_hex': hex_code}
        )
    
    # Lista de categorías comunes para generar íconos
    categorias_comunes = [
        'comida', 'transporte', 'hogar', 'entretenimiento', 
        'gimnasio', 'viaje', 'educación', 'salud', 
        'mascotas', 'regalo', 'compras', 'servicios', 'ocio'
    ]
    
    for categoria in categorias_comunes:
        icon_class = get_icon_class_from_name(categoria)
        Icono.objects.get_or_create(
            icono=icon_class,
            defaults={'nombre': categoria.capitalize()}
        )