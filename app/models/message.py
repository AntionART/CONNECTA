"""
Message Model — Chat History Storage.

The messages collection stores every individual chat message exchanged
within a conversation. Each message is linked to a conversation via
conversation_id and contains its content, direction, and delivery status.

MVP Integration: Messages are created by the webhook (inbound from WhatsApp)
and by the agent dashboard (outbound replies). They are queried with
pagination to render the chat view.

Debugging Patterns: wa_message_id (WhatsApp message ID) enables deduplication
and status tracking of messages through the WhatsApp delivery pipeline.
"""

from app.extensions import mongo
from datetime import datetime, timezone
from bson import ObjectId


class Message:
    COLLECTION = 'messages'

    @staticmethod
    def create(conversation_id, direction, sender_type, content, wa_message_id=None):
        """
        Data Structure: content is a nested dict {type, text, media_url}
        that holds the message payload. The shape varies by message type
        (text, image, document, etc.).

        Syntax & Variables: direction is 'inbound' or 'outbound' (enum-like
        string). 'inbound' = from WhatsApp contact, 'outbound' = from agent.
        sender_type further distinguishes 'contact', 'agent', or 'system'.
        """
        doc = {
            'conversation_id': ObjectId(conversation_id),
            # Syntax & Variables: direction controls message flow logic.
            'direction': direction,
            'sender_type': sender_type,
            'content': content,
            'wa_message_id': wa_message_id,
            # Business Rule: status defaults based on direction.
            # 'outbound' messages start as 'sent' (awaiting delivery confirmation),
            # 'inbound' messages start as 'received' (already delivered to us).
            'status': 'sent' if direction == 'outbound' else 'received',
            'timestamp': datetime.now(timezone.utc),
        }
        result = mongo.db[Message.COLLECTION].insert_one(doc)
        doc['_id'] = result.inserted_id
        return doc

    @staticmethod
    def find_by_conversation(conversation_id, page=1, per_page=50):
        # Arithmetic Logic: skip = (page - 1) * per_page calculates the
        # pagination offset. Page 1 skips 0, page 2 skips 50, etc.
        skip = (page - 1) * per_page
        # List: Returns a list of message documents sorted by timestamp
        # in ascending order (oldest first) so the chat reads top-to-bottom.
        return list(
            mongo.db[Message.COLLECTION]
            .find({'conversation_id': ObjectId(conversation_id)})
            .sort('timestamp', 1)
            .skip(skip)
            .limit(per_page)
        )

    @staticmethod
    def count_by_conversation(conversation_id):
        return mongo.db[Message.COLLECTION].count_documents(
            {'conversation_id': ObjectId(conversation_id)}
        )

    @staticmethod
    def find_by_wa_id(wa_message_id):
        return mongo.db[Message.COLLECTION].find_one(
            {'wa_message_id': wa_message_id}
        )


def init_message_indexes():
    mongo.db[Message.COLLECTION].create_index('conversation_id')
    mongo.db[Message.COLLECTION].create_index('wa_message_id', sparse=True)
    mongo.db[Message.COLLECTION].create_index('timestamp')
