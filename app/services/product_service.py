from typing import List, Optional
from app.models.product import ProductModel, PyObjectId
from app.db.mongo import products_collection
from bson import ObjectId
from app.messaging.rabbitmq import publish_product_created

# Créer un nouveau produit
def create_product(product: ProductModel) -> ProductModel:
    product_dict = product.model_dump(by_alias=True, exclude_unset=True)
    result = products_collection.insert_one(product_dict)
    product_dict["_id"] = str(result.inserted_id)
    publish_product_created(product_dict)
    return ProductModel(**product_dict)


# Obtenir un produit par ID
def get_product(product_id: str) -> Optional[ProductModel]:
    if not ObjectId.is_valid(product_id):
        return None
    data = products_collection.find_one({"_id": ObjectId(product_id)})
    if data:
        data["_id"] = str(data["_id"])
        return ProductModel(**data)
    return None

# Lister tous les produits
def list_products() -> List[ProductModel]:
    products = []
    for doc in products_collection.find():
        doc["_id"] = str(doc["_id"])
        products.append(ProductModel(**doc))
    return products

# Mettre à jour un produit
def update_product(product_id: str, product: ProductModel) -> Optional[ProductModel]:
    if not ObjectId.is_valid(product_id):
        return None
    update_data = product.model_dump(by_alias=True, exclude_unset=True)
    updated = products_collection.find_one_and_update(
        {"_id": ObjectId(product_id)},
        {"$set": update_data},
        return_document=True
    )
    if updated:
        updated["_id"] = str(updated["_id"])
        return ProductModel(**updated)
    return None

# Supprimer un produit
def delete_product(product_id: str) -> bool:
    if not ObjectId.is_valid(product_id):
        return False
    result = products_collection.delete_one({"_id": ObjectId(product_id)})
    return result.deleted_count == 1
