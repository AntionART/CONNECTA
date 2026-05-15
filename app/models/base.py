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

    [GUÍA 9 - ACTIVIDAD 1] Patrón Template Method: find_by_id delega la
    construcción del objeto a from_db(), que cada subclase implementa.
    """

    # [GUÍA 9 - ACTIVIDAD 1] from_db por defecto — retorna el dict crudo de MongoDB.
    # Las subclases (Pet, Appointment, Conversation) lo sobreescriben para retornar
    # una instancia tipada. Modelos auxiliares (Label) usan este default.
    @classmethod
    def from_db(cls, document: dict):
        """Construye un objeto desde un documento MongoDB. Override en subclases."""
        return document

    @classmethod
    def find_by_id(cls, doc_id):
        # [GUÍA 9 - ACTIVIDAD 1] Delega la construcción al from_db de la subclase;
        # Pet.find_by_id() retorna Pet, Appointment.find_by_id() retorna Appointment, etc.
        doc = mongo.db[cls.COLLECTION].find_one({'_id': ObjectId(doc_id)})
        return cls.from_db(doc) if doc else None

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
