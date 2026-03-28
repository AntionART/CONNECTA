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
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON del webhook de Evolution API
    # Uso en CONNECTA: request.get_json(silent=True) captura el payload POST
    # enviado por Evolution API cuando llega un mensaje de WhatsApp
    # Ejemplo: data = {'event': 'messages.upsert', 'data': {'key': {...}, 'message': {...}}}
    data = request.get_json(silent=True)

    # [GUÍA 3 - ACTIVIDAD 3] Validación de entrada — verificar que hay datos
    # Uso en CONNECTA: Si Evolution API envía un POST vacío o malformado,
    # retorna 400 inmediatamente sin procesar
    # Ejemplo: if not data → return {'status': 'no data'}, 400
    if not data:
        return jsonify({'status': 'no data'}), 400

    event = data.get('event')

    # [GUÍA 3 - ACTIVIDAD 1] if/elif — enrutamiento por tipo de evento
    # Uso en CONNECTA: Evolution API puede enviar 'messages.upsert' (nuevo mensaje)
    # o 'messages.update' (estado de entrega); cada uno tiene su handler
    # Ejemplo: event='messages.upsert' → _handle_message_upsert(data)
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
        # Uso en CONNECTA: key.fromMe=True significa que el mensaje lo envió la clínica;
        # solo procesamos mensajes de contactos externos (fromMe=False)
        # Ejemplo: if key.get('fromMe', False): return → descarta eco de mensajes salientes
        if key.get('fromMe', False):
            return

        # [GUÍA 2 - ACTIVIDAD 2] String manipulation — .replace() para limpiar número
        # Uso en CONNECTA: Evolution API envía el teléfono como '573001234567@s.whatsapp.net';
        # se limpia para obtener solo el número que usamos como clave en conversations
        # Ejemplo: '573001234567@s.whatsapp.net'.replace('@s.whatsapp.net', '') → '573001234567'
        remote_jid = key.get('remoteJid', '')
        phone = remote_jid.replace('@s.whatsapp.net', '').replace('@g.us', '')

        # [GUÍA 3 - ACTIVIDAD 3] Validación — rechazar si no hay número de teléfono
        # Uso en CONNECTA: Mensajes de grupos o payloads malformados pueden no tener
        # phone; sin él no podemos crear ni encontrar la conversación
        # Ejemplo: if not phone: return → ignora mensajes de grupos de WhatsApp
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

        # [GUÍA 6 - ACTIVIDAD 1] Vector — lista de tipos de media a detectar
        # Uso en CONNECTA: media_types es un vector 1D con los 4 tipos de adjuntos
        # que soporta WhatsApp; se itera para detectar si el mensaje tiene multimedia
        # Ejemplo: ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage']
        media_types = ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage']

        # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — iteración sobre tipos de media
        # Uso en CONNECTA: Revisa cada tipo de media en orden; si el mensaje
        # es una imagen, video, audio o documento, actualiza el tipo del content
        # Ejemplo: for media_type in media_types → si 'imageMessage' en msg_content → type='image'
        for media_type in media_types:
            if media_type in msg_content:
                # [GUÍA 5 - ACTIVIDAD 6] String method en ciclo — .replace() dentro de for
                # Uso en CONNECTA: 'imageMessage'.replace('Message', '') → 'image';
                # normaliza el nombre del tipo de media para almacenarlo en DB
                # Ejemplo: 'videoMessage'.replace('Message', '') → 'video'
                content['type'] = media_type.replace('Message', '')
                content['text'] = msg_content[media_type].get('caption', '')
                # [GUÍA 5 - ACTIVIDAD 3] break — detiene el ciclo al encontrar el tipo
                # Uso en CONNECTA: Un mensaje solo puede ser de un tipo de media;
                # al encontrar el primero, no tiene sentido seguir revisando los demás
                # Ejemplo: si es imagen → break, no verifica si también es video
                break

        # Find or create conversation
        conv = Conversation.find_or_create(phone, contact_name)
        conv_id = str(conv['_id'])

        # [GUÍA 3 - ACTIVIDAD 2] Operadores lógicos — and para condición compuesta
        # Uso en CONNECTA: Solo actualiza contact_name si llegó un nombre Y la
        # conversación no tenía nombre aún (evita sobreescribir nombres editados)
        # Ejemplo: if contact_name and not conv.get('contact_name') → actualiza
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

        # Emit socket events for real-time updates
        updated_conv = Conversation.find_by_id(conv_id)
        socketio.emit('new_message', {
            'conversation_id': conv_id,
            'message': serialize_doc(msg),
        })
        socketio.emit('conversation_updated', serialize_doc(updated_conv))

    # [GUÍA 4 - ACTIVIDAD 3] F-string en manejo de errores
    # Uso en CONNECTA: f'Webhook error: {e}' formatea el mensaje de log
    # incluyendo la excepción real para facilitar el debugging en producción
    # Ejemplo: logger.error('Webhook error: ConnectionRefusedError: ...')
    except Exception as e:
        current_app.logger.error(f'Webhook error: {e}')


def _handle_message_update(data):
    """
    Handle message status updates (delivered, read, etc.).
    """
    try:
        updates = data.get('data', [])

        # [GUÍA 3 - ACTIVIDAD 1] if/else — normalización de tipos de dato
        # Uso en CONNECTA: Evolution API puede enviar updates como dict único
        # o como lista; lo normalizamos siempre a lista para el for siguiente
        # Ejemplo: if isinstance(updates, dict): updates = [updates]
        if isinstance(updates, dict):
            updates = [updates]

        # [GUÍA 5 - ACTIVIDAD 4] Diccionario clave:valor — mapa de código a estado
        # Uso en CONNECTA: status_map convierte el código numérico de WhatsApp
        # al string de estado legible que guardamos en DB
        # Ejemplo: status_map = {2: 'sent', 3: 'delivered', 4: 'read'}
        status_map = {2: 'sent', 3: 'delivered', 4: 'read'}

        # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — iterar sobre actualizaciones de estado
        # Uso en CONNECTA: Cada update contiene el ID del mensaje de WhatsApp
        # y su nuevo estado; el for procesa cada uno para actualizar la DB
        # Ejemplo: for update in updates → actualiza status de msg '3EB0...' a 'read'
        for update in updates:
            wa_id = update.get('key', {}).get('id')
            status_code = update.get('update', {}).get('status')

            # [GUÍA 3 - ACTIVIDAD 2] Operador lógico — and para condición compuesta
            # Uso en CONNECTA: Solo procesa si hay tanto ID como código de estado;
            # un update sin ambos datos no puede ser procesado correctamente
            # Ejemplo: if wa_id and status_code → busca y actualiza el mensaje
            if wa_id and status_code:
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
