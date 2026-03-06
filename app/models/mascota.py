from app.extensions import mongo
from datetime import datetime


def crear_mascota(nombre, especie, raza, propietario_telefono):
    mascota = {
        'nombre': nombre,
        'especie': especie,
        'raza': raza,
        'propietario_telefono': propietario_telefono,
        'creado_en': datetime.utcnow()
    }
    resultado = mongo.db.mascotas.insert_one(mascota)
    return str(resultado.inserted_id)


def obtener_mascota_por_telefono(telefono):
    return mongo.db.mascotas.find_one({'propietario_telefono': telefono})
