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
from datetime import datetime, timezone
from bson import ObjectId


class Conversation:
    COLLECTION = 'conversations'

    @staticmethod
    def create(phone_number, contact_name=''):
        doc = {
            'phone_number': phone_number,
            'contact_name': contact_name,
            'assigned_to': None,
            # List: labels is an array/list field that stores tag names.
            # Allows a conversation to have multiple categorical labels
            # (e.g., 'urgent', 'vip') for filtering and organization.
            'labels': [],
            # Business Rule: New conversations start with status 'open'
            # and unread_count 0 — they become 'unread' once a message
            # arrives and the agent hasn't viewed it yet.
            'status': 'open',
            'unread_count': 0,
            # Nested Structure: last_message is a nested dict within the
            # document. It stores a denormalized snapshot of the most recent
            # message to enable fast list rendering without joining messages.
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
    def find_by_id(conversation_id):
        return mongo.db[Conversation.COLLECTION].find_one(
            {'_id': ObjectId(conversation_id)}
        )

    @staticmethod
    def find_by_phone(phone_number):
        return mongo.db[Conversation.COLLECTION].find_one(
            {'phone_number': phone_number}
        )

    # Business Rule: Ensures one conversation per phone number (idempotent).
    # If a conversation for this phone already exists, it returns the existing
    # one; otherwise it creates a new one. This prevents duplicate threads
    # when multiple messages arrive before the first is fully processed.
    @staticmethod
    def find_or_create(phone_number, contact_name=''):
        conv = Conversation.find_by_phone(phone_number)
        if not conv:
            conv = Conversation.create(phone_number, contact_name)
        return conv

    # Dynamic Input: Receives optional filters dict from the dashboard/API.
    @staticmethod
    def list_all(filters=None):
        query = {}
        # Nested Logic: Builds query dict conditionally based on provided
        # filters. Each filter key is checked independently, allowing
        # partial filtering (e.g., only by status, or status + assigned_to).
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
        # Nested Structure: Uses MongoDB $set with nested dot notation
        # to update the embedded last_message sub-document atomically.
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
        # Arithmetic Logic: $inc increments unread_count by 1 for inbound
        # messages. This is an atomic counter update in MongoDB.
        # Business Rule: Only inbound messages (is_from_contact=True)
        # increment unread count — outbound messages sent by agents don't.
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


# List: Multiple index definitions for query optimization.
# Each index targets a common query pattern in the CRM dashboard:
# phone_number (unique lookup), status (filter), assigned_to (filter),
# and last_message.timestamp (sort order for conversation list).
def init_conversation_indexes():
    mongo.db[Conversation.COLLECTION].create_index('phone_number', unique=True)
    mongo.db[Conversation.COLLECTION].create_index('status')
    mongo.db[Conversation.COLLECTION].create_index('assigned_to')
    mongo.db[Conversation.COLLECTION].create_index([('last_message.timestamp', -1)])
