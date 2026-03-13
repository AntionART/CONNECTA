import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/connecta')
    EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
    EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
    EVOLUTION_INSTANCE = os.getenv('EVOLUTION_INSTANCE')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
