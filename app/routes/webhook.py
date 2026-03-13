from flask import Blueprint, request, jsonify

webhook_bp = Blueprint('webhook', __name__)


@webhook_bp.route('/', methods=['POST'])
def recibir_mensaje():
    """Recibe mensajes entrantes desde Evolution API."""
    data = request.get_json()
    # TODO: procesar mensaje con servicio NLP
    return jsonify({'status': 'recibido'}), 200
