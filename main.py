from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import Product, Base
from schemas import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    UserOrderRequest,
    SupplierOrderRequest
)
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configurar CORS para producción
allowed_origins = [
    "https://tu-frontend.com",  # Cambia por tu URL de frontend
    "http://localhost:3000",  # Para desarrollo local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint de verificación de salud
@app.get("/health")
def health_check():
    return {"status": "OK", "message": "Inventory service is running"}


# Endpoints para Productos
@app.post("/products/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@app.get("/products", response_model=list[ProductResponse])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(product)
    db.commit()
    return None


# Endpoints para gestión de stock
@app.post("/user-orders/")
def process_user_order(order: UserOrderRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if product.stock_actual < order.quantity:
        raise HTTPException(
            status_code=400,
            detail="Stock insuficiente para realizar el pedido"
        )

    product.stock_actual -= order.quantity
    db.commit()
    db.refresh(product)
    return {"message": "Pedido de usuario procesado", "nuevo_stock": product.stock_actual}


@app.post("/supplier-orders/")
def process_supplier_order(order: SupplierOrderRequest, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product.stock_actual += order.quantity
    db.commit()
    db.refresh(product)
    return {"message": "Pedido de proveedor procesado", "nuevo_stock": product.stock_actual}


# Configuración para producción
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)