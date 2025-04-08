from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProductCategory(str, Enum):
    ropa = "ropa"
    accesorios = "accesorios"
    coleccionables = "coleccionables"
    novelas_graficas = "novelas_graficas"

class ProductBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    descripcion: str = Field(None, max_length=500)
    stock_actual: int = Field(..., ge=0)
    costo_por_unidad: float = Field(..., gt=0)
    precio_venta: float = Field(..., gt=0)
    categoria: ProductCategory
    proveedores: str = Field(..., max_length=200)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    stock_actual: Optional[int] = Field(None, ge=0)
    costo_por_unidad: Optional[float] = Field(None, gt=0)
    precio_venta: Optional[float] = Field(None, gt=0)
    categoria: Optional[ProductCategory] = None
    proveedores: Optional[str] = Field(None, max_length=200)

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserOrderRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Cantidad debe ser mayor a 0")

class SupplierOrderRequest(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Cantidad debe ser mayor a 0")