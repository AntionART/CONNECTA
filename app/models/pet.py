"""
Pet Model — Linked to Owners via Phone Number.

Pets represent the animals registered in the veterinary CRM. Each pet
is linked to its owner through the owner_phone field, which matches
the phone_number in the conversations collection.

Concept Validation: The phone number serves as a natural foreign key
between pets and conversations, avoiding the need for a separate
owners collection in the MVP.

Bilingualism: Code in English; pet names and owner names may be in
any language as entered by the user.
"""

from app.extensions import mongo
from datetime import datetime, timezone
from bson import ObjectId


class Pet:
    COLLECTION = 'pets'

    # [GUÍA 2 - ACTIVIDAD 1] Declaración de tipos de variables en parámetros
    # Uso en CONNECTA: name y species son str (texto libre del usuario),
    # age_years es float (puede ser 1.5 años), weight_kg es float (ej: 4.2 kg),
    # owner_phone es str (número WhatsApp como '573001234567')
    # Ejemplo: Pet.create('Luna', 'Perro', 'Labrador', 2.5, 18.3, '573001234567')
    @staticmethod
    def create(name, species, breed, age_years, weight_kg, owner_phone, owner_name=''):
        # [GUÍA 2 - ACTIVIDAD 1] Variables con tipos explícitos en el documento MongoDB
        # Uso en CONNECTA: age_years (float) y weight_kg (float) permiten decimales
        # para representar '6 meses' como 0.5 o '4.2 kg' con precisión decimal
        # Ejemplo: {'age_years': 2.5, 'weight_kg': 18.3, 'name': 'Luna', 'species': 'Perro'}
        doc = {
            'name': name,            # str — nombre de la mascota
            'species': species,      # str — especie (Perro, Gato, etc.)
            'breed': breed,          # str — raza
            'age_years': age_years,  # float — edad en años (ej: 0.5 = 6 meses)
            'weight_kg': weight_kg,  # float — peso en kilogramos
            'owner_phone': owner_phone,  # str — teléfono WhatsApp del dueño
            'owner_name': owner_name,    # str — nombre del dueño
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        result = mongo.db[Pet.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    @staticmethod
    def find_by_id(pet_id):
        return mongo.db[Pet.COLLECTION].find_one({'_id': ObjectId(pet_id)})

    # [GUÍA 2 - ACTIVIDAD 3] Lista como resultado de consulta
    # Uso en CONNECTA: list() convierte el cursor MongoDB en una lista Python;
    # phone_number actúa como FK hacia conversations para vincular mascota con chat
    # Ejemplo: find_by_owner_phone('573001234567') → [{'name': 'Luna', ...}, {'name': 'Max', ...}]
    @staticmethod
    def find_by_owner_phone(phone):
        return list(mongo.db[Pet.COLLECTION].find({'owner_phone': phone}))

    @staticmethod
    def list_all():
        return list(mongo.db[Pet.COLLECTION].find().sort('created_at', -1))

    @staticmethod
    def update(pet_id, data):
        data['updated_at'] = datetime.now(timezone.utc)
        mongo.db[Pet.COLLECTION].update_one(
            {'_id': ObjectId(pet_id)},
            {'$set': data},
        )

    @staticmethod
    def delete(pet_id):
        mongo.db[Pet.COLLECTION].delete_one({'_id': ObjectId(pet_id)})


def init_pet_indexes():
    mongo.db[Pet.COLLECTION].create_index('owner_phone')
    mongo.db[Pet.COLLECTION].create_index('species')
