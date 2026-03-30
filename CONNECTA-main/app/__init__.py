"""
CONNECTA - Veterinary CRM with WhatsApp Integration
=====================================================
Software Scenario: SaaS-style CRM for veterinary clinics.
Paradigm Analysis: Uses Object-Oriented (Flask extensions as objects) and
Procedural (factory function pattern) paradigms combined.
Development Environment: Python 3.11, Flask 3.1, MongoDB 7, Docker containers.
Git Management: Main branch workflow, feature-based development.
MVP Integration: Minimal Viable Product delivering chat, pets, appointments, and dashboard.
Bilingualism: Code and comments in English; UI labels in Spanish for end users.
"""
from flask import Flask
from config import Config
from app.extensions import mongo, socketio, login_manager, bcrypt


def create_app(config_class=Config):
    """
    Application Factory Pattern (concept validation).
    - Receives a config class as dynamic input (configurable per environment).
    - Returns a fully configured Flask app as professional output.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    # Data Structure: Each extension is an object instance (OOP paradigm)
    mongo.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    bcrypt.init_app(app)

    # Register blueprints
    # List: Collection of blueprint modules to register (modular architecture)
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.chat import chat_bp
    from app.routes.webhook import webhook_bp
    from app.routes.pets import pets_bp
    from app.routes.appointments import appointments_bp
    from app.routes.settings_routes import settings_bp
    from app.routes.api import api_bp

    # Nested Structure: Each tuple is (blueprint_object, url_prefix_string)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.register_blueprint(pets_bp, url_prefix='/pets')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Initialize DB indexes and seed admin user
    with app.app_context():
        _init_db()

    return app


def _init_db():
    """
    Business Rule: Database must have indexes and a default admin user.
    Concept Validation: Ensures the system is usable immediately after deployment.
    """
    # List: Sequential function calls to initialize indexes for each collection
    from app.models.user import User, init_user_indexes
    from app.models.conversation import init_conversation_indexes
    from app.models.message import init_message_indexes
    from app.models.pet import init_pet_indexes
    from app.models.appointment import init_appointment_indexes
    from app.models.label import init_label_indexes
    from app.models.settings import init_settings_indexes

    init_user_indexes()
    init_conversation_indexes()
    init_message_indexes()
    init_pet_indexes()
    init_appointment_indexes()
    init_label_indexes()
    init_settings_indexes()

    # Business Rule: Seed admin user if not exists (first-run setup)
    # Dynamic Input: Hardcoded defaults for MVP; in production, use env vars
    if not User.find_by_username('admin'):
        User.create(
            username='admin',
            email='admin@connecta.local',
            password='admin',
            display_name='Administrador',  # Bilingualism: Spanish display name
            role='admin',
        )
