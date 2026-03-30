"""
Conversation Model — Core of the WhatsApp CRM.

Conversations represent ongoing chat threads between the veterinary clinic
and pet owners via WhatsApp. Each conversation is uniquely identified by
a phone number and aggregates metadata such as labels, assignment, and
the last message received or sent.

MVP Integration: Conversations bridge the WhatsApp webhook (inbound) and
the agent dashboard (outbound), forming the central entity of the CRM.

Bilingualism: Code and comments in English; contact_name and message text
may contain any locale content from WhatsApp users.
"""

from app.extensions import mongo
from app.models.base import BaseModel
from datetime import datetime, timezone
from bson import ObjectId


class Conversation(BaseModel):
    COLLECTION = 'conversations'

    @staticmethod
    def create(phone_number, contact_name=''):
        # [GUÍA 2 - ACTIVIDAD 1] Variables con tipos explícitos en el documento
        # Uso en CONNECTA: phone_number y contact_name son str, unread_count es int (contador),
        # status es str constante, labels es lista, last_message es dict anidado
        # Ejemplo: {'phone_number': '573001234567', 'unread_count': 0, 'status': 'open'}
        doc = {
            'phone_number': phone_number,  # str — número WhatsApp del contacto
            'contact_name': contact_name,  # str — nombre del dueño (pushName)
            'assigned_to': None,
            # [GUÍA 2 - ACTIVIDAD 3] Lista como campo del documento
            # Uso en CONNECTA: labels almacena los tags de la conversación como lista;
            # permite múltiples etiquetas por chat (ej: ['urgente', 'vip'])
            # Ejemplo: labels=['urgente', 'vip'] → filtrables en el dashboard
            'labels': [],
            'status': 'open',       # str — estado del hilo ('open' | 'closed')
            'unread_count': 0,      # int — contador de mensajes no leídos
            # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado como sub-documento
            # Uso en CONNECTA: last_message es un dict embebido que permite mostrar
            # la vista previa del chat sin hacer join con la colección messages
            # Ejemplo: last_message = {'text': 'Hola', 'timestamp': ..., 'is_from_contact': True}
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
        return doc

    @staticmethod
    def find_by_phone(phone_number):
        return mongo.db[Conversation.COLLECTION].find_one(
            {'phone_number': phone_number}
        )

    # [GUÍA 3 - ACTIVIDAD 1] if/else — patrón find-or-create idempotente
    # Uso en CONNECTA: Garantiza un solo hilo por número de teléfono;
    # si ya existe la conversación, la retorna; si no, la crea nueva
    # Ejemplo: Mensaje del mismo número → misma conversación, no duplicados
    @staticmethod
    def find_or_create(phone_number, contact_name=''):
        conv = Conversation.find_by_phone(phone_number)
        if not conv:
            conv = Conversation.create(phone_number, contact_name)
        return conv

    # [GUÍA 3 - ACTIVIDAD 3] Validación de parámetro opcional con construcción condicional
    # Uso en CONNECTA: Construye el query MongoDB solo con los filtros que tienen valor;
    # permite filtrar por status='open', assigned_to='user_id', o label='urgente'
    # Ejemplo: filters={'status': 'open'} → query={'status': 'open'}
    @staticmethod
    def list_all(filters=None):
        query = {}
        # [GUÍA 3 - ACTIVIDAD 1] if/elif anidados — construcción condicional de query
        # Uso en CONNECTA: Cada condición agrega un filtro al dict query solo si
        # el parámetro fue provisto; permite búsquedas parciales o combinadas
        # Ejemplo: filters={'status':'open','label':'vip'} → query={'status':'open','labels':'vip'}
        if filters:
            if filters.get('status'):
                query['status'] = filters['status']
            if filters.get('assigned_to'):
                query['assigned_to'] = filters['assigned_to']
            if filters.get('label'):
                query['labels'] = filters['label']
        return list(
            mongo.db[Conversation.COLLECTION]
            .find(query)
            .sort('last_message.timestamp', -1)
        )

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
        # [GUÍA 2 - ACTIVIDAD 4] Operador aritmético — incremento atómico de contador
        # Uso en CONNECTA: $inc incrementa unread_count en +1 por cada mensaje
        # entrante; el agente lo resetea a 0 al abrir la conversación
        # Ejemplo: unread_count = 3 + 1 = 4 al llegar un nuevo mensaje
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
# Uso en CONNECTA: create_index([('last_message.timestamp', -1)]) recibe una lista
# de tuplas (campo, dirección), estructura matricial de [campo][orden]
# Ejemplo: [('last_message.timestamp', -1)] → índice descendente para ordenar chats
def init_conversation_indexes():
    mongo.db[Conversation.COLLECTION].create_index('phone_number', unique=True)
    mongo.db[Conversation.COLLECTION].create_index('status')
    mongo.db[Conversation.COLLECTION].create_index('assigned_to')
    mongo.db[Conversation.COLLECTION].create_index([('last_message.timestamp', -1)])
