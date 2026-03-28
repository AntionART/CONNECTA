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

    # [GUÍA 6 - ACTIVIDAD 1] Vector (lista 1D) de estados válidos
    # Uso en CONNECTA: STATUSES es un vector constante que define el ciclo de vida
    # de una cita; se usa para validación y filtrado en queries MongoDB
    # Ejemplo: STATUSES[0] == 'scheduled', STATUSES[-1] == 'cancelled'
    STATUSES = ['scheduled', 'confirmed', 'completed', 'cancelled']

    # [GUÍA 2 - ACTIVIDAD 1] Tipos de variables en parámetros del modelo
    # Uso en CONNECTA: pet_id es str (ObjectId serializado), date es datetime,
    # reason es str (texto del motivo), veterinarian es str (nombre del vet)
    # Ejemplo: Appointment.create('64abc...', datetime(2025,3,27,10,0), 'Vacunación', 'Dr. López')
    @staticmethod
    def create(pet_id, date, reason, veterinarian=''):
        doc = {
            'pet_id': ObjectId(pet_id),
            'date': date,
            'reason': reason,          # str — motivo de la cita
            'veterinarian': veterinarian,  # str — nombre del veterinario
            'status': 'scheduled',     # str — estado inicial del ciclo de vida
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

    # [GUÍA 2 - ACTIVIDAD 3] Lista como resultado de consulta por mascota
    # Uso en CONNECTA: Retorna el historial de citas de una mascota como lista Python,
    # ordenado por fecha descendente (cita más reciente primero)
    # Ejemplo: find_by_pet('64abc...') → [{'date': ..., 'reason': 'Vacunación'}, ...]
    @staticmethod
    def find_by_pet(pet_id):
        return list(
            mongo.db[Appointment.COLLECTION]
            .find({'pet_id': ObjectId(pet_id)})
            .sort('date', -1)
        )

    @staticmethod
    def list_all(status=None):
        # [GUÍA 3 - ACTIVIDAD 3] Validación de parámetro opcional
        # Uso en CONNECTA: Si status es None se retornan todas las citas;
        # si se provee un valor se filtra el query — evita errores de query vacío
        # Ejemplo: list_all('scheduled') → solo citas pendientes
        query = {}
        if status:
            query['status'] = status
        return list(
            mongo.db[Appointment.COLLECTION].find(query).sort('date', 1)
        )

    @staticmethod
    def list_today():
        # [GUÍA 2 - ACTIVIDAD 4] Operadores aritméticos — cálculo de rango de fechas
        # Uso en CONNECTA: .replace() ajusta horas del datetime actual para obtener
        # inicio (00:00:00) y fin (23:59:59) del día de hoy en UTC
        # Ejemplo: today_start = datetime(2025,3,27,0,0,0), today_end = datetime(2025,3,27,23,59,59)
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        # [GUÍA 3 - ACTIVIDAD 1] if implícito en query MongoDB — $gte y $lte
        # Uso en CONNECTA: El dict anidado {'$gte': today_start, '$lte': today_end}
        # es el equivalente MongoDB de: if today_start <= date <= today_end
        # Ejemplo: {'date': {'$gte': 2025-03-27T00:00:00Z, '$lte': 2025-03-27T23:59:59Z}}
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
