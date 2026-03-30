from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.pet import Pet
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404


@api_bp.route('/pets', methods=['GET'])
@login_required
def list_pets():
    pets = Pet.list_all()
    return jsonify(serialize_docs(pets))


@api_bp.route('/pets/by-phone/<phone>', methods=['GET'])
@login_required
def list_pets_by_phone(phone):
    """
    List pets belonging to a specific phone number.
    """
    pets = Pet.find_by_owner_phone(phone)
    return jsonify(serialize_docs(pets))


@api_bp.route('/pets/<pet_id>', methods=['GET'])
@login_required
def get_pet(pet_id):
    pet, err = get_or_404(Pet, pet_id)
    if err:
        return err
    return jsonify(serialize_doc(pet))


@api_bp.route('/pets', methods=['POST'])
@login_required
def create_pet():
    """
    Create a new pet record.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body con datos de la mascota
    # Uso en CONNECTA: El formulario del dashboard envía name, species, breed,
    # age_years, weight_kg, owner_phone; request.get_json() los captura
    # Ejemplo: data = {'name': 'Luna', 'species': 'Perro', 'owner_phone': '573001234567'}
    data = request.get_json()

    # [GUÍA 6 - ACTIVIDAD 1] Vector — lista 1D de campos obligatorios
    # Uso en CONNECTA: required define los 3 campos mínimos sin los cuales
    # no se puede crear una mascota; se itera para validar cada uno
    # Ejemplo: required = ['name', 'species', 'owner_phone']
    required = ['name', 'species', 'owner_phone']

    # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — validación de campos requeridos
    # Uso en CONNECTA: Itera el vector required; si cualquier campo falta en data
    # retorna 400 con el nombre del campo faltante en el mensaje de error
    # Ejemplo: for field in required → if not data.get('name') → return 400 'name is required'
    for field in required:
        if not data.get(field):
            # [GUÍA 4 - ACTIVIDAD 3] F-string en mensaje de error dinámico
            # Uso en CONNECTA: El nombre del campo faltante se embebe en el error
            # para que el frontend pueda mostrar exactamente qué hace falta
            # Ejemplo: f'{field} is required' → 'species is required'
            return jsonify({'error': f'{field} is required'}), 400

    pet = Pet.create(
        name=data['name'],
        species=data['species'],
        breed=data.get('breed', ''),
        age_years=data.get('age_years', 0),
        weight_kg=data.get('weight_kg', 0),
        owner_phone=data['owner_phone'],
        owner_name=data.get('owner_name', ''),
    )
    return jsonify(serialize_doc(pet)), 201


@api_bp.route('/pets/<pet_id>', methods=['PUT'])
@login_required
def update_pet(pet_id):
    """
    Update an existing pet record.
    """
    pet, err = get_or_404(Pet, pet_id)
    if err:
        return err

    data = request.get_json()
    update = {}

    # [GUÍA 6 - ACTIVIDAD 1] Vector — lista 1D de campos actualizables
    # Uso en CONNECTA: allowed_fields define exactamente qué campos del modelo
    # Pet puede actualizar el usuario; evita que envíen campos no autorizados
    # Ejemplo: ['name', 'species', 'breed', 'age_years', 'weight_kg', 'owner_phone', 'owner_name']

    # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — construcción selectiva del dict de update
    # Uso en CONNECTA: Solo los campos que el cliente envió Y que están en la lista
    # se incluyen en el update; protege campos internos como created_at
    # Ejemplo: data={'name':'Max', 'age_years':3} → update={'name':'Max', 'age_years':3}
    for field in ['name', 'species', 'breed', 'age_years', 'weight_kg', 'owner_phone', 'owner_name']:
        if field in data:
            update[field] = data[field]

    if update:
        Pet.update(pet_id, update)

    return jsonify(serialize_doc(Pet.find_by_id(pet_id)))


@api_bp.route('/pets/<pet_id>', methods=['DELETE'])
@login_required
def delete_pet(pet_id):
    pet, err = get_or_404(Pet, pet_id)
    if err:
        return err
    Pet.delete(pet_id)
    return jsonify({'status': 'deleted'}), 200
