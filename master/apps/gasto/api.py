from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Q
from .models import Gasto
from apps.ingreso.models import Ingreso
from .schemas import (
    GastoCreateSchema,
    GastoUpdateSchema,
    GastoOutSchema,
    GastoTotalSchema,
    SaldoSchema
)
from api.auth import session_auth

# Crear router para gastos
router = Router(tags=["Gastos"])

# ==================== ENDPOINTS DE GASTOS ====================

@router.get("/", response=List[GastoOutSchema], auth=session_auth)
def listar_gastos(
    request,
    categoria: int = None,
    fecha: str = None,
    year: int = None,
    search: str = None,
    ordering: str = "-fecha"
):
    """
    Lista todos los gastos del usuario autenticado.
    
    Parámetros de consulta:
    - categoria: Filtrar por ID de categoría
    - fecha: Filtrar por fecha exacta (formato: YYYY-MM-DD)
    - year: Filtrar por año
    - search: Buscar en descripción
    - ordering: Ordenar resultados (fecha, -fecha, monto, -monto)
    """
    queryset = Gasto.objects.filter(usuario=request.user).select_related(
        'categoria', 'moneda', 'usuario'
    )
    
    # Aplicar filtros
    if categoria:
        queryset = queryset.filter(categoria_id=categoria)
    
    if fecha:
        queryset = queryset.filter(fecha=fecha)
    
    if year:
        queryset = queryset.filter(fecha__year=year)
    
    if search:
        queryset = queryset.filter(
            Q(descripcion__icontains=search) | 
            Q(categoria__nombre__icontains=search)
        )
    
    # Aplicar ordenamiento
    queryset = queryset.order_by(ordering)
    
    return list(queryset)


@router.get("/{gasto_id}", response=GastoOutSchema, auth=session_auth)
def obtener_gasto(request, gasto_id: int):
    """
    Obtiene el detalle de un gasto específico.
    Solo si pertenece al usuario autenticado.
    """
    gasto = get_object_or_404(
        Gasto,
        id=gasto_id,
        usuario=request.user
    )
    return gasto


@router.post("/", response=GastoOutSchema, auth=session_auth)
def crear_gasto(request, payload: GastoCreateSchema):
    """
    Crea un nuevo gasto para el usuario autenticado.
    El usuario y la moneda se asignan automáticamente.
    """
    gasto = Gasto.objects.create(
        usuario=request.user,
        categoria_id=payload.categoria,
        fecha=payload.fecha,
        monto=payload.monto,
        descripcion=payload.descripcion,
        moneda=request.user.moneda
    )
    return gasto


@router.put("/{gasto_id}", response=GastoOutSchema, auth=session_auth)
def actualizar_gasto(request, gasto_id: int, payload: GastoUpdateSchema):
    """
    Actualiza un gasto existente.
    Solo si pertenece al usuario autenticado.
    """
    gasto = get_object_or_404(
        Gasto,
        id=gasto_id,
        usuario=request.user
    )
    
    # Actualizar campos proporcionados
    if payload.categoria is not None:
        gasto.categoria_id = payload.categoria
    if payload.fecha is not None:
        gasto.fecha = payload.fecha
    if payload.monto is not None:
        gasto.monto = payload.monto
    if payload.descripcion is not None:
        gasto.descripcion = payload.descripcion
    
    gasto.save()
    return gasto


@router.patch("/{gasto_id}", response=GastoOutSchema, auth=session_auth)
def actualizar_parcial_gasto(request, gasto_id: int, payload: GastoUpdateSchema):
    """
    Actualización parcial de un gasto.
    """
    return actualizar_gasto(request, gasto_id, payload)


@router.delete("/{gasto_id}", auth=session_auth)
def eliminar_gasto(request, gasto_id: int):
    """
    Elimina un gasto existente.
    Solo si pertenece al usuario autenticado.
    """
    gasto = get_object_or_404(
        Gasto,
        id=gasto_id,
        usuario=request.user
    )
    gasto.delete()
    return {"success": True, "message": "Gasto eliminado correctamente"}


@router.get("/estadisticas/total", response=GastoTotalSchema, auth=session_auth)
def total_gastos(request):
    """
    Calcula el total de gastos del usuario autenticado.
    """
    resultado = Gasto.objects.filter(usuario=request.user).aggregate(
        total=Sum('monto')
    )
    
    cantidad = Gasto.objects.filter(usuario=request.user).count()
    
    return {
        'total': float(resultado['total'] or 0),
        'cantidad': cantidad,
        'moneda': request.user.moneda.abreviatura if request.user.moneda else None
    }


@router.get("/estadisticas/saldo", response=SaldoSchema, auth=session_auth)
def calcular_saldo(request):
    """
    Calcula el saldo restante: Total Ingresos - Total Gastos.
    Este es uno de los endpoints más importantes del sistema.
    """
    # Calcular total de ingresos
    total_ingresos = Ingreso.objects.filter(usuario=request.user).aggregate(
        total=Sum('monto')
    )['total'] or 0
    
    # Calcular total de gastos
    total_gastos = Gasto.objects.filter(usuario=request.user).aggregate(
        total=Sum('monto')
    )['total'] or 0
    
    # Calcular saldo
    saldo = total_ingresos - total_gastos
    
    return {
        'total_ingresos': float(total_ingresos),
        'total_gastos': float(total_gastos),
        'saldo_restante': float(saldo),
        'moneda': request.user.moneda.abreviatura if request.user.moneda else None
    }