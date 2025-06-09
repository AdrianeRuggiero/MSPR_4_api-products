"""Point d'entrée principal de l'API Products avec monitoring Prometheus."""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.routes import products

app = FastAPI(
    title="Products API",
    version="1.0.0",
    description="API de gestion des produits pour PayeTonKawa"
)

# Monitoring Prometheus
Instrumentator().instrument(app).expose(app)

@app.get("/")
def root():
    """Message de bienvenue"""
    return {"msg": "Bienvenue sur l'API Products"}

# Inclusion des routes produits
app.include_router(products.router, prefix="/products", tags=["products"])
