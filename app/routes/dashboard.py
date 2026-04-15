"""
Dashboard route — aggregates metrics from all collections for the home page.
"""
from flask import Blueprint, render_template
from flask_login import login_required
from app.models.conversation import Conversation
from app.models.appointment import Appointment
from app.extensions import mongo
from datetime import datetime, timezone, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


# [GUÍA 7 - ACTIVIDAD 1] - Subalgorithm: enriquece una cita con el nombre de su mascota
def _enriquecer_cita_dashboard(apt):
    """
    Serializa el _id de una cita y embebe el nombre de la mascota asociada.
    Extrae la lógica inline del for-loop del dashboard en una función de
    responsabilidad única, reutilizable con map().

    Params:
        apt (dict): Documento de cita de MongoDB (upcoming_appointments)

    Returns:
        dict: Cita con _id y pet_id serializados y campo pet_name agregado
    """
    pet = mongo.db.pets.find_one({'_id': apt['pet_id']})
    return {
        **apt,
        '_id': str(apt['_id']),
        'pet_id': str(apt['pet_id']),
        'pet_name': pet['name'] if pet else 'Desconocida',
    }


@dashboard_bp.route('/')
@login_required
def index():
    """
    Render the dashboard home page with aggregated metrics.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # [GUÍA 2 - ACTIVIDAD 4] Operadores aritméticos — cálculo de inicio de semana
    # Uso en CONNECTA: Resta los días transcurridos desde el lunes para obtener
    # week_start y calcular estadísticas semanales de mensajes
    # Ejemplo: hoy=miércoles (weekday=2) → week_start = hoy - 2 días = lunes
    week_start = today_start - timedelta(days=today_start.weekday())

    # Main stats
    open_conversations = mongo.db.conversations.count_documents({'status': 'open'})
    total_conversations = mongo.db.conversations.count_documents({})
    today_appointments = len(Appointment.list_today())

    # [GUÍA 2 - ACTIVIDAD 1] Variables int — contadores de métricas del dashboard
    # Uso en CONNECTA: total_pets, messages_today, messages_week son int que
    # se pasan al template para renderizar tarjetas de estadísticas
    # Ejemplo: total_pets = 42, messages_today = 17, messages_week = 95
    total_pets = mongo.db.pets.count_documents({})
    messages_today = mongo.db.messages.count_documents({'timestamp': {'$gte': today_start}})
    messages_week = mongo.db.messages.count_documents({'timestamp': {'$gte': week_start}})

    # Inbound vs outbound today
    inbound_today = mongo.db.messages.count_documents({
        'timestamp': {'$gte': today_start},
        'direction': 'inbound',
    })
    outbound_today = mongo.db.messages.count_documents({
        'timestamp': {'$gte': today_start},
        'direction': 'outbound',
    })

    # Unread conversations
    # [GUÍA 2 - ACTIVIDAD 5] Operador de comparación — $gt (mayor que)
    # Uso en CONNECTA: Filtra conversaciones con unread_count > 0
    # para mostrar el badge de "pendientes" en el sidebar
    # Ejemplo: {'unread_count': {'$gt': 0}} → conversaciones sin leer
    unread_conversations = mongo.db.conversations.count_documents({'unread_count': {'$gt': 0}})

    # Appointments by status
    scheduled_appointments = mongo.db.appointments.count_documents({'status': 'scheduled'})
    confirmed_appointments = mongo.db.appointments.count_documents({'status': 'confirmed'})
    completed_today = mongo.db.appointments.count_documents({
        'status': 'completed',
        'date': {'$gte': today_start},
    })

    # [GUÍA 2 - ACTIVIDAD 3] Lista — conversaciones recientes como array Python
    # Uso en CONNECTA: Las 5 últimas conversaciones abiertas se guardan en lista
    # para iterar en el template y renderizar las tarjetas del dashboard
    # Ejemplo: recent_conversations = [{'phone_number': '573...', 'contact_name': 'Ana'}, ...]
    recent_conversations = list(
        mongo.db.conversations
        .find({'status': 'open'})
        .sort('last_message.timestamp', -1)
        .limit(5)
    )

    # [GUÍA 7 - ACTIVIDAD 2] map + lambda: serializa _id de cada conversación
    # Reemplaza el for-loop de mutación por una transformación funcional pura.
    # Ventaja: no muta los dicts originales — retorna nuevos dicts con _id como str.
    # Ejemplo: lambda c: {**c, '_id': str(c['_id'])} → copia el dict cambiando solo _id
    recent_conversations = list(map(
        lambda c: {**c, '_id': str(c['_id'])}, recent_conversations
    ))

    # [GUÍA 5 - ACTIVIDAD 5] Lista de diccionarios — citas enriquecidas con datos de mascota
    # Uso en CONNECTA: Cada cita en upcoming_appointments es un dict que se
    # enriquece con pet_name para mostrarlo en la tabla del dashboard sin un join SQL
    # Ejemplo: [{'_id': '...', 'reason': 'Vacuna', 'pet_name': 'Luna'}, ...]
    upcoming_appointments = list(
        mongo.db.appointments
        .find({'status': {'$in': ['scheduled', 'confirmed']}, 'date': {'$gte': now}})
        .sort('date', 1)
        .limit(5)
    )

    # [GUÍA 7 - ACTIVIDAD 2] map + función modular: reemplaza el for-loop anidado
    # _enriquecer_cita_dashboard encapsula la lógica (serializar + buscar mascota);
    # map la aplica a cada cita sin mutar la lista original elemento por elemento.
    # Ejemplo: map(_enriquecer_cita_dashboard, upcoming_appointments)
    #          → cada apt sale con _id:str, pet_id:str y pet_name embebido
    upcoming_appointments = list(map(_enriquecer_cita_dashboard, upcoming_appointments))

    return render_template(
        'dashboard/index.html',
        open_conversations=open_conversations,
        total_conversations=total_conversations,
        today_appointments=today_appointments,
        total_pets=total_pets,
        messages_today=messages_today,
        messages_week=messages_week,
        inbound_today=inbound_today,
        outbound_today=outbound_today,
        unread_conversations=unread_conversations,
        scheduled_appointments=scheduled_appointments,
        confirmed_appointments=confirmed_appointments,
        completed_today=completed_today,
        recent_conversations=recent_conversations,
        upcoming_appointments=upcoming_appointments,
    )
