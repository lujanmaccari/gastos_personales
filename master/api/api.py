from ninja import NinjaAPI
from apps.ingreso.api import router as ingreso_router
from apps.gasto.api import router as gasto_router
from apps.categoria.api import router as categoria_router
from .auth import AuthBearer

# Crear la instancia principal de la API
api = NinjaAPI(
    title="API Gestión de Gastos Personales",
    version="1.0.0",
    description="API RESTful para gestionar gastos personales",
    docs_url="/docs",  # Swagger UI en /api/docs
    auth=AuthBearer()
)

# Registrar los routers de cada modulo
api.add_router("/ingresos", ingreso_router)
api.add_router("/gastos", gasto_router)
api.add_router("/categorias", categoria_router)

@api.get("/health")
def health_check(request):
    """Endpoint para verificar que la API está funcionando"""
    return {"status": "ok", "message": "API funcionando correctamente"}