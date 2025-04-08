from sqlalchemy import Column, Integer, String, Text, Float, Enum, DateTime
from sqlalchemy.sql import func
from database import Base
from enum import Enum as PyEnum

class ProductCategory(str, PyEnum):
    ROPA = "ropa"
    ACCESORIOS = "accesorios"
    COLECCIONABLES = "coleccionables"
    NOVELAS_GRAFICAS = "novelas_graficas"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    stock_actual = Column(Integer, nullable=False)
    costo_por_unidad = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    categoria = Column(Enum(ProductCategory), nullable=False)
    proveedores = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())