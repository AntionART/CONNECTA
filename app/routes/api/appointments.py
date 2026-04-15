from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.appointment import Appointment
from app.models.pet import Pet
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404, validar_campos_requeridos
from datetime import datetime


def _enrich_appointment(apt):
    """Serializa una cita y embebe los datos de su mascota."""
    apt_dict = serialize_doc(apt)
    pet = Pet.find_by_id(str(apt['pet_id']))
    apt_dict['pet'] = serialize_doc(pet) if pet else None
    return apt_dict


@api_bp.route('/appointments', methods=['GET'])
@login_required
def list_appointments():
    """
    List all appointments with optional status filter.
    """
    status = request.args.get('status')
    appointments = Appointment.list_all(status)

    # [GUÍA 5 - ACTIVIDAD 5] Lista de diccionarios — citas enriquecidas con datos de mascota
    # [GUÍA 6 - ACTIVIDAD 3] Ciclo anidado — for + consulta DB por mascota en _enrich_appointment
    return jsonify([_enrich_appointment(apt) for apt in appointments])


@api_bp.route('/appointments/by-pet/<pet_id>', methods=['GET'])
@login_required
def list_appointments_by_pet(pet_id):
    """
    List appointment history for a specific pet.
    """
    appointments = Appointment.find_by_pet(pet_id)
    return jsonify([_enrich_appointment(apt) for apt in appointments])


@api_bp.route('/appointments/<appointment_id>', methods=['GET'])
@login_required
def get_appointment(appointment_id):
    apt, err = get_or_404(Appointment, appointment_id)
    if err:
        return err
    return jsonify(_enrich_appointment(apt))


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

    # [GUÍA 7 - ACTIVIDAD 1] validar_campos_requeridos: subalgorithm reutilizado desde helpers
    # Mismo patrón que pets.py — un solo punto de cambio si los requisitos varían.
    # Ejemplo: validar_campos_requeridos(data, ['pet_id','date','reason']) → 'date' si falta
    campo_faltante = validar_campos_requeridos(data, ['pet_id', 'date', 'reason'])
    if campo_faltante:
        return jsonify({'error': f'{campo_faltante} is required'}), 400

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
    apt, err = get_or_404(Appointment, appointment_id)
    if err:
        return err

    data = request.get_json()
    update = {}

    # [GUÍA 7 - ACTIVIDAD 2] filter + lambda: construye update dict de forma funcional
    # Idéntico al patrón de pets.py — filter selecciona solo campos presentes en el payload.
    # Ejemplo: data={'status':'confirmed','pet_id':'...'} → update={'status':'confirmed'}
    update = {c: data[c] for c in filter(lambda c: c in data, ['reason', 'veterinarian', 'status'])}

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
    apt, err = get_or_404(Appointment, appointment_id)
    if err:
        return err
    Appointment.delete(appointment_id)
    return jsonify({'status': 'deleted'}), 200
