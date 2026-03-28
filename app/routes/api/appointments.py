from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.appointment import Appointment
from app.models.pet import Pet
from app.utils.helpers import serialize_doc, serialize_docs
from datetime import datetime


@api_bp.route('/appointments', methods=['GET'])
@login_required
def list_appointments():
    """
    List all appointments with optional status filter.
    """
    status = request.args.get('status')
    appointments = Appointment.list_all(status)

    # [GUÍA 5 - ACTIVIDAD 5] Lista de diccionarios — citas enriquecidas con datos de mascota
    # Uso en CONNECTA: result es una lista donde cada elemento es un dict de cita
    # al que se le añade la clave 'pet' con los datos de la mascota embebidos
    # Ejemplo: [{'_id': '...', 'reason': 'Vacuna', 'pet': {'name': 'Luna', 'species': 'Perro'}}]
    result = []

    # [GUÍA 6 - ACTIVIDAD 3] Ciclo anidado — for sobre citas + find_one por mascota
    # Uso en CONNECTA: El ciclo externo recorre cada cita; internamente hace una
    # consulta a pets por cada cita (ciclo DB implícito) para enriquecer la respuesta
    # Ejemplo: for apt in appointments → pet = Pet.find_by_id(apt['pet_id']) → apt_dict['pet']=pet
    for apt in appointments:
        apt_dict = serialize_doc(apt)
        pet = Pet.find_by_id(str(apt['pet_id']))
        apt_dict['pet'] = serialize_doc(pet) if pet else None
        result.append(apt_dict)
    return jsonify(result)


@api_bp.route('/appointments/by-pet/<pet_id>', methods=['GET'])
@login_required
def list_appointments_by_pet(pet_id):
    """
    List appointment history for a specific pet.
    """
    appointments = Appointment.find_by_pet(pet_id)
    result = []

    # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — construcción de respuesta enriquecida
    # Uso en CONNECTA: Para el historial clínico de una mascota, cada cita
    # incluye sus propios datos de mascota para que el frontend no necesite
    # hacer una segunda llamada
    # Ejemplo: for apt in appointments → serializa y agrega datos de mascota
    for apt in appointments:
        apt_dict = serialize_doc(apt)
        pet = Pet.find_by_id(str(apt['pet_id']))
        apt_dict['pet'] = serialize_doc(pet) if pet else None
        result.append(apt_dict)
    return jsonify(result)


@api_bp.route('/appointments/<appointment_id>', methods=['GET'])
@login_required
def get_appointment(appointment_id):
    apt = Appointment.find_by_id(appointment_id)
    if not apt:
        return jsonify({'error': 'Not found'}), 404
    apt_dict = serialize_doc(apt)
    pet = Pet.find_by_id(str(apt['pet_id']))
    apt_dict['pet'] = serialize_doc(pet) if pet else None
    return jsonify(apt_dict)


@api_bp.route('/appointments', methods=['POST'])
@login_required
def create_appointment():
    """
    Create a new appointment for a pet.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body con datos de la cita
    # Uso en CONNECTA: El formulario de agendamiento envía pet_id, date, reason,
    # veterinarian; request.get_json() captura el payload completo
    # Ejemplo: data = {'pet_id': '64abc...', 'date': '2025-03-27T10:00', 'reason': 'Vacunación'}
    data = request.get_json()

    # [GUÍA 6 - ACTIVIDAD 1] Vector — lista de campos obligatorios para una cita
    # Uso en CONNECTA: Una cita requiere mínimo pet_id (qué mascota), date (cuándo)
    # y reason (por qué); sin estos no se puede agendar
    # Ejemplo: required = ['pet_id', 'date', 'reason']
    required = ['pet_id', 'date', 'reason']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # [GUÍA 3 - ACTIVIDAD 3] Validación — verificar que la mascota existe
    # Uso en CONNECTA: No se puede crear una cita para una mascota que no existe;
    # la validación previa evita referencias huérfanas en la colección appointments
    # Ejemplo: if not pet → return 404 'Pet not found'
    pet = Pet.find_by_id(data['pet_id'])
    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    # [GUÍA 4 - ACTIVIDAD 2] Casting de tipos — str ISO 8601 → datetime
    # Uso en CONNECTA: La fecha llega como string '2025-03-27T10:00:00' desde el
    # frontend; datetime.fromisoformat() la convierte al tipo datetime de Python
    # para almacenarla correctamente en MongoDB y poder hacer queries de rango
    # Ejemplo: datetime.fromisoformat('2025-03-27T10:00:00') → datetime(2025, 3, 27, 10, 0)
    try:
        date = datetime.fromisoformat(data['date'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400

    apt = Appointment.create(
        pet_id=data['pet_id'],
        date=date,
        reason=data['reason'],
        veterinarian=data.get('veterinarian', ''),
    )
    return jsonify(serialize_doc(apt)), 201


@api_bp.route('/appointments/<appointment_id>', methods=['PUT'])
@login_required
def update_appointment(appointment_id):
    apt = Appointment.find_by_id(appointment_id)
    if not apt:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json()
    update = {}

    # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — construcción del dict de update por campos permitidos
    # Uso en CONNECTA: Solo permite actualizar reason, veterinarian y status de una cita;
    # protege campos como pet_id y created_at de modificaciones accidentales
    # Ejemplo: for field in ['reason', 'veterinarian', 'status'] → if field in data → update[field]
    for field in ['reason', 'veterinarian', 'status']:
        if field in data:
            update[field] = data[field]

    # [GUÍA 4 - ACTIVIDAD 2] Casting de tipos — str → datetime para update de fecha
    # Uso en CONNECTA: Al reschedular una cita, la nueva fecha llega como string;
    # debe convertirse a datetime antes de guardarse en MongoDB
    # Ejemplo: data['date'] = '2025-04-01T09:00' → update['date'] = datetime(2025, 4, 1, 9, 0)
    if 'date' in data:
        try:
            update['date'] = datetime.fromisoformat(data['date'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format'}), 400

    if update:
        Appointment.update(appointment_id, update)

    return jsonify(serialize_doc(Appointment.find_by_id(appointment_id)))


@api_bp.route('/appointments/<appointment_id>', methods=['DELETE'])
@login_required
def delete_appointment(appointment_id):
    apt = Appointment.find_by_id(appointment_id)
    if not apt:
        return jsonify({'error': 'Not found'}), 404
    Appointment.delete(appointment_id)
    return jsonify({'status': 'deleted'}), 200
