from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.conversation import Conversation
from app.models.message import Message
from app.services.whatsapp import WhatsAppService
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404, save_message_and_notify


@api_bp.route('/conversations/<conversation_id>/messages', methods=['GET'])
@login_required
def list_messages(conversation_id):
    """
    List messages for a conversation with pagination.
    """
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err

    # [GUÍA 4 - ACTIVIDAD 2] Casting de tipos — type=int en args.get()
    # Uso en CONNECTA: Los query params de URL son siempre strings; type=int
    # convierte '2' → 2 automáticamente para usar en cálculos de paginación
    # Ejemplo: ?page=2&per_page=50 → page=int('2')=2, per_page=int('50')=50
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    messages = Message.find_by_conversation(conversation_id, page, per_page)
    total = Message.count_by_conversation(conversation_id)

    # [GUÍA 2 - ACTIVIDAD 4] Operadores aritméticos — implícitos en paginación MongoDB
    # Uso en CONNECTA: La paginación usa skip=(page-1)*per_page internamente;
    # page y per_page son int para hacer esa multiplicación correctamente
    # Ejemplo: page=2, per_page=50 → skip=50, limit=50 → mensajes 51-100
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
    """
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err

    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body con texto del mensaje
    # Uso en CONNECTA: El agente escribe el mensaje en el chat del dashboard;
    # .get('text', '').strip() captura y limpia el texto antes de enviarlo
    # Ejemplo: data = {'text': 'Hola, su cita es mañana a las 10am'}
    data = request.get_json()
    text = data.get('text', '').strip()

    # [GUÍA 3 - ACTIVIDAD 3] Validación — texto vacío no se envía a WhatsApp
    # Uso en CONNECTA: Evita enviar mensajes vacíos al contacto vía Evolution API
    # Ejemplo: if not text → return 400 antes de llamar WhatsAppService.send_text()
    if not text:
        return jsonify({'error': 'text is required'}), 400

    wa_response = WhatsAppService.send_text(conv['phone_number'], text)

    # [GUÍA 3 - ACTIVIDAD 2] Operadores lógicos — isinstance + and para acceso seguro
    # Uso en CONNECTA: wa_response puede ser dict o None según la respuesta de Evolution;
    # solo accede a 'key' si efectivamente es un dict y tiene esa clave
    # Ejemplo: if isinstance(wa_response, dict) and 'key' in wa_response → extrae ID
    wa_message_id = None
    if isinstance(wa_response, dict) and 'key' in wa_response:
        wa_message_id = wa_response['key'].get('id')

    content = {'type': 'text', 'text': text, 'media_url': None}
    msg = save_message_and_notify(conversation_id, 'outbound', 'agent', content, wa_message_id)

    return jsonify(serialize_doc(msg)), 201
