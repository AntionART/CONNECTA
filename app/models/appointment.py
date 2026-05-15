"""
Appointment Model — Tracks Veterinary Visits.

Appointments represent scheduled, confirmed, completed, or cancelled
veterinary visits. Each appointment is linked to a pet via pet_id.

[GUÍA 9 - ACTIVIDAD 1] Modelo OOP completo: __init__, from_db, to_dict,
__str__, __repr__. El estado del ciclo de vida (_status) se encapsula
con @property y setter con validación contra STATUSES.

[GUÍA 9 - ACTIVIDAD 2] Métodos migrados desde funciones de rutas:
enriquecer_dashboard() ← _enriquecer_cita_dashboard() en dashboard.py
enriquecer_api()       ← _enrich_appointment() en appointments.py
"""

from app.extensions import mongo
from app.models.base import BaseModel
from datetime import datetime, timezone
from bson import ObjectId


class Appointment(BaseModel):
    COLLECTION = 'appointments'

    # [GUÍA 6 - ACTIVIDAD 1] Vector (lista 1D) de estados válidos del ciclo de vida
    STATUSES = ['scheduled', 'confirmed', 'completed', 'cancelled']

    # [GUÍA 9 - ACTIVIDAD 1] Constructor explícito con todos los atributos de la entidad.
    # _status se encapsula porque el ciclo de vida de una cita se controla con validación.
    def __init__(self, pet_id: str, date, reason: str,
                 veterinarian: str = '', status: str = 'scheduled',
                 id: str = None, created_at=None, updated_at=None):
        """
        Inicializa una cita veterinaria.
        _status es un atributo sensible controlado por @property con validación.
        """
        # [GUÍA 9 - ACTIVIDAD 1] Atributos públicos de la entidad cita
        self.id = id
        self.pet_id = pet_id          # str — ID de la mascota (referencia a pets)
        self.date = date              # datetime — fecha y hora de la cita
        self.reason = reason          # str — motivo de la consulta
        self.veterinarian = veterinarian  # str — nombre del veterinario
        self.created_at = created_at
        self.updated_at = updated_at
        # [GUÍA 9 - ACTIVIDAD 1] Atributo sensible: controla el ciclo de vida
        self._status = status

    # [GUÍA 9 - ACTIVIDAD 1] from_db — puente entre MongoDB y objeto Python.
    # Invocado automáticamente por BaseModel.find_by_id() vía patrón Template Method.
    @classmethod
    def from_db(cls, document: dict) -> 'Appointment':
        """Construye una instancia Appointment desde un documento MongoDB."""
        if document is None:
            return None
        pet_id_raw = document.get('pet_id')
        return cls(
            id=str(document['_id']),
            pet_id=str(pet_id_raw) if pet_id_raw else None,
            date=document.get('date'),
            reason=document.get('reason', ''),
            veterinarian=document.get('veterinarian', ''),
            status=document.get('status', 'scheduled'),
            created_at=document.get('created_at'),
            updated_at=document.get('updated_at'),
        )

    # [GUÍA 9 - ACTIVIDAD 1] to_dict — serializa la instancia a dict JSON-serializable.
    def to_dict(self) -> dict:
        """Serializa la cita a dict compatible con JSON."""
        return {
            '_id': self.id,
            'pet_id': self.pet_id,
            'date': (
                self.date.isoformat()
                if isinstance(self.date, datetime)
                else self.date
            ),
            'reason': self.reason,
            'veterinarian': self.veterinarian,
            # [GUÍA 9 - ACTIVIDAD 2] Accede al atributo privado vía property
            'status': self._status,
            'created_at': (
                self.created_at.isoformat()
                if isinstance(self.created_at, datetime)
                else self.created_at
            ),
            'updated_at': (
                self.updated_at.isoformat()
                if isinstance(self.updated_at, datetime)
                else self.updated_at
            ),
        }

    # [GUÍA 9 - ACTIVIDAD 1] __str__ — estado del objeto de forma profesional
    def __str__(self) -> str:
        date_str = (
            self.date.strftime('%Y-%m-%d %H:%M')
            if isinstance(self.date, datetime)
            else str(self.date)
        )
        return (
            f"Appointment(pet={self.pet_id}, "
            f"date={date_str}, reason='{self.reason}', "
            f"status={self._status})"
        )

    # [GUÍA 9 - ACTIVIDAD 1] __repr__ — representación técnica para debugging
    def __repr__(self) -> str:
        return (
            f"Appointment(id={self.id!r}, pet_id={self.pet_id!r}, "
            f"status={self._status!r})"
        )

    # [GUÍA 9 - ACTIVIDAD 2] @property para status — controla el ciclo de vida
    @property
    def status(self) -> str:
        """Estado del ciclo de vida de la cita (atributo sensible)."""
        return self._status

    # [GUÍA 9 - ACTIVIDAD 2] @setter valida la transición antes de asignar
    @status.setter
    def status(self, value: str):
        if value not in Appointment.STATUSES:
            raise ValueError(
                f"status inválido '{value}'. "
                f"Debe ser uno de: {Appointment.STATUSES}"
            )
        self._status = value

    # [GUÍA 9 - ACTIVIDAD 2] Método de instancia migrado desde dashboard.py.
    # _enriquecer_cita_dashboard(apt) → apt.enriquecer_dashboard()
    # Encapsula la lógica de serialización + lookup de mascota como comportamiento del objeto.
    def enriquecer_dashboard(self) -> dict:
        """
        Serializa la cita y embebe el nombre de la mascota para el dashboard.
        Migrado desde _enriquecer_cita_dashboard() en app/routes/dashboard.py.
        """
        # [GUÍA 7 - ACTIVIDAD 1] Mantiene la responsabilidad única: serializa + embebe pet_name
        from app.models.pet import Pet  # import tardío para evitar circularidad
        pet = Pet.find_by_id(self.pet_id)
        result = self.to_dict()
        result['pet_name'] = pet.name if pet else 'Desconocida'
        return result

    # [GUÍA 9 - ACTIVIDAD 2] Método de instancia migrado desde appointments.py.
    # _enrich_appointment(apt) → apt.enriquecer_api()
    # Embebe el objeto mascota completo para la respuesta JSON de la API REST.
    def enriquecer_api(self) -> dict:
        """
        Serializa la cita y embebe los datos completos de la mascota.
        Migrado desde _enrich_appointment() en app/routes/api/appointments.py.
        """
        from app.models.pet import Pet
        pet = Pet.find_by_id(self.pet_id)
        result = self.to_dict()
        result['pet'] = pet.to_dict() if pet else None
        return result

    # --- Operaciones de BD ---

    # [GUÍA 2 - ACTIVIDAD 1] Tipos de variables en parámetros del modelo
    @staticmethod
    def create(pet_id, date, reason, veterinarian='') -> 'Appointment':
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
        # [GUÍA 9 - ACTIVIDAD 3] Retorna instancia en lugar de dict crudo
        return Appointment.from_db(doc)

    # [GUÍA 2 - ACTIVIDAD 3] Lista de citas por mascota — ahora lista de instancias
    @staticmethod
    def find_by_pet(pet_id) -> list:
        docs = list(
            mongo.db[Appointment.COLLECTION]
            .find({'pet_id': ObjectId(pet_id)})
            .sort('date', -1)
        )
        # [GUÍA 9 - ACTIVIDAD 3] from_db convierte cada dict en instancia Appointment
        return [Appointment.from_db(doc) for doc in docs]

    @staticmethod
    def list_all(status=None) -> list:
        # [GUÍA 3 - ACTIVIDAD 3] Validación de parámetro opcional
        query = {}
        if status:
            query['status'] = status
        docs = list(
            mongo.db[Appointment.COLLECTION].find(query).sort('date', 1)
        )
        # [GUÍA 9 - ACTIVIDAD 3] Lista de instancias Appointment
        return [Appointment.from_db(doc) for doc in docs]

    @staticmethod
    def list_today() -> list:
        # [GUÍA 2 - ACTIVIDAD 4] Operadores aritméticos — cálculo de rango de fechas
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        docs = list(
            mongo.db[Appointment.COLLECTION].find({
                'date': {'$gte': today_start, '$lte': today_end}
            }).sort('date', 1)
        )
        # [GUÍA 9 - ACTIVIDAD 3] Lista de instancias
        return [Appointment.from_db(doc) for doc in docs]


def init_appointment_indexes():
    mongo.db[Appointment.COLLECTION].create_index('pet_id')
    mongo.db[Appointment.COLLECTION].create_index('date')
    mongo.db[Appointment.COLLECTION].create_index('status')
