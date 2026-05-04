def descripcion_resumida(obj):
    """Devuelve los primeros 30 caracteres de una descripción."""
    if obj.descripcion:
        return obj.descripcion[:30] + ('...' if len(obj.descripcion) > 30 else '')
    return '-'

# Nombre visible en el admin
descripcion_resumida.short_description = "Descripción"