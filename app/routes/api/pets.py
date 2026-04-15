from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.pet import Pet
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404, validar_campos_requeridos


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

    # [GUÍA 7 - ACTIVIDAD 1] validar_campos_requeridos: reemplaza el for+if de validación
    # Uso en CONNECTA: Centraliza la lógica de validación de campos obligatorios;
    # retorna el primer campo faltante o None si todo está OK.
    # Ejemplo: validar_campos_requeridos(data, ['name','species','owner_phone']) → 'species'
    campo_faltante = validar_campos_requeridos(data, ['name', 'species', 'owner_phone'])
    if campo_faltante:
        return jsonify({'error': f'{campo_faltante} is required'}), 400

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

    # [GUÍA 7 - ACTIVIDAD 2] filter + lambda: construye el dict de update de forma funcional
    # filter(lambda c: c in data, campos_permitidos) → solo los campos que llegaron en el payload
    # El dict comprehension los extrae: protege campos internos (created_at, _id) sin for explícito.
    # Ejemplo: data={'name':'Max','created_at':'...'} → update={'name':'Max'} (created_at ignorado)
    campos_permitidos = ['name', 'species', 'breed', 'age_years', 'weight_kg', 'owner_phone', 'owner_name']
    update = {c: data[c] for c in filter(lambda c: c in data, campos_permitidos)}

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
