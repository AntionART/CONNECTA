from flask import request, jsonify
from flask_login import login_required, current_user
from app.routes.api import api_bp
from app.models.conversation import Conversation
from app.models.label import Label
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404


# [GUÍA 4 - ACTIVIDAD 1] Captura de datos — query params de la request HTTP
@api_bp.route('/conversations', methods=['GET'])
@login_required
def list_conversations():
    """
    List all conversations with optional filtering.
    """
    # [GUÍA 5 - ACTIVIDAD 4] Diccionario — construcción de filtros desde query params
    filters = {
        'status': request.args.get('status'),
        'assigned_to': request.args.get('assigned_to'),
        'label': request.args.get('label'),
    }
    # [GUÍA 9 - ACTIVIDAD 3] list_all() retorna List[Conversation]; .to_dict() serializa
    conversations = Conversation.list_all(filters)
    return jsonify([c.to_dict() for c in conversations])


@api_bp.route('/conversations/<conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    # [GUÍA 9 - ACTIVIDAD 3] get_or_404 retorna instancia Conversation
    conv, err = get_or_404(Conversation, conversation_id)
    if err:
        return err
    Conversation.reset_unread(conversation_id)
    return jsonify(conv.to_dict())


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
    data = request.get_json()

    # [GUÍA 3 - ACTIVIDAD 1] if/elif — construcción selectiva del update
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

    # [GUÍA 9 - ACTIVIDAD 3] find_by_id retorna instancia Conversation actualizada
    updated = Conversation.find_by_id(conversation_id)

    from app.extensions import socketio
    socketio.emit('conversation_updated', updated.to_dict())

    return jsonify(updated.to_dict())


@api_bp.route('/labels', methods=['GET'])
@login_required
def list_labels():
    # Label no se refactorizó a OOP (entidad auxiliar sin comportamiento propio)
    # serialize_docs se mantiene para dicts crudos de MongoDB
    labels = Label.list_all()
    return jsonify(serialize_docs(labels))


@api_bp.route('/labels', methods=['POST'])
@login_required
def create_label():
    """
    Create a new label for conversation categorization.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body de la request POST
    data = request.get_json()

    # [GUÍA 2 - ACTIVIDAD 2] String manipulation — .strip(), .lower(), .replace()
    name = data.get('name', '').strip().lower().replace(' ', '_')
    display_name = data.get('display_name', '').strip()
    color = data.get('color', '#6B7280')

    # [GUÍA 3 - ACTIVIDAD 2] Operador lógico — not...or para validación doble
    if not name or not display_name:
        return jsonify({'error': 'name and display_name are required'}), 400

    existing = Label.find_by_name(name)
    if existing:
        return jsonify({'error': 'Label already exists'}), 409

    # Label.create() retorna dict crudo (no refactorizado) — serialize_doc aplica
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
