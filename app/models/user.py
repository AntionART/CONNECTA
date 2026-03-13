"""
User Model — OOP Paradigm (class with static methods).

Defines the User entity for authentication and authorization.
Follows OOP principles: the User class encapsulates data access via
static factory/finder methods and instance methods for password validation.

Business Rules for Auth:
- Passwords are hashed with bcrypt before storage (never stored in plaintext).
- Flask-Login integration provides session-based authentication.
- Roles ('agent' by default) enable future role-based access control.

Debugging Patterns: find_by_* methods return None when no match is found,
allowing callers to handle missing users gracefully.

Bilingualism: Code and comments in English; display_name may contain
any locale string for the UI.
"""

from app.extensions import mongo, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone
from bson import ObjectId


# Data Structure: Class wrapping a MongoDB document (dict) into an object.
# Inherits from UserMixin to satisfy Flask-Login's required interface
# (is_authenticated, is_active, is_anonymous, get_id).
class User(UserMixin):

    # Nested Structure: Accesses nested dict keys with .get() for safe access.
    # Each attribute maps to a field in the MongoDB 'users' document.
    # .get() returns None instead of raising KeyError if the key is missing,
    # making the constructor resilient to incomplete documents.
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.display_name = user_data.get('display_name')
        # Syntax & Variables: role defaults to 'agent' (enum-like string).
        self.role = user_data.get('role', 'agent')
        self.is_active_user = user_data.get('is_active', True)

    @property
    def is_active(self):
        return self.is_active_user

    @staticmethod
    def find_by_id(user_id):
        data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(data) if data else None

    @staticmethod
    def find_by_username(username):
        data = mongo.db.users.find_one({'username': username})
        return User(data) if data else None

    # Dynamic Input: Receives user data parameters (username, email, password,
    # display_name, role) from the registration endpoint or admin panel.
    @staticmethod
    def create(username, email, password, display_name, role='agent'):
        # Business Rule: Password is hashed before storage (security).
        # bcrypt generates a salted hash, so identical passwords produce
        # different hashes — preventing rainbow-table attacks.
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

        # List: user_data dict acts as a key-value collection that mirrors
        # the MongoDB document schema for the 'users' collection.
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'display_name': display_name,
            'role': role,
            'is_active': True,
            'created_at': datetime.now(timezone.utc),
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

    # Concept Validation: Compares hashed password, never stores plaintext.
    # bcrypt.check_password_hash safely compares the stored hash with the
    # provided password — timing-safe to prevent side-channel attacks.
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Professional Output: Returns a sanitized dict (excludes password_hash).
    # This is safe to serialize to JSON for API responses or template rendering
    # without leaking sensitive credential data.
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role,
            'is_active': self.is_active_user,
        }


# Business Rule: Flask-Login callback, loads user from session ID.
# This function is invoked automatically on every authenticated request
# to reconstruct the User object from the session-stored user_id.
@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)


# Data Structure: MongoDB indexes — unique constraints enforce business rules.
# 'username' and 'email' must be unique across all users, preventing
# duplicate accounts. MongoDB raises DuplicateKeyError on violation.
def init_user_indexes():
    mongo.db.users.create_index('username', unique=True)
    mongo.db.users.create_index('email', unique=True)
