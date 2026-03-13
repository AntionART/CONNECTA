"""
Extensions Module
=================
Development Environment: Centralizes third-party extension instances.
Paradigm Analysis: Each extension follows the Singleton pattern —
    one instance shared across the entire application.
Concept Validation: Separating extensions avoids circular imports
    (a common Flask architectural pattern).
"""
from flask_pymongo import PyMongo
from flask_socketio import SocketIO
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Data Structure: Each variable holds a singleton object instance
mongo = PyMongo()        # MongoDB connection manager
socketio = SocketIO()    # WebSocket server for real-time communication
login_manager = LoginManager()  # Session-based authentication manager
bcrypt = Bcrypt()        # Password hashing utility (security layer)
