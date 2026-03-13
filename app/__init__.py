from flask import Flask
from config import Config
from app.extensions import mongo


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    mongo.init_app(app)

    # Registrar Blueprints
    from app.routes.webhook import webhook_bp
    from app.routes.citas import citas_bp
    from app.routes.historial import historial_bp

    app.register_blueprint(webhook_bp, url_prefix='/webhook')
    app.register_blueprint(citas_bp, url_prefix='/citas')
    app.register_blueprint(historial_bp, url_prefix='/historial')

    return app
