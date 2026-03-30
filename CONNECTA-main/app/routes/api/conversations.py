from flask import request, jsonify
from flask_login import login_required, current_user
from app.routes.api import api_bp
from app.models.conversation import Conversation
from app.models.label import Label
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404


# [GUÍA 4 - ACTIVIDAD 1] Captura de datos — query params de la request HTTP
# Uso en CONNECTA: Los filtros del listado de conversaciones llegan como
# parámetros de URL (?status=open&label=urgente); request.args.get() los captura
# Ejemplo: GET /api/conversations?status=open → filters['status'] = 'open'
@api_bp.route('/conversations', methods=['GET'])
@login_required
def list_conversations():
    """
    List all conversations with optional filtering.
    """
    # [GUÍA 5 - ACTIVIDAD 4] Diccionario — construcción de filtros desde query params
    # Uso en CONNECTA: filters agrupa los 3 parámetros opcionales en un dict
    # que se pasa al modelo; si un param no está en la URL su valor es None
    # Ejemplo: filters = {'status': 'open', 'assigned_to': None, 'label': 'vip'}
    filters = {
        'status': request.args.get('status'),
        'assigned_to': request.args.get('assigned_to'),
        'label': request.args.get('label'),
    }
    conversations = Conversation.list_all(filters)
    return jsonify(serialize_docs(conversations))


@api_bp.route('/conversations/<conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err
    Conversation.reset_unread(conversation_id)
    return jsonify(serialize_doc(conv))


@api_bp.route('/conversations/<conversation_id>', methods=['PATCH'])
@login_required
def update_conversation(conversation_id):
    """
    Partially update a conversation's metadata.
    """
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err

    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — cuerpo JSON de la request PATCH
    # Uso en CONNECTA: El frontend envía un JSON con solo los campos a actualizar
    # (assigned_to, labels, status, contact_name); request.get_json() lo captura
    # Ejemplo: data = {'status': 'closed'} → cierra la conversación
    data = request.get_json()

    # [GUÍA 3 - ACTIVIDAD 1] if/elif anidados — construcción selectiva del update
    # Uso en CONNECTA: Solo los campos presentes en data se agregan al dict update;
    # permite PATCH parcial sin sobrescribir campos no enviados
    # Ejemplo: if 'status' in data → update['status'] = 'closed'
    update = {}

    if 'assigned_to' in data:
        update['assigned_to'] = data['assigned_to']
    if 'labels' in data:
        update['labels'] = data['labels']
    if 'status' in data:
        update['status'] = data['status']
    if 'contact_name' in data:
        update['contact_name'] = data['contact_name']

    if update:
        Conversation.update(conversation_id, update)

    updated = Conversation.find_by_id(conversation_id)

    from app.extensions import socketio
    from app.utils.helpers import serialize_doc as sd
    socketio.emit('conversation_updated', sd(updated))

    return jsonify(serialize_doc(updated))


@api_bp.route('/labels', methods=['GET'])
@login_required
def list_labels():
    labels = Label.list_all()
    return jsonify(serialize_docs(labels))


@api_bp.route('/labels', methods=['POST'])
@login_required
def create_label():
    """
    Create a new label for conversation categorization.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body de la request POST
    # Uso en CONNECTA: El usuario del dashboard envía {name, display_name, color}
    # para crear una nueva etiqueta de conversación
    # Ejemplo: data = {'name': 'VIP', 'display_name': 'Cliente VIP', 'color': '#FFD700'}
    data = request.get_json()

    # [GUÍA 2 - ACTIVIDAD 2] String manipulation — .strip(), .lower(), .replace()
    # Uso en CONNECTA: Normaliza el nombre de la etiqueta para almacenaje consistente;
    # 'Urgente ', 'URGENTE', 'urgente' → todos se guardan como 'urgente'
    # Ejemplo: '  VIP Cliente  '.strip().lower().replace(' ', '_') → 'vip_cliente'
    name = data.get('name', '').strip().lower().replace(' ', '_')
    display_name = data.get('display_name', '').strip()
    color = data.get('color', '#6B7280')

    # [GUÍA 3 - ACTIVIDAD 2] Operador lógico — not...or para validación doble
    # Uso en CONNECTA: Ambos campos son obligatorios; si cualquiera está vacío
    # después de normalizar, retorna 400 antes de tocar la base de datos
    # Ejemplo: if not name or not display_name → return error 400
    if not name or not display_name:
        return jsonify({'error': 'name and display_name are required'}), 400

    existing = Label.find_by_name(name)
    if existing:
        return jsonify({'error': 'Label already exists'}), 409

    label = Label.create(name, display_name, color)
    return jsonify(serialize_doc(label)), 201


@api_bp.route('/labels/<label_id>', methods=['DELETE'])
@login_required
def delete_label(label_id):
    label, err = get_or_404(Label, label_id)
    if err:
        return err
    Label.delete(label_id)
    return jsonify({'status': 'deleted'})


@api_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    from app.extensions import mongo
    users = list(mongo.db.users.find({'is_active': True}, {'password_hash': 0}))
    return jsonify(serialize_docs(users))
