from flask import request, jsonify
from flask_login import login_required, current_user
from app.routes.api import api_bp
from app.models.conversation import Conversation
from app.models.label import Label
from app.utils.helpers import serialize_doc, serialize_docs


@api_bp.route('/conversations', methods=['GET'])
@login_required
def list_conversations():
    """
    List all conversations with optional filtering.

    Dynamic Input: Filters from query params (status, assigned_to, label).
    List: Returns JSON array of conversation documents.
    """
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
    conv = Conversation.find_by_id(conversation_id)
    if not conv:
        return jsonify({'error': 'Not found'}), 404
    Conversation.reset_unread(conversation_id)
    return jsonify(serialize_doc(conv))


@api_bp.route('/conversations/<conversation_id>', methods=['PATCH'])
@login_required
def update_conversation(conversation_id):
    """
    Partially update a conversation's metadata.

    Nested Logic: Conditionally builds update dict based on provided fields.
    Business Rule: Emits SocketIO event so all connected clients see the change in real-time.
    """
    conv = Conversation.find_by_id(conversation_id)
    if not conv:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json()
    # Nested Logic: Conditionally builds update dict based on provided fields
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

    # Business Rule: Emits SocketIO event so all connected clients see the change in real-time
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

    Syntax & Variables: name is normalized (lowercase, underscores) from display_name.
    Business Rule: Prevents duplicate labels (checks existing before insert).
    """
    data = request.get_json()
    # Syntax & Variables: name is normalized (lowercase, underscores) from display_name
    name = data.get('name', '').strip().lower().replace(' ', '_')
    display_name = data.get('display_name', '').strip()
    color = data.get('color', '#6B7280')

    if not name or not display_name:
        return jsonify({'error': 'name and display_name are required'}), 400

    # Business Rule: Prevents duplicate labels (checks existing before insert)
    existing = Label.find_by_name(name)
    if existing:
        return jsonify({'error': 'Label already exists'}), 409

    label = Label.create(name, display_name, color)
    return jsonify(serialize_doc(label)), 201


@api_bp.route('/labels/<label_id>', methods=['DELETE'])
@login_required
def delete_label(label_id):
    label = Label.find_by_id(label_id)
    if not label:
        return jsonify({'error': 'Not found'}), 404
    Label.delete(label_id)
    return jsonify({'status': 'deleted'})


@api_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    from app.extensions import mongo
    users = list(mongo.db.users.find({'is_active': True}, {'password_hash': 0}))
    return jsonify(serialize_docs(users))
