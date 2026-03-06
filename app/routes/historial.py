from flask import Blueprint, request, jsonify

historial_bp = Blueprint('historial', __name__)


@historial_bp.route('/<mascota_id>', methods=['GET'])
def obtener_historial(mascota_id):
    """Obtiene el historial clínico de una mascota."""
    # TODO: consultar MongoDB por mascota_id
    return jsonify({'historial': []}), 200


@historial_bp.route('/<mascota_id>', methods=['POST'])
def agregar_registro(mascota_id):
    """Agrega un registro clínico al historial de una mascota."""
    data = request.get_json()
    # TODO: guardar registro en MongoDB
    return jsonify({'status': 'registro agregado'}), 201
