"""
Webhook endpoint receives real-time events from Evolution API.
This is the entry point for all WhatsApp inbound messages.
"""
from flask import Blueprint, request, jsonify, current_app
from app.models.conversation import Conversation
from app.models.message import Message
from app.utils.helpers import save_message_and_notify

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/', methods=['POST'])
def receive_message():
    """
    Receive incoming messages from Evolution API webhook.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON del webhook de Evolution API
    data = request.get_json(silent=True)

    # [GUÍA 3 - ACTIVIDAD 3] Validación de entrada — verificar que hay datos
    if not data:
        return jsonify({'status': 'no data'}), 400

    event = data.get('event')

    # [GUÍA 3 - ACTIVIDAD 1] if/elif — enrutamiento por tipo de evento
    if event == 'messages.upsert':
        _handle_message_upsert(data)
    elif event == 'messages.update':
        _handle_message_update(data)

    return jsonify({'status': 'ok'}), 200


def _handle_message_upsert(data):
    """
    Handle a new incoming message from Evolution API.
    """
    try:
        message_data = data.get('data', {})
        key = message_data.get('key', {})

        # [GUÍA 3 - ACTIVIDAD 2] Operador lógico — not para excluir mensajes propios
        if key.get('fromMe', False):
            return

        # [GUÍA 2 - ACTIVIDAD 2] String manipulation — .replace() para limpiar número
        remote_jid = key.get('remoteJid', '')
        phone = remote_jid.replace('@s.whatsapp.net', '').replace('@g.us', '')

        # [GUÍA 3 - ACTIVIDAD 3] Validación — rechazar si no hay número de teléfono
        if not phone:
            return

        contact_name = message_data.get('pushName', '')
        msg_content = message_data.get('message', {})
        wa_message_id = key.get('id', '')

        text = (
            msg_content.get('conversation')
            or msg_content.get('extendedTextMessage', {}).get('text')
            or ''
        )

        content = {'type': 'text', 'text': text, 'media_url': None}

        # [GUÍA 6 - ACTIVIDAD 1] Vector — lista de tipos de media a detectar
        media_types = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage']

        # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — iteración sobre tipos de media
        for media_type in media_types:
            if media_type in msg_content:
                # [GUÍA 5 - ACTIVIDAD 6] String method en ciclo — .replace()
                content['type'] = media_type.replace('Message', '')
                content['text'] = msg_content[media_type].get('caption', '')
                # [GUÍA 5 - ACTIVIDAD 3] break — detiene el ciclo al encontrar el tipo
                break

        # [GUÍA 9 - ACTIVIDAD 3] find_or_create retorna instancia Conversation
        conv = Conversation.find_or_create(phone, contact_name)
        # Accede al ID mediante atributo de instancia en lugar de dict lookup
        conv_id = conv.id

        # [GUÍA 3 - ACTIVIDAD 2] Operadores lógicos — and para condición compuesta
        # [GUÍA 9 - ACTIVIDAD 3] conv.contact_name en lugar de conv.get('contact_name')
        if contact_name and not conv.contact_name:
            Conversation.update(conv_id, {'contact_name': contact_name})

        save_message_and_notify(conv_id, 'inbound', 'contact', content, wa_message_id)

    # [GUÍA 4 - ACTIVIDAD 3] F-string en manejo de errores
    except Exception as e:
        current_app.logger.error(f'Webhook error: {e}')


def _handle_message_update(data):
    """
    Handle message status updates (delivered, read, etc.).
    """
    try:
        updates = data.get('data', [])

        # [GUÍA 3 - ACTIVIDAD 1] if/else — normalización de tipos de dato
        if isinstance(updates, dict):
            updates = [updates]

        # [GUÍA 5 - ACTIVIDAD 4] Diccionario clave:valor — mapa de código a estado
        status_map = {2: 'sent', 3: 'delivered', 4: 'read'}

        # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — iterar sobre actualizaciones de estado
        for update in updates:
            wa_id = update.get('key', {}).get('id')
            status_code = update.get('update', {}).get('status')

            # [GUÍA 3 - ACTIVIDAD 2] Operador lógico — and para condición compuesta
            if wa_id and status_code:
                status = status_map.get(status_code)
                if status:
                    # [GUÍA 9 - ACTIVIDAD 3] find_by_wa_id retorna instancia Message
                    msg = Message.find_by_wa_id(wa_id)
                    if msg:
                        from app.extensions import mongo
                        from bson import ObjectId
                        mongo.db.messages.update_one(
                            {'_id': ObjectId(msg.id)},
                            {'$set': {'status': status}},
                        )
    except Exception as e:
        current_app.logger.error(f'Webhook update error: {e}')
