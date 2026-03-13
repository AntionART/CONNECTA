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

    Arithmetic Logic: week_start = today - timedelta(days=weekday) calculates Monday.
    List: recent_conversations is a list of the 5 most recent open conversations.
    Nested Loop: Iterates upcoming_appointments and enriches each with pet_name (loop + DB lookup).
    Data Structure: Each appointment dict is augmented with pet_name field.
    Professional Output: Passes 15+ context variables to the template.
    Bilingualism: Variable names in English, displayed labels in Spanish via template.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Arithmetic Logic: week_start = today - timedelta(days=weekday) calculates Monday
    week_start = today_start - timedelta(days=today_start.weekday())

    # Main stats
    open_conversations = mongo.db.conversations.count_documents({'status': 'open'})
    total_conversations = mongo.db.conversations.count_documents({})
    today_appointments = len(Appointment.list_today())
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
    unread_conversations = mongo.db.conversations.count_documents({'unread_count': {'$gt': 0}})

    # Appointments by status
    scheduled_appointments = mongo.db.appointments.count_documents({'status': 'scheduled'})
    confirmed_appointments = mongo.db.appointments.count_documents({'status': 'confirmed'})
    completed_today = mongo.db.appointments.count_documents({
        'status': 'completed',
        'date': {'$gte': today_start},
    })

    # List: recent_conversations is a list of the 5 most recent open conversations
    recent_conversations = list(
        mongo.db.conversations
        .find({'status': 'open'})
        .sort('last_message.timestamp', -1)
        .limit(5)
    )
    for conv in recent_conversations:
        conv['_id'] = str(conv['_id'])

    # Nested Loop: Iterates upcoming_appointments and enriches each with pet_name (loop + DB lookup)
    upcoming_appointments = list(
        mongo.db.appointments
        .find({'status': {'$in': ['scheduled', 'confirmed']}, 'date': {'$gte': now}})
        .sort('date', 1)
        .limit(5)
    )
    for apt in upcoming_appointments:
        apt['_id'] = str(apt['_id'])
        # Data Structure: Each appointment dict is augmented with pet_name field
        pet = mongo.db.pets.find_one({'_id': apt['pet_id']})
        apt['pet_name'] = pet['name'] if pet else 'Desconocida'
        apt['pet_id'] = str(apt['pet_id'])

    # Professional Output: Passes 15+ context variables to the template
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
