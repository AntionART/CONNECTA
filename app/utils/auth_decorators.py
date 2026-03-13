"""
Authentication decorators for role-based access control.
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to restrict access by user role.

    Nested Structure: Decorator factory pattern (function returning decorator returning wrapper).
    List: *roles parameter accepts variable number of role strings.
    Business Rule: Checks current_user.role against allowed roles.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            # Business Rule: Checks current_user.role against allowed roles
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
