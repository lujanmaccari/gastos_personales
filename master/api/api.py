from ninja import NinjaAPI
from apps.ingreso.api import router as ingreso_router
from apps.gasto.api import router as gasto_router

# Crear la instancia principal de la API
api = NinjaAPI(
    title="API Gestión de Gastos Personales",
    version="1.0.0",
    description="API RESTful para gestionar gastos personales",
    docs_url="/docs"  # Swagger UI estará en /api/docs
)

# Registrar los routers de cada módulo
api.add_router("/ingresos", ingreso_router)
api.add_router("/gastos", gasto_router)

# Endpoint de prueba
@api.get("/health")
def health_check(request):
    """Endpoint para verificar que la API está funcionando"""
    return {"status": "ok", "message": "API funcionando correctamente"}