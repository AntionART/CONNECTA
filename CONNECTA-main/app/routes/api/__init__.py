from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.routes.api import conversations, messages, pets, appointments
