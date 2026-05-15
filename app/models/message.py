"""
Message Model — Chat History Storage.

The messages collection stores every individual chat message exchanged
within a conversation. Each message is linked via conversation_id.

[GUÍA 9 - ACTIVIDAD 1] Modelo OOP completo: __init__, from_db, to_dict,
__str__, __repr__. _status es sensible porque refleja el pipeline de
entrega de WhatsApp (sent → delivered → read).
"""

from app.extensions import mongo
from datetime import datetime, timezone
from bson import ObjectId


class Message:
    COLLECTION = 'messages'

    # [GUÍA 9 - ACTIVIDAD 1] Constructor explícito con todos los atributos del mensaje.
    # _status encapsula el estado del pipeline de entrega de WhatsApp.
    def __init__(self, conversation_id: str, direction: str,
                 sender_type: str, content: dict,
                 wa_message_id: str = None, status: str = None,
                 id: str = None, timestamp=None):
        """
        Inicializa un mensaje del historial de chat.
        _status refleja el estado de entrega WhatsApp (sent/delivered/read/received).
        """
        # [GUÍA 9 - ACTIVIDAD 1] Atributos públicos del mensaje
        self.id = id
        self.conversation_id = conversation_id  # str — ref a conversations
        self.direction = direction              # str — 'inbound' | 'outbound'
        self.sender_type = sender_type         # str — 'contact' | 'agent'
        self.content = content                 # dict — {type, text, media_url}
        self.wa_message_id = wa_message_id    # str — ID de WhatsApp para tracking
        self.timestamp = timestamp
        # [GUÍA 9 - ACTIVIDAD 1] Atributo sensible — pipeline de entrega WhatsApp
        default_status = 'sent' if direction == 'outbound' else 'received'
        self._status = status if status is not None else default_status

    # [GUÍA 9 - ACTIVIDAD 1] from_db — puente entre MongoDB y objeto Python.
    @classmethod
    def from_db(cls, document: dict) -> 'Message':
        """Construye una instancia Message desde un documento MongoDB."""
        if document is None:
            return None
        conv_id_raw = document.get('conversation_id')
        return cls(
            id=str(document['_id']),
            conversation_id=(
                str(conv_id_raw) if conv_id_raw else None
            ),
            direction=document.get('direction', ''),
            sender_type=document.get('sender_type', ''),
            content=document.get('content', {}),
            wa_message_id=document.get('wa_message_id'),
            status=document.get('status'),
            timestamp=document.get('timestamp'),
        )

    # [GUÍA 9 - ACTIVIDAD 1] to_dict — serializa a dict JSON-serializable.
    def to_dict(self) -> dict:
        """Serializa el mensaje a dict compatible con JSON."""
        return {
            '_id': self.id,
            'conversation_id': self.conversation_id,
            'direction': self.direction,
            'sender_type': self.sender_type,
            'content': self.content,
            'wa_message_id': self.wa_message_id,
            # [GUÍA 9 - ACTIVIDAD 2] Accede al estado vía property
            'status': self._status,
            'timestamp': (
                self.timestamp.isoformat()
                if isinstance(self.timestamp, datetime)
                else self.timestamp
            ),
        }

    # [GUÍA 9 - ACTIVIDAD 1] __str__ — representación legible del estado del objeto
    def __str__(self) -> str:
        text_preview = (self.content or {}).get('text', '')
        preview = text_preview[:40] + '...' if len(text_preview) > 40 else text_preview
        return (
            f"Message({self.direction}, {self.sender_type}, "
            f"status={self._status}, text='{preview}')"
        )

    # [GUÍA 9 - ACTIVIDAD 1] __repr__ — representación técnica para debugging
    def __repr__(self) -> str:
        return (
            f"Message(id={self.id!r}, direction={self.direction!r}, "
            f"status={self._status!r})"
        )

    # [GUÍA 9 - ACTIVIDAD 2] @property read-only para status del pipeline de entrega
    @property
    def status(self) -> str:
        """Estado del pipeline de entrega WhatsApp (solo lectura desde instancia)."""
        return self._status

    # --- Operaciones de BD ---

    @staticmethod
    def create(conversation_id, direction, sender_type,
               content, wa_message_id=None) -> 'Message':
        doc = {
            'conversation_id': ObjectId(conversation_id),
            'direction': direction,
            'sender_type': sender_type,
            'content': content,
            'wa_message_id': wa_message_id,
            'status': 'sent' if direction == 'outbound' else 'received',
            'timestamp': datetime.now(timezone.utc),
        }
        result = mongo.db[Message.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        # [GUÍA 9 - ACTIVIDAD 3] Retorna instancia en lugar de dict crudo
        return Message.from_db(doc)

    @staticmethod
    def find_by_conversation(conversation_id, page=1, per_page=50) -> list:
        skip = (page - 1) * per_page
        docs = list(
            mongo.db[Message.COLLECTION]
            .find({'conversation_id': ObjectId(conversation_id)})
            .sort('timestamp', 1)
            .skip(skip)
            .limit(per_page)
        )
        # [GUÍA 9 - ACTIVIDAD 3] Lista de instancias Message
        return [Message.from_db(doc) for doc in docs]

    @staticmethod
    def count_by_conversation(conversation_id) -> int:
        return mongo.db[Message.COLLECTION].count_documents(
            {'conversation_id': ObjectId(conversation_id)}
        )

    @staticmethod
    def find_by_wa_id(wa_message_id) -> 'Message':
        doc = mongo.db[Message.COLLECTION].find_one(
            {'wa_message_id': wa_message_id}
        )
        # [GUÍA 9 - ACTIVIDAD 3] from_db retorna instancia o None
        return Message.from_db(doc) if doc else None


def init_message_indexes():
    mongo.db[Message.COLLECTION].create_index('conversation_id')
    mongo.db[Message.COLLECTION].create_index('wa_message_id', sparse=True)
    mongo.db[Message.COLLECTION].create_index('timestamp')
