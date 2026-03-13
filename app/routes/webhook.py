"""
Webhook endpoint receives real-time events from Evolution API.
This is the entry point for all WhatsApp inbound messages.
"""
from flask import Blueprint, request, jsonify, current_app
from app.models.conversation import Conversation
from app.models.message import Message
from app.extensions import socketio
from app.utils.helpers import serialize_doc

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/', methods=['POST'])
def receive_message():
    """
    Receive incoming messages from Evolution API webhook.

    Dynamic Input: Receives JSON payload from Evolution API.
    Business Rule: Routes events by type (messages.upsert, messages.update).
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'status': 'no data'}), 400

    event = data.get('event')

    if event == 'messages.upsert':
        _handle_message_upsert(data)
    elif event == 'messages.update':
        _handle_message_update(data)

    return jsonify({'status': 'ok'}), 200


def _handle_message_upsert(data):
    """
    Handle a new incoming message from Evolution API.

    Nested Structure: Evolution API payload has deeply nested keys (data.key.remoteJid).
    Nested Logic: Iterates through media types to detect content type (nested loop over list).
    List: media_types list ['imageMessage', 'videoMessage', ...] checked in loop.
    Business Rule: Only processes messages NOT from us (key.fromMe == False).
    Professional Output: Emits SocketIO events for real-time frontend updates.
    Debugging: try/except with logger.error for production error tracking.
    """
    try:
        message_data = data.get('data', {})
        key = message_data.get('key', {})

        # Business Rule: Only process messages from contacts (not sent by us)
        if key.get('fromMe', False):
            return

        # Nested Structure: Extract phone from deeply nested remoteJid
        remote_jid = key.get('remoteJid', '')
        phone = remote_jid.replace('@s.whatsapp.net', '').replace('@g.us', '')
        if not phone:
            return

        contact_name = message_data.get('pushName', '')
        msg_content = message_data.get('message', {})
        wa_message_id = key.get('id', '')

        # Extract text content
        text = (
            msg_content.get('conversation')
            or msg_content.get('extendedTextMessage', {}).get('text')
            or ''
        )

        content = {'type': 'text', 'text': text, 'media_url': None}

        # List: media_types list checked in loop to detect content type
        # Nested Logic: Iterates through media types; first match breaks the loop
        for media_type in ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage']:
            if media_type in msg_content:
                content['type'] = media_type.replace('Message', '')
                content['text'] = msg_content[media_type].get('caption', '')
                break

        # Find or create conversation
        conv = Conversation.find_or_create(phone, contact_name)
        conv_id = str(conv['_id'])

        # Update contact name if we have one now
        if contact_name and not conv.get('contact_name'):
            Conversation.update(conv_id, {'contact_name': contact_name})

        # Create message record
        msg = Message.create(
            conversation_id=conv_id,
            direction='inbound',
            sender_type='contact',
            content=content,
            wa_message_id=wa_message_id,
        )

        # Update conversation last message
        Conversation.update_last_message(conv_id, text, is_from_contact=True)

        # Professional Output: Emit socket events for real-time updates
        updated_conv = Conversation.find_by_id(conv_id)
        socketio.emit('new_message', {
            'conversation_id': conv_id,
            'message': serialize_doc(msg),
        })
        socketio.emit('conversation_updated', serialize_doc(updated_conv))

    # Debugging: try/except with logger.error for production error tracking
    except Exception as e:
        current_app.logger.error(f'Webhook error: {e}')


def _handle_message_update(data):
    """
    Handle message status updates (delivered, read, etc.).

    Nested Structure: Maps numeric status codes to string labels.
    Data Structure: status_map dict maps integers to status strings.
    List: Iterates over updates array.
    """
    try:
        # List: updates may be a single dict or an array; normalize to list
        updates = data.get('data', [])
        if isinstance(updates, dict):
            updates = [updates]

        # List: Iterates over updates array
        for update in updates:
            wa_id = update.get('key', {}).get('id')
            status_code = update.get('update', {}).get('status')
            if wa_id and status_code:
                # Data Structure: status_map dict maps integers to status strings
                status_map = {2: 'sent', 3: 'delivered', 4: 'read'}
                status = status_map.get(status_code)
                if status:
                    msg = Message.find_by_wa_id(wa_id)
                    if msg:
                        from app.extensions import mongo
                        mongo.db.messages.update_one(
                            {'_id': msg['_id']},
                            {'$set': {'status': status}},
                        )
    except Exception as e:
        current_app.logger.error(f'Webhook update error: {e}')
