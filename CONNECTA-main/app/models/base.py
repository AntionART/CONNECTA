"""
BaseModel — métodos CRUD genéricos compartidos por todos los modelos MongoDB.
"""
from app.extensions import mongo
from datetime import datetime, timezone
from bson import ObjectId


class BaseModel:
    """
    Mixin con operaciones CRUD comunes para colecciones MongoDB.
    Las subclases deben definir COLLECTION = 'nombre_coleccion'.
    """

    @classmethod
    def find_by_id(cls, doc_id):
        return mongo.db[cls.COLLECTION].find_one({'_id': ObjectId(doc_id)})

    @classmethod
    def update(cls, doc_id, data):
        data['updated_at'] = datetime.now(timezone.utc)
        mongo.db[cls.COLLECTION].update_one(
            {'_id': ObjectId(doc_id)},
            {'$set': data},
        )

    @classmethod
    def delete(cls, doc_id):
        mongo.db[cls.COLLECTION].delete_one({'_id': ObjectId(doc_id)})
