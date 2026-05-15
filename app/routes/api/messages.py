from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.whatsapp import WhatsAppService
from app.utils.helpers import get_or_404, save_message_and_notify


@api_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
@login_required
def list_messages(conversation_id):
    """
    List messages for a conversation with pagination.
    """
    # [GUÍA 9 - ACTIVIDAD 3] get_or_404 retorna instancia Conversation
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err

    # [GUÍA 4 - ACTIVIDAD 2] Casting de tipos — type=int en args.get()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # [GUÍA 9 - ACTIVIDAD 3] find_by_conversation retorna List[Message]
    messages = Message.find_by_conversation(conversation_id, page, per_page)
    total = Message.count_by_conversation(conversation_id)

    # [GUÍA 2 - ACTIVIDAD 4] Paginación — skip=(page-1)*per_page calculado en Message
    return jsonify({
        'messages': [m.to_dict() for m in messages],
        'total': total,
        'page': page,
        'per_page': per_page,
    })


@api_bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
@login_required
def send_message(conversation_id):
    """
    Send a message to a WhatsApp contact from the dashboard.
    """
    # [GUÍA 9 - ACTIVIDAD 3] get_or_404 retorna instancia Conversation
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err

    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body con texto del mensaje
    data = request.get_json()
    text = data.get('text', '').strip()

    # [GUÍA 3 - ACTIVIDAD 3] Validación — texto vacío no se envía a WhatsApp
    if not text:
        return jsonify({'error': 'text is required'}), 400

    # [GUÍA 9 - ACTIVIDAD 3] conv.phone_number en lugar de conv['phone_number']
    wa_response = WhatsAppService.send_text(conv.phone_number, text)

    # [GUÍA 3 - ACTIVIDAD 2] Operadores lógicos — isinstance + and para acceso seguro
    wa_message_id = None
    if isinstance(wa_response, dict) and 'key' in wa_response:
        wa_message_id = wa_response['key'].get('id')

    content = {'type': 'text', 'text': text, 'media_url': None}
    # [GUÍA 9 - ACTIVIDAD 3] save_message_and_notify retorna instancia Message
    msg = save_message_and_notify(conversation_id, 'outbound', 'agent', content, wa_message_id)

    return jsonify(msg.to_dict()), 201
