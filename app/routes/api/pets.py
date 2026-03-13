from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.pet import Pet
from app.utils.helpers import serialize_doc, serialize_docs


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

    Concept Validation: Phone number links WhatsApp contact to their pets.
    """
    pets = Pet.find_by_owner_phone(phone)
    return jsonify(serialize_docs(pets))


@api_bp.route('/pets/<pet_id>', methods=['GET'])
@login_required
def get_pet(pet_id):
    pet = Pet.find_by_id(pet_id)
    if not pet:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(serialize_doc(pet))


@api_bp.route('/pets', methods=['POST'])
@login_required
def create_pet():
    """
    Create a new pet record.

    List: required list defines mandatory fields, iterated for validation.
    Dynamic Input: All fields come from JSON request body.
    """
    data = request.get_json()
    # List: required list defines mandatory fields, iterated for validation
    required = ['name', 'species', 'owner_phone']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    # Dynamic Input: All fields come from JSON request body
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

    List: Iterates over allowed field names to build update dict.
    """
    pet = Pet.find_by_id(pet_id)
    if not pet:
        return jsonify({'error': 'Not found'}), 404

    data = request.get_json()
    update = {}
    # List: Iterates over allowed field names to build update dict
    for field in ['name', 'species', 'breed', 'age_years', 'weight_kg', 'owner_phone', 'owner_name']:
        if field in data:
            update[field] = data[field]

    if update:
        Pet.update(pet_id, update)

    return jsonify(serialize_doc(Pet.find_by_id(pet_id)))


@api_bp.route('/pets/<pet_id>', methods=['DELETE'])
@login_required
def delete_pet(pet_id):
    pet = Pet.find_by_id(pet_id)
    if not pet:
        return jsonify({'error': 'Not found'}), 404
    Pet.delete(pet_id)
    return jsonify({'status': 'deleted'}), 200
