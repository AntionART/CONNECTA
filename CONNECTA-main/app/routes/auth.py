"""
Authentication routes — handles login/logout with session management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login via GET (render form) and POST (authenticate).

    Business Rule: Redirects authenticated users away from login page.
    Dynamic Input: Username and password from form POST.
    Concept Validation: Checks user exists AND password matches.
    Bilingualism: Flash message in English, UI renders in Spanish.
    """
    # Business Rule: Redirects authenticated users away from login page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        # Dynamic Input: Username and password from form POST
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Concept Validation: Checks user exists AND password matches
        user = User.find_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        # Bilingualism: Flash message in English, UI renders in Spanish
        flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
