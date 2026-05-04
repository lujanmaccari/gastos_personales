from ninja import Schema
from datetime import date
from typing import Optional
from decimal import Decimal

# Schema para CREAR un ingreso (input)
class IngresoCreateSchema(Schema):
    fuente: int  # ID de la fuente
    fecha: date
    monto: Decimal
    descripcion: Optional[str] = None

# Schema para ACTUALIZAR un ingreso (input)
class IngresoUpdateSchema(Schema):
    fuente: Optional[int] = None
    fecha: Optional[date] = None
    monto: Optional[Decimal] = None
    descripcion: Optional[str] = None

# Schema para MOSTRAR un ingreso (output)
class IngresoOutSchema(Schema):
    id: int
    usuario_id: int
    usuario_username: str
    fuente_id: int
    fuente_nombre: str
    moneda_abreviatura: Optional[str] = None
    fecha: date
    monto: Decimal
    descripcion: Optional[str] = None
    
    @staticmethod
    def resolve_usuario_username(obj):
        return obj.usuario.username
    
    @staticmethod
    def resolve_fuente_id(obj):
        return obj.fuente.id
    
    @staticmethod
    def resolve_fuente_nombre(obj):
        return obj.fuente.nombre
    
    @staticmethod
    def resolve_moneda_abreviatura(obj):
        return obj.moneda.abreviatura if obj.moneda else None

# Schema para el total de ingresos
class IngresoTotalSchema(Schema):
    total: float
    cantidad: int
    moneda: Optional[str] = None

# Schema para Fuente (output)
class FuenteOutSchema(Schema):
    id: int
    nombre: str