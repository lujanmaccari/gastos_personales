from apps.ingreso.models import Fuente  

def moneda_actual(request):
    if request.user.is_authenticated and hasattr(request.user, "moneda") and request.user.moneda:
        return {
            "MONEDA_ACTUAL": request.user.moneda,
        }
    return {
        "MONEDA_ACTUAL": None,
    }

# tiene siempre la moneda en todos los templates


def fuentes_ingreso(request):
    if request.user.is_authenticated:
        return {"FUENTES_INGRESO": Fuente.objects.all()}
    return {"FUENTES_INGRESO": []}

# y este retorna todas las fuentes de ingreso del usuario logueado

# es una función q inserta datos
#  automáticamente en TODOS los templates de django, 
# los va a detectar solo si están en 
# este archivo.
# expone la moneda seleccionada 
# por el usuario a todas las plantillas
# creado para no interferir tocando tras apps