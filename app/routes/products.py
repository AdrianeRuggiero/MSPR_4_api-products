from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.product import ProductModel
from app.services.product_service import (
    create_product, get_product, list_products, update_product, delete_product
)
from app.security.dependencies import get_current_user, role_required

router = APIRouter()

@router.post("/", response_model=ProductModel, status_code=status.HTTP_201_CREATED)
def create(product: ProductModel, user=Depends(role_required("admin"))):
    return create_product(product)

@router.get("/", response_model=List[ProductModel], dependencies=[Depends(role_required("admin"))])
def get_all(user=Depends(get_current_user)):
    return list_products()

@router.get("/{product_id}", response_model=ProductModel)
def get_by_id(product_id: str, user=Depends(get_current_user)):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return product

@router.put("/{product_id}", response_model=ProductModel)
def update(product_id: str, product: ProductModel, user=Depends(role_required("admin"))):
    updated = update_product(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Produit non trouvé ou non modifié")
    return updated

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(product_id: str, user=Depends(role_required("admin"))):
    success = delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return
