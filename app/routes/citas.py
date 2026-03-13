from flask import Blueprint, request, jsonify

citas_bp = Blueprint('citas', __name__)


@citas_bp.route('/', methods=['GET'])
def listar_citas():
    """Lista todas las citas agendadas."""
    # TODO: consultar MongoDB
    return jsonify({'citas': []}), 200


@citas_bp.route('/', methods=['POST'])
def agendar_cita():
    """Agenda una nueva cita."""
    data = request.get_json()
    # TODO: guardar cita en MongoDB y enviar confirmación por WhatsApp
    return jsonify({'status': 'cita agendada'}), 201
