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

    # Dynamic Input: Receives pet attributes from API request (name, species,
    # breed, age_years, weight_kg, owner_phone, owner_name).
    @staticmethod
    def create(name, species, breed, age_years, weight_kg, owner_phone, owner_name=''):
        # Business Rule: owner_phone links pet to WhatsApp conversations.
        # This field must match a conversation's phone_number to associate
        # the pet with its owner's chat thread.
        doc = {
            'name': name,
            'species': species,
            'breed': breed,
            'age_years': age_years,
            'weight_kg': weight_kg,
            'owner_phone': owner_phone,
            'owner_name': owner_name,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        result = mongo.db[Pet.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    @staticmethod
    def find_by_id(pet_id):
        return mongo.db[Pet.COLLECTION].find_one({'_id': ObjectId(pet_id)})

    # List: Returns array of pets matching the phone number.
    # Concept Validation: Phone number is the foreign key linking pets
    # to conversations — all pets sharing an owner_phone belong to the
    # same WhatsApp contact.
    @staticmethod
    def find_by_owner_phone(phone):
        return list(mongo.db[Pet.COLLECTION].find({'owner_phone': phone}))

    # Professional Output: Returns all pets sorted by creation date descending
    # (newest first), suitable for rendering in admin/dashboard views.
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
