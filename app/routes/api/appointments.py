from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.appointment import Appointment
from app.models.pet import Pet
from app.utils.helpers import get_or_404, validar_campos_requeridos
from datetime import datetime


# [GUÍA 9 - ACTIVIDAD 3] _enrich_appointment eliminado: su lógica migró al método
# Appointment.enriquecer_api() en app/models/appointment.py (Actividad 2).
# La función era transversal a la ruta, ahora es comportamiento del objeto Appointment.


@api_bp.route('/appointments', methods=['GET'])
@login_required
def list_appointments():
    """
    List all appointments with optional status filter.
    """
    status = request.args.get('status')
    # [GUÍA 9 - ACTIVIDAD 3] Appointment.list_all() retorna List[Appointment]
    appointments = Appointment.list_all(status)

    # [GUÍA 9 - ACTIVIDAD 3] .enriquecer_api() invoca el método del objeto
    # (migrado desde _enrich_appointment) en lugar de una función suelta
    # [GUÍA 5 - ACTIVIDAD 5] Lista de dicts enriquecidos con datos de mascota
    # [GUÍA 6 - ACTIVIDAD 3] Ciclo anidado — enriquecer_api() hace lookup interno de pet
    return jsonify([apt.enriquecer_api() for apt in appointments])


@api_bp.route('/appointments/by-pet/<pet_id>', methods=['GET'])
@login_required
def list_appointments_by_pet(pet_id):
    """
    List appointment history for a specific pet.
    """
    appointments = Appointment.find_by_pet(pet_id)
    return jsonify([apt.enriquecer_api() for apt in appointments])


@api_bp.route('/appointments/<appointment_id>', methods=['GET'])
@login_required
def get_appointment(appointment_id):
    apt, err = get_or_404(Appointment, appointment_id)
    if err:
        return err
    return jsonify(apt.enriquecer_api())


@api_bp.route('/appointments', methods=['POST'])
@login_required
def create_appointment():
    """
    Create a new appointment for a pet.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body con datos de la cita
    data = request.get_json()

    # [GUÍA 7 - ACTIVIDAD 1] validar_campos_requeridos: subalgorithm reutilizado
    campo_faltante = validar_campos_requeridos(data, ['pet_id', 'date', 'reason'])
    if campo_faltante:
        return jsonify({'error': f'{campo_faltante} is required'}), 400

    # [GUÍA 3 - ACTIVIDAD 3] Validación — mascota debe existir
    # [GUÍA 9 - ACTIVIDAD 3] Pet.find_by_id() retorna instancia Pet (o None)
    pet = Pet.find_by_id(data['pet_id'])
    if not pet:
        return jsonify({'error': 'Pet not found'}), 404

    # [GUÍA 4 - ACTIVIDAD 2] Casting — str ISO 8601 → datetime
    try:
        date = datetime.fromisoformat(data['date'])
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format'}), 400

    # [GUÍA 9 - ACTIVIDAD 3] Appointment.create() retorna instancia Appointment
    apt = Appointment.create(
        pet_id=data['pet_id'],
        date=date,
        reason=data['reason'],
        veterinarian=data.get('veterinarian', ''),
    )
    return jsonify(apt.to_dict()), 201


@api_bp.route('/appointments/<appointment_id>', methods=['PUT'])
@login_required
def update_appointment(appointment_id):
    apt, err = get_or_404(Appointment, appointment_id)
    if err:
        return err

    data = request.get_json()

    # [GUÍA 7 - ACTIVIDAD 2] filter + lambda: construye update dict de forma funcional
    update = {c: data[c] for c in filter(lambda c: c in data, ['reason', 'veterinarian', 'status'])}

    # [GUÍA 4 - ACTIVIDAD 2] Casting — str → datetime para update de fecha
    if 'date' in data:
        try:
            update['date'] = datetime.fromisoformat(data['date'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format'}), 400

    if update:
        Appointment.update(appointment_id, update)

    # [GUÍA 9 - ACTIVIDAD 3] find_by_id retorna instancia Appointment actualizada
    return jsonify(Appointment.find_by_id(appointment_id).to_dict())


@api_bp.route('/appointments/<appointment_id>', methods=['DELETE'])
@login_required
def delete_appointment(appointment_id):
    apt, err = get_or_404(Appointment, appointment_id)
    if err:
        return err
    Appointment.delete(appointment_id)
    return jsonify({'status': 'deleted'}), 200
