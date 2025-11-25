from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from .models import Ingreso, Fuente
from .schemas import (
    IngresoCreateSchema, 
    IngresoUpdateSchema, 
    IngresoOutSchema,
    IngresoTotalSchema,
    FuenteOutSchema
)
from api.auth import session_auth
from api.auth import AuthBearer

# Crear router para ingresos
router = Router(tags=["Ingresos"])

# ==================== ENDPOINTS DE INGRESOS ====================

@router.get("/", response=List[IngresoOutSchema], auth=[session_auth, AuthBearer()])
def listar_ingresos(
    request,
    fuente: int = None,
    fecha: str = None,
    search: str = None,
    ordering: str = "-fecha"
):
    """
    Lista todos los ingresos del usuario autenticado.
    
    Parámetros de consulta:
    - fuente: Filtrar por ID de fuente
    - fecha: Filtrar por fecha exacta (formato: YYYY-MM-DD)
    - search: Buscar en descripción
    - ordering: Ordenar resultados (fecha, -fecha, monto, -monto)
    """
    queryset = Ingreso.objects.filter(usuario=request.user).select_related(
        'fuente', 'moneda', 'usuario'
    )
    
    # Aplicar filtros
    if fuente:
        queryset = queryset.filter(fuente_id=fuente)
    
    if fecha:
        queryset = queryset.filter(fecha=fecha)
    
    if search:
        queryset = queryset.filter(
            Q(descripcion__icontains=search) | 
            Q(fuente__nombre__icontains=search)
        )
    
    # Aplicar ordenamiento
    queryset = queryset.order_by(ordering)
    
    return list(queryset)


@router.get("/{ingreso_id}", response=IngresoOutSchema, auth=[session_auth, AuthBearer()])
def obtener_ingreso(request, ingreso_id: int):
    """
    Obtiene el detalle de un ingreso específico.
    Solo si pertenece al usuario autenticado.
    """
    ingreso = get_object_or_404(
        Ingreso, 
        id=ingreso_id, 
        usuario=request.user
    )
    return ingreso


@router.post("/", response=IngresoOutSchema, auth=[session_auth, AuthBearer()])
def crear_ingreso(request, payload: IngresoCreateSchema):
    """
    Crea un nuevo ingreso para el usuario autenticado.
    El usuario y la moneda se asignan automáticamente.
    """
    # Crear el ingreso
    ingreso = Ingreso.objects.create(
        usuario=request.user,
        fuente_id=payload.fuente,
        fecha=payload.fecha,
        monto=payload.monto,
        descripcion=payload.descripcion,
        moneda=request.user.moneda  # Asignar moneda del usuario
    )
    return ingreso


@router.put("/{ingreso_id}", response=IngresoOutSchema, auth=[session_auth, AuthBearer()])
def actualizar_ingreso(request, ingreso_id: int, payload: IngresoUpdateSchema):
    """
    Actualiza un ingreso existente.
    Solo si pertenece al usuario autenticado.
    """
    ingreso = get_object_or_404(
        Ingreso, 
        id=ingreso_id, 
        usuario=request.user
    )
    
    # Actualizar campos proporcionados
    if payload.fuente is not None:
        ingreso.fuente_id = payload.fuente
    if payload.fecha is not None:
        ingreso.fecha = payload.fecha
    if payload.monto is not None:
        ingreso.monto = payload.monto
    if payload.descripcion is not None:
        ingreso.descripcion = payload.descripcion
    
    ingreso.save()
    return ingreso


@router.patch("/{ingreso_id}", response=IngresoOutSchema, auth=[session_auth, AuthBearer()])
def actualizar_parcial_ingreso(request, ingreso_id: int, payload: IngresoUpdateSchema):
    """
    Actualización parcial de un ingreso (igual que PUT pero semánticamente diferente).
    """
    return actualizar_ingreso(request, ingreso_id, payload)


@router.delete("/{ingreso_id}", auth=[session_auth, AuthBearer()])
def eliminar_ingreso(request, ingreso_id: int):
    """
    Elimina un ingreso existente.
    Solo si pertenece al usuario autenticado.
    """
    ingreso = get_object_or_404(
        Ingreso, 
        id=ingreso_id, 
        usuario=request.user
    )
    ingreso.delete()
    return {"success": True, "message": "Ingreso eliminado correctamente"}


@router.get("/estadisticas/total", response=IngresoTotalSchema, auth=[session_auth, AuthBearer()])
def total_ingresos(request):
    """
    Calcula el total de ingresos del usuario autenticado.
    """
    resultado = Ingreso.objects.filter(usuario=request.user).aggregate(
        total=Sum('monto')
    )
    
    cantidad = Ingreso.objects.filter(usuario=request.user).count()
    
    return {
        'total': float(resultado['total'] or 0),
        'cantidad': cantidad,
        'moneda': request.user.moneda.abreviatura if request.user.moneda else None
    }


# ==================== ENDPOINTS DE FUENTES ====================

@router.get("/fuentes/", response=List[FuenteOutSchema], auth=[session_auth, AuthBearer()])
def listar_fuentes(request):
    """
    Lista todas las fuentes de ingreso disponibles.
    """
    return list(Fuente.objects.all())


@router.get("/fuentes/{fuente_id}", response=FuenteOutSchema, auth=[session_auth, AuthBearer()])
def obtener_fuente(request, fuente_id: int):
    """
    Obtiene el detalle de una fuente específica.
    """
    fuente = get_object_or_404(Fuente, id=fuente_id)
    return fuente