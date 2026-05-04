# schemas.py
from ninja import Schema
from pydantic import BaseModel
from typing import List, Optional

class CategoriaCreateSchema(Schema):
    nombre: str
    icono: str
    color_nombre: str
    color_hex: str


class CategoriaUpdateSchema(Schema):
    nombre: str
    icono: str
    color_nombre: str
    color_hex: str


class CategoriaOutSchema(Schema):
    id: int
    nombre: str
    icono: str | None
    color: str | None

class CategoriaPaginatedResponse(BaseModel):
    items: List[CategoriaOutSchema]
    total: int
    totalPages: int
    pageIndex: int
    pageSize: int