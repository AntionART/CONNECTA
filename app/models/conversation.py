"""
Conversation Model — Core of the WhatsApp CRM.

Conversations represent ongoing chat threads entre la clínica y los dueños
de mascotas vía WhatsApp. Cada conversación se identifica por número de teléfono.

[GUÍA 9 - ACTIVIDAD 1] Modelo OOP completo: __init__, from_db, to_dict,
__str__, __repr__. Atributos PII y de estado prefijados con _ para
encapsulamiento. phone_number es read-only (inmutable tras la creación).
"""

from app.extensions import mongo
from app.models.base import BaseModel
from datetime import datetime, timezone
from bson import ObjectId


class Conversation(BaseModel):
    COLLECTION = 'conversations'

    # [GUÍA 9 - ACTIVIDAD 1] Constructor explícito con todos los atributos de la entidad.
    # _phone_number es PII e inmutable; _status y _unread_count son sensibles de estado.
    def __init__(self, phone_number: str, contact_name: str = '',
                 assigned_to=None, labels: list = None,
                 status: str = 'open', unread_count: int = 0,
                 last_message: dict = None,
                 id: str = None, created_at=None, updated_at=None):
        """
        Inicializa un hilo de conversación WhatsApp.
        _phone_number es PII e inmutable (sin setter).
        _status y _unread_count son atributos de estado sensibles.
        """
        # [GUÍA 9 - ACTIVIDAD 1] Atributos públicos
        self.id = id
        self.contact_name = contact_name
        self.assigned_to = assigned_to
        # [GUÍA 2 - ACTIVIDAD 3] Lista como campo del documento — etiquetas de la conv
        self.labels = labels if labels is not None else []
        # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado como sub-documento last_message
        self.last_message = last_message if last_message is not None else {
            'text': '',
            'timestamp': None,
            'is_from_contact': True,
        }
        self.created_at = created_at
        self.updated_at = updated_at
        # [GUÍA 9 - ACTIVIDAD 1] Atributos sensibles con convención _atributo
        self._phone_number = phone_number  # PII — inmutable, sin setter
        self._status = status              # estado del hilo ('open' | 'closed')
        self._unread_count = unread_count  # contador — solo se modifica vía BD

    # [GUÍA 9 - ACTIVIDAD 1] from_db — puente entre MongoDB y objeto Python.
    @classmethod
    def from_db(cls, document: dict) -> 'Conversation':
        """Construye una instancia Conversation desde un documento MongoDB."""
        if document is None:
            return None
        return cls(
            id=str(document['_id']),
            phone_number=document.get('phone_number', ''),
            contact_name=document.get('contact_name', ''),
            assigned_to=document.get('assigned_to'),
            labels=document.get('labels', []),
            status=document.get('status', 'open'),
            unread_count=document.get('unread_count', 0),
            last_message=document.get('last_message', {}),
            created_at=document.get('created_at'),
            updated_at=document.get('updated_at'),
        )

    # [GUÍA 9 - ACTIVIDAD 1] to_dict — serializa a dict JSON-serializable.
    # Maneja el datetime interno de last_message.
    def to_dict(self) -> dict:
        """Serializa la conversación a dict compatible con JSON."""
        # Serializa el timestamp dentro de last_message
        last_msg = {}
        if self.last_message:
            ts = self.last_message.get('timestamp')
            last_msg = {
                **self.last_message,
                'timestamp': ts.isoformat() if isinstance(ts, datetime) else ts,
            }
        return {
            '_id': self.id,
            # [GUÍA 9 - ACTIVIDAD 2] Accede al atributo PII vía property
            'phone_number': self._phone_number,
            'contact_name': self.contact_name,
            'assigned_to': self.assigned_to,
            'labels': self.labels,
            'status': self._status,
            'unread_count': self._unread_count,
            'last_message': last_msg,
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
        last_text = (self.last_message or {}).get('text', '')
        preview = last_text[:40] + '...' if len(last_text) > 40 else last_text
        return (
            f"Conversation(phone={self._phone_number}, "
            f"contact='{self.contact_name}', status={self._status}, "
            f"unread={self._unread_count}, last='{preview}')"
        )

    # [GUÍA 9 - ACTIVIDAD 1] __repr__ — representación técnica para debugging
    def __repr__(self) -> str:
        return (
            f"Conversation(id={self.id!r}, "
            f"phone={self._phone_number!r}, "
            f"status={self._status!r})"
        )

    # [GUÍA 9 - ACTIVIDAD 2] @property read-only para phone_number (PII inmutable)
    @property
    def phone_number(self) -> str:
        """Número WhatsApp del contacto — PII inmutable tras la creación."""
        return self._phone_number

    # [GUÍA 9 - ACTIVIDAD 2] @property con setter para status
    @property
    def status(self) -> str:
        """Estado del hilo de conversación."""
        return self._status

    @status.setter
    def status(self, value: str):
        valid = ('open', 'closed')
        if value not in valid:
            raise ValueError(f"status inválido. Debe ser uno de: {valid}")
        self._status = value

    # [GUÍA 9 - ACTIVIDAD 2] @property read-only para unread_count
    # El contador se gestiona vía BD (update_last_message / reset_unread)
    @property
    def unread_count(self) -> int:
        """Mensajes no leídos — solo se modifica vía update_last_message()."""
        return self._unread_count

    # --- Operaciones de BD ---

    @staticmethod
    def create(phone_number, contact_name='') -> 'Conversation':
        # [GUÍA 2 - ACTIVIDAD 1] Variables con tipos explícitos en el documento
        doc = {
            'phone_number': phone_number,
            'contact_name': contact_name,
            'assigned_to': None,
            # [GUÍA 2 - ACTIVIDAD 3] Lista como campo del documento
            'labels': [],
            'status': 'open',
            'unread_count': 0,
            # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado como sub-documento
            'last_message': {
                'text': '',
                'timestamp': datetime.now(timezone.utc),
                'is_from_contact': True,
            },
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
        result = mongo.db[Conversation.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        # [GUÍA 9 - ACTIVIDAD 3] Retorna instancia en lugar de dict crudo
        return Conversation.from_db(doc)

    @staticmethod
    def find_by_phone(phone_number) -> 'Conversation':
        doc = mongo.db[Conversation.COLLECTION].find_one(
            {'phone_number': phone_number}
        )
        # [GUÍA 9 - ACTIVIDAD 3] from_db retorna instancia o None
        return Conversation.from_db(doc) if doc else None

    # [GUÍA 3 - ACTIVIDAD 1] if/else — patrón find-or-create idempotente
    @staticmethod
    def find_or_create(phone_number, contact_name='') -> 'Conversation':
        conv = Conversation.find_by_phone(phone_number)
        if not conv:
            conv = Conversation.create(phone_number, contact_name)
        return conv

    # [GUÍA 3 - ACTIVIDAD 1/3] Construcción condicional del query con filtros opcionales
    @staticmethod
    def list_all(filters=None) -> list:
        query = {}
        if filters:
            if filters.get('status'):
                query['status'] = filters['status']
            if filters.get('assigned_to'):
                query['assigned_to'] = filters['assigned_to']
            if filters.get('label'):
                query['labels'] = filters['label']
        docs = list(
            mongo.db[Conversation.COLLECTION]
            .find(query)
            .sort('last_message.timestamp', -1)
        )
        # [GUÍA 9 - ACTIVIDAD 3] Lista de instancias Conversation
        return [Conversation.from_db(doc) for doc in docs]

    @staticmethod
    def update(conversation_id, update_data):
        update_data['updated_at'] = datetime.now(timezone.utc)
        mongo.db[Conversation.COLLECTION].update_one(
            {'_id': ObjectId(conversation_id)},
            {'$set': update_data},
        )

    @staticmethod
    def update_last_message(conversation_id, text, is_from_contact):
        now = datetime.now(timezone.utc)
        update = {
            '$set': {
                'last_message': {
                    'text': text,
                    'timestamp': now,
                    'is_from_contact': is_from_contact,
                },
                'updated_at': now,
            }
        }
        # [GUÍA 2 - ACTIVIDAD 4] $inc — incremento atómico de contador
        if is_from_contact:
            update['$inc'] = {'unread_count': 1}
        mongo.db[Conversation.COLLECTION].update_one(
            {'_id': ObjectId(conversation_id)},
            update,
        )

    @staticmethod
    def reset_unread(conversation_id):
        mongo.db[Conversation.COLLECTION].update_one(
            {'_id': ObjectId(conversation_id)},
            {'$set': {'unread_count': 0}},
        )


# [GUÍA 6 - ACTIVIDAD 2] Matriz implícita — índice compuesto como lista de tuplas
def init_conversation_indexes():
    mongo.db[Conversation.COLLECTION].create_index('phone_number', unique=True)
    mongo.db[Conversation.COLLECTION].create_index('status')
    mongo.db[Conversation.COLLECTION].create_index('assigned_to')
    mongo.db[Conversation.COLLECTION].create_index([('last_message.timestamp', -1)])
