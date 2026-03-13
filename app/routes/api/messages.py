from flask import request, jsonify
from flask_login import login_required, current_user
from app.routes.api import api_bp
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.whatsapp import WhatsAppService
from app.extensions import socketio
from app.utils.helpers import serialize_doc, serialize_docs


@api_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
@login_required
def list_messages(conversation_id):
    """
    List messages for a conversation with pagination.

    Arithmetic Logic: Pagination with page and per_page parameters.
    Professional Output: Returns paginated response with messages, total, page, per_page.
    """
    conv = Conversation.find_by_id(conversation_id)
    if not conv:
        return jsonify({'error': 'Not found'}), 404

    # Arithmetic Logic: Pagination with page and per_page parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    messages = Message.find_by_conversation(conversation_id, page, per_page)
    total = Message.count_by_conversation(conversation_id)

    # Professional Output: Returns paginated response with messages, total, page, per_page
    return jsonify({
        'messages': serialize_docs(messages),
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@api_bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
@login_required
def send_message(conversation_id):
    """
    Send a message to a WhatsApp contact from the dashboard.

    Business Rule: Sends via WhatsApp first, then saves to DB.
    Nested Structure: wa_response may contain nested key.id for message tracking.
    MVP Integration: Core feature — agents can reply to WhatsApp from the dashboard.
    """
    conv = Conversation.find_by_id(conversation_id)
    if not conv:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'text is required'}), 400

    # Business Rule: Sends via WhatsApp first, then saves to DB
    wa_response = WhatsAppService.send_text(conv['phone_number'], text)

    # Nested Structure: wa_response may contain nested key.id for message tracking
    wa_message_id = None
    if isinstance(wa_response, dict) and 'key' in wa_response:
        wa_message_id = wa_response['key'].get('id')

    # Save message to DB
    content = {'type': 'text', 'text': text, 'media_url': None}
    msg = Message.create(
        conversation_id=conversation_id,
        direction='outbound',
        sender_type='agent',
        content=content,
        wa_message_id=wa_message_id,
    )

    # Update conversation
    Conversation.update_last_message(conversation_id, text, is_from_contact=False)

    # Emit socket event
    socketio.emit('new_message', {
        'conversation_id': conversation_id,
        'message': serialize_doc(msg),
    })

    updated_conv = Conversation.find_by_id(conversation_id)
    socketio.emit('conversation_updated', serialize_doc(updated_conv))

    return jsonify(serialize_doc(msg)), 201
