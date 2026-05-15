from flask import request, jsonify
from flask_login import login_required
from app.routes.api import api_bp
from app.models.pet import Pet
from app.utils.helpers import serialize_doc, serialize_docs, get_or_404, validar_campos_requeridos


@api_bp.route('/pets', methods=['GET'])
@login_required
def list_pets():
    # [GUÍA 9 - ACTIVIDAD 3] Pet.list_all() retorna List[Pet]; .to_dict() serializa cada instancia
    pets = Pet.list_all()
    return jsonify([p.to_dict() for p in pets])


@api_bp.route('/pets/by-phone/<phone>', methods=['GET'])
@login_required
def list_pets_by_phone(phone):
    """
    List pets belonging to a specific phone number.
    """
    # [GUÍA 9 - ACTIVIDAD 3] find_by_owner_phone retorna List[Pet]
    pets = Pet.find_by_owner_phone(phone)
    return jsonify([p.to_dict() for p in pets])


@api_bp.route('/pets/<pet_id>', methods=['GET'])
@login_required
def get_pet(pet_id):
    # [GUÍA 9 - ACTIVIDAD 3] get_or_404 retorna instancia Pet (via find_by_id → from_db)
    pet, err = get_or_404(Pet, pet_id)
    if err:
        return err
    return jsonify(pet.to_dict())


@api_bp.route('/pets', methods=['POST'])
@login_required
def create_pet():
    """
    Create a new pet record.
    """
    # [GUÍA 4 - ACTIVIDAD 1] Captura de datos — JSON body con datos de la mascota
    data = request.get_json()

    # [GUÍA 7 - ACTIVIDAD 1] validar_campos_requeridos: subalgorithm reutilizable
    campo_faltante = validar_campos_requeridos(data, ['name', 'species', 'owner_phone'])
    if campo_faltante:
        return jsonify({'error': f'{campo_faltante} is required'}), 400

    # [GUÍA 9 - ACTIVIDAD 3] Pet.create() retorna instancia Pet; .to_dict() serializa
    pet = Pet.create(
        name=data['name'],
        species=data['species'],
        breed=data.get('breed', ''),
        age_years=data.get('age_years', 0),
        weight_kg=data.get('weight_kg', 0),
        owner_phone=data['owner_phone'],
        owner_name=data.get('owner_name', ''),
    )
    return jsonify(pet.to_dict()), 201


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

    # [GUÍA 7 - ACTIVIDAD 2] filter + lambda: construye el dict de update de forma funcional
    campos_permitidos = ['name', 'species', 'breed', 'age_years', 'weight_kg', 'owner_phone', 'owner_name']
    update = {c: data[c] for c in filter(lambda c: c in data, campos_permitidos)}

    if update:
        Pet.update(pet_id, update)

    # [GUÍA 9 - ACTIVIDAD 3] find_by_id retorna instancia Pet actualizada
    return jsonify(Pet.find_by_id(pet_id).to_dict())


@api_bp.route('/pets/<pet_id>', methods=['DELETE'])
@login_required
def delete_pet(pet_id):
    pet, err = get_or_404(Pet, pet_id)
    if err:
        return err
    Pet.delete(pet_id)
    return jsonify({'status': 'deleted'}), 200


@api_bp.route('/pets/export/csv', methods=['GET'])
@login_required
def export_pets_csv():
    """
    # [GUÍA 8 - ACTIVIDAD 2]
    Endpoint REST que exporta todas las mascotas a CSV y retorna confirmación JSON.
    """
    from app.utils.persistence import exportar_mascotas_csv

    # [GUÍA 9 - ACTIVIDAD 3] Pet.list_all() + to_dict() reemplaza la consulta directa
    # a mongo y el loop manual de str(_id) para serialización
    mascotas = [p.to_dict() for p in Pet.list_all()]

    ok = exportar_mascotas_csv(mascotas)
    return jsonify({
        'ok': ok,
        'mensaje': 'Exportación completada' if ok else 'Error en la exportación',
        'total': len(mascotas)
    })
