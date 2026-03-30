"""
Configuration Module
====================
Development Environment: Uses python-dotenv to load .env files.
Syntax & Variables: Class-based configuration with inheritance.
Concept Validation: Separating config per environment (dev/prod)
    follows the Twelve-Factor App methodology.
"""
import os
from dotenv import load_dotenv

# Dynamic Input: Loads environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class.
    Data Structure: Class attributes act as a key-value dictionary
        accessible via app.config['KEY'].
    """
    # Syntax: str variable with fallback default value
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # Syntax: Connection string (URI format) for MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/connecta')


class DevelopmentConfig(Config):
    """Development environment — enables debug mode."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment — disables debug mode."""
    DEBUG = False
