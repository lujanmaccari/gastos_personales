"""
Utilidades para generar estilos CSS inline desde colores hexadecimales.
Compartido entre Gasto y Categoría.
"""

def get_badge_styles_from_hex(hex_color):
    """
    Genera estilos CSS inline para badges basándose en un color hexadecimal.
    Crea un fondo suave (15% opacidad) y texto oscurecido (75% del color original).
    
    Args:
        hex_color: str - Código hexadecimal del color (ej: '#FFFB1C')
    
    Returns:
        str - Estilos CSS inline (ej: 'background-color: rgba(...); color: rgb(...);')
    """
    hex_color = hex_color.lstrip('#')
    
    # Convertir hex a RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Fondo con 15% de opacidad
    bg_color = f"rgba({r},{g},{b},0.15)"
    
    # Texto oscurecido al 75%
    text_color = f"rgb({int(r*0.75)},{int(g*0.75)},{int(b*0.75)})"
    
    return f"background-color: {bg_color}; color: {text_color};"


def darken_hex(hex_code, factor=0.75):
    """
    Oscurece un color hexadecimal.
    
    Args:
        hex_code: str - Código hexadecimal (ej: '#FFFB1C')
        factor: float - Factor de oscurecimiento (0.0 = negro, 1.0 = sin cambio)
    
    Returns:
        str - Código hexadecimal oscurecido
    """
    hex_code = hex_code.lstrip("#")
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def rgba_from_hex(hex_code, opacity=0.15):
    """
    Convierte un color hexadecimal a RGBA con opacidad personalizada.
    
    Args:
        hex_code: str - Código hexadecimal (ej: '#FFFB1C')
        opacity: float - Nivel de opacidad (0.0 = transparente, 1.0 = opaco)
    
    Returns:
        str - Color en formato RGBA
    """
    hex_code = hex_code.lstrip("#")
    r = int(hex_code[0:2], 16)
    g = int(hex_code[2:4], 16)
    b = int(hex_code[4:6], 16)
    
    return f"rgba({r},{g},{b},{opacity})"