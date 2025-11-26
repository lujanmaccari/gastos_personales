from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from .models import Categoria , Icono, Color
from .schemas import (
    CategoriaCreateSchema,
    CategoriaUpdateSchema,
    CategoriaOutSchema
)
from api.auth import session_auth
from api.auth import AuthBearer
from typing import Optional
from typing import Optional, List, Dict, Any
from math import ceil
from .schemas import CategoriaPaginatedResponse

router = Router(tags=["Categorias"])


# ==================== LISTAR ====================
@router.get("/", response=CategoriaPaginatedResponse, auth=[session_auth, AuthBearer()])
def listar_categorias(
    request,
    nombre: Optional[str] = None,
    icono: Optional[str] = None,
    color: Optional[str] = None,
    pageIndex: int = 0,
    pageSize: int = 10
):
    queryset = Categoria.objects.filter(usuario=request.user).select_related(
        "icono", "color"
    )

    if nombre:
        queryset = queryset.filter(nombre__icontains=nombre)

    if icono:
        queryset = queryset.filter(icono__icono__icontains=icono)

    if color:
        queryset = queryset.filter(color__nombre__icontains=color)

    total = queryset.count()

    start = pageIndex * pageSize
    end = start + pageSize
    queryset = queryset[start:end]

    items = [
        CategoriaOutSchema(
            id=c.id,
            nombre=c.nombre,
            icono=c.icono.icono if c.icono else None,
            color=c.color.nombre if c.color else None
        )
        for c in queryset
    ]

    return {
        "items": items,
        "total": total,
        "totalPages": (total // pageSize) + (1 if total % pageSize else 0),
        "pageIndex": pageIndex,
        "pageSize": pageSize
    }


# ==================== OBTENER DETALLE ====================
@router.get("/{categoria_id}", response=CategoriaOutSchema, auth=[session_auth, AuthBearer()])
def obtener_categoria(request, categoria_id: int):
    """
    Obtiene una categoría específica del usuario autenticado.
    """
    categoria = Categoria.objects.get(id=categoria_id, usuario=request.user)

    return {
        "id": categoria.id,
        "nombre": categoria.nombre,
        "icono": categoria.icono.icono if categoria.icono else None,         
        "color": categoria.color.codigo_hex if categoria.color else None
    }


# ==================== CREAR ====================
@router.post("/", response=CategoriaOutSchema, auth=[session_auth, AuthBearer()])
def crear_categoria(request, payload: CategoriaCreateSchema):
    """
    Crea una categoría y sus relaciones (icono y color).
    Si el icono o el color ya existen, los reutiliza.
    """

    icono_obj, _ = Icono.objects.get_or_create(
        icono=payload.icono
    )

    color_obj, _ = Color.objects.get_or_create(
        nombre=payload.color_nombre,
        defaults={"codigo_hex": payload.color_hex}
    )

    if color_obj.codigo_hex != payload.color_hex:
        color_obj.codigo_hex = payload.color_hex
        color_obj.save()

    categoria = Categoria.objects.create(
        usuario=request.user,
        nombre=payload.nombre,
        icono=icono_obj,
        color=color_obj
    )

    return {
        "id": categoria.id,
        "nombre": categoria.nombre,
        "icono": categoria.icono.icono,
        "color": categoria.color.codigo_hex
    }



# ==================== ACTUALIZAR ====================
@router.put("/{categoria_id}", response=CategoriaOutSchema, auth=[session_auth, AuthBearer()])
def actualizar_categoria(request, categoria_id: int, payload: CategoriaUpdateSchema):
    """
    Actualiza una categoría existente del usuario autenticado.
    """
    categoria = get_object_or_404(
        Categoria,
        id=categoria_id,
        usuario=request.user
    )

    if payload.nombre is not None:
        categoria.nombre = payload.nombre

    if payload.icono is not None:
        try:
            icono = Icono.objects.get(icono=payload.icono)
            categoria.icono = icono
        except Icono.DoesNotExist:
            pass  

    if payload.color_nombre is not None and payload.color_hex is not None:
        color, _ = Color.objects.get_or_create(
            nombre=payload.color_nombre,
            defaults={"codigo_hex": payload.color_hex}
        )
        categoria.color = color

    categoria.save()

    return {
        "id": categoria.id,
        "nombre": categoria.nombre,
        "icono": categoria.icono.icono,
        "color": categoria.color.codigo_hex
    }



# ==================== ELIMINAR ====================
@router.delete("/{categoria_id}", auth=[session_auth, AuthBearer()])
def eliminar_categoria(request, categoria_id: int):
    """
    Elimina una categoría del usuario autenticado.
    """
    categoria = get_object_or_404(
        Categoria,
        id=categoria_id,
        usuario=request.user
    )
    categoria.delete()
    return {"success": True, "message": "Categoría eliminada correctamente"}
