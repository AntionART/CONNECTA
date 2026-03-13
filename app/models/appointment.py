"""
Appointment Model — Tracks Veterinary Visits.

Appointments represent scheduled, confirmed, completed, or cancelled
veterinary visits. Each appointment is linked to a pet via pet_id
and records the date, reason, and assigned veterinarian.

MVP Integration: Appointments connect the CRM's scheduling features
with pets and, transitively, with their owners' WhatsApp conversations.
"""

from app.extensions import mongo
from datetime import datetime, timezone
from bson import ObjectId


class Appointment:
    COLLECTION = 'appointments'

    # List: STATUSES is a constant list defining valid appointment states.
    # Used for validation and filtering — appointments transition through
    # these states: scheduled -> confirmed -> completed (or cancelled).
    STATUSES = ['scheduled', 'confirmed', 'completed', 'cancelled']

    # Business Rule: New appointments default to 'scheduled' status.
    # The status can later be updated to 'confirmed', 'completed', or
    # 'cancelled' as the appointment lifecycle progresses.
    @staticmethod
    def create(pet_id, date, reason, veterinarian=''):
        doc = {
            'pet_id': ObjectId(pet_id),
            'date': date,
            'reason': reason,
            'veterinarian': veterinarian,
            'status': 'scheduled',
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        result = mongo.db[Appointment.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    @staticmethod
    def find_by_id(appointment_id):
        return mongo.db[Appointment.COLLECTION].find_one(
            {'_id': ObjectId(appointment_id)}
        )

    # List: Returns array of appointments for a specific pet,
    # sorted by date descending (most recent first).
    @staticmethod
    def find_by_pet(pet_id):
        return list(
            mongo.db[Appointment.COLLECTION]
            .find({'pet_id': ObjectId(pet_id)})
            .sort('date', -1)
        )

    @staticmethod
    def list_all(status=None):
        query = {}
        if status:
            query['status'] = status
        return list(
            mongo.db[Appointment.COLLECTION].find(query).sort('date', 1)
        )

    @staticmethod
    def list_today():
        # Arithmetic Logic: Calculates today's date range (00:00:00 to
        # 23:59:59) by replacing time components of the current UTC datetime.
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        # Nested Logic: MongoDB query uses $gte and $lte for date range
        # filtering. This nested dict becomes a BSON query operator that
        # selects documents where 'date' falls within today's boundaries.
        return list(
            mongo.db[Appointment.COLLECTION].find({
                'date': {'$gte': today_start, '$lte': today_end}
            }).sort('date', 1)
        )

    @staticmethod
    def update(appointment_id, data):
        data['updated_at'] = datetime.now(timezone.utc)
        mongo.db[Appointment.COLLECTION].update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': data},
        )

    @staticmethod
    def delete(appointment_id):
        mongo.db[Appointment.COLLECTION].delete_one(
            {'_id': ObjectId(appointment_id)}
        )


def init_appointment_indexes():
    mongo.db[Appointment.COLLECTION].create_index('pet_id')
    mongo.db[Appointment.COLLECTION].create_index('date')
    mongo.db[Appointment.COLLECTION].create_index('status')
