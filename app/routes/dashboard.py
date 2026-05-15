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


@dashboard_bp.route('/')
@login_required
def index():
    """
    Render the dashboard home page with aggregated metrics.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # [GUÍA 2 - ACTIVIDAD 4] Operadores aritméticos — cálculo de inicio de semana
    week_start = today_start - timedelta(days=today_start.weekday())

    # Main stats
    open_conversations = mongo.db.conversations.count_documents({'status': 'open'})
    total_conversations = mongo.db.conversations.count_documents({})
    today_appointments = len(Appointment.list_today())

    # [GUÍA 2 - ACTIVIDAD 1] Variables int — contadores de métricas del dashboard
    total_pets = mongo.db.pets.count_documents({})
    messages_today = mongo.db.messages.count_documents({'timestamp': {'$gte': today_start}})
    messages_week = mongo.db.messages.count_documents({'timestamp': {'$gte': week_start}})

    inbound_today = mongo.db.messages.count_documents({
        'timestamp': {'$gte': today_start},
        'direction': 'inbound',
    })
    outbound_today = mongo.db.messages.count_documents({
        'timestamp': {'$gte': today_start},
        'direction': 'outbound',
    })

    # [GUÍA 2 - ACTIVIDAD 5] Operador de comparación — $gt (mayor que)
    unread_conversations = mongo.db.conversations.count_documents({'unread_count': {'$gt': 0}})

    scheduled_appointments = mongo.db.appointments.count_documents({'status': 'scheduled'})
    confirmed_appointments = mongo.db.appointments.count_documents({'status': 'confirmed'})
    completed_today = mongo.db.appointments.count_documents({
        'status': 'completed',
        'date': {'$gte': today_start},
    })

    # [GUÍA 9 - ACTIVIDAD 3] Conversation.list_all() retorna List[Conversation];
    # se limita con .find directamente para mantener la paginación eficiente.
    # [GUÍA 2 - ACTIVIDAD 3] Lista de conversaciones recientes
    recent_convs_docs = list(
        mongo.db.conversations
        .find({'status': 'open'})
        .sort('last_message.timestamp', -1)
        .limit(5)
    )
    # [GUÍA 9 - ACTIVIDAD 3] from_db convierte cada doc en instancia Conversation
    # [GUÍA 7 - ACTIVIDAD 2] map + método: reemplaza el for-loop de serialización
    recent_conversations = list(map(
        lambda doc: Conversation.from_db(doc).to_dict(), recent_convs_docs
    ))

    # [GUÍA 5 - ACTIVIDAD 5] Lista de citas enriquecidas con datos de mascota
    upcoming_apts_docs = list(
        mongo.db.appointments
        .find({'status': {'$in': ['scheduled', 'confirmed']}, 'date': {'$gte': now}})
        .sort('date', 1)
        .limit(5)
    )
    # [GUÍA 9 - ACTIVIDAD 3] from_db → instancia → enriquecer_dashboard() (método migrado)
    # [GUÍA 7 - ACTIVIDAD 2] map + método de instancia: reemplaza _enriquecer_cita_dashboard()
    upcoming_appointments = list(map(
        lambda doc: Appointment.from_db(doc).enriquecer_dashboard(),
        upcoming_apts_docs
    ))

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
