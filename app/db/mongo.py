from pymongo import MongoClient
from app.config import settings

# Connexion au client MongoDB
client = MongoClient(settings.MONGO_URI)

# Sélection de la base de données
db = client[settings.DATABASE_NAME]

# Accès à la collection 'products'
products_collection = db["products"]
