from app.extensions import mongo
from datetime import datetime


def crear_cita(mascota_id, fecha, motivo, veterinario=None):
    cita = {
        'mascota_id': mascota_id,
        'fecha': fecha,
        'motivo': motivo,
        'veterinario': veterinario,
        'estado': 'pendiente',
        'creado_en': datetime.utcnow()
    }
    resultado = mongo.db.citas.insert_one(cita)
    return str(resultado.inserted_id)


def listar_citas_por_mascota(mascota_id):
    return list(mongo.db.citas.find({'mascota_id': mascota_id}))
