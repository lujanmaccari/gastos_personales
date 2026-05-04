from ninja import Schema
from datetime import date
from typing import Optional
from decimal import Decimal

# Schema para CREAR un gasto (input)
class GastoCreateSchema(Schema):
    categoria: int  # ID de la categoría
    fecha: date
    monto: Decimal
    descripcion: Optional[str] = None

# Schema para ACTUALIZAR un gasto (input)
class GastoUpdateSchema(Schema):
    categoria: Optional[int] = None
    fecha: Optional[date] = None
    monto: Optional[Decimal] = None
    descripcion: Optional[str] = None

# Schema para MOSTRAR un gasto (output)
class GastoOutSchema(Schema):
    id: int
    usuario_id: int
    usuario_username: str
    categoria_id: int
    categoria_nombre: str
    moneda_abreviatura: Optional[str] = None
    fecha: date
    monto: Decimal
    descripcion: Optional[str] = None
    
    @staticmethod
    def resolve_usuario_username(obj):
        return obj.usuario.username
    
    @staticmethod
    def resolve_categoria_id(obj):
        return obj.categoria.id
    
    @staticmethod
    def resolve_categoria_nombre(obj):
        return obj.categoria.nombre
    
    @staticmethod
    def resolve_moneda_abreviatura(obj):
        return obj.moneda.abreviatura if obj.moneda else None

# Schema para el total de gastos
class GastoTotalSchema(Schema):
    total: float
    cantidad: int
    moneda: Optional[str] = None

# Schema para el cálculo de saldo
class SaldoSchema(Schema):
    total_ingresos: float
    total_gastos: float
    saldo_restante: float
    moneda: Optional[str] = None