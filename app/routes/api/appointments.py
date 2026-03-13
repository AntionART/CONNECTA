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

    Nested Loop: For each appointment, fetches associated pet (loop + DB query).
    Professional Output: Each appointment includes embedded pet data.
    """
    status = request.args.get('status')
    appointments = Appointment.list_all(status)
    result = []
    # Nested Loop: For each appointment, fetches associated pet (loop + DB query)
    for apt in appointments:
        apt_dict = serialize_doc(apt)
        pet = Pet.find_by_id(str(apt['pet_id']))
        # Professional Output: Each appointment includes embedded pet data
        apt_dict['pet'] = serialize_doc(pet) if pet else None
        result.append(apt_dict)
    return jsonify(result)


@api_bp.route('/appointments/by-pet/<pet_id>', methods=['GET'])
@login_required
def list_appointments_by_pet(pet_id):
    """
    List appointment history for a specific pet.

    Business Rule: Returns appointment history for a specific pet.
    """
    appointments = Appointment.find_by_pet(pet_id)
    result = []
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

    Concept Validation: Validates pet exists before creating appointment.
    Dynamic Input: Date parsed from ISO format string.
    """
    data = request.get_json()
    required = ['pet_id', 'date', 'reason']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Concept Validation: Validates pet exists before creating appointment
    pet = Pet.find_by_id(data['pet_id'])
    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    # Dynamic Input: Date parsed from ISO format string
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
    for field in ['reason', 'veterinarian', 'status']:
        if field in data:
            update[field] = data[field]
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
