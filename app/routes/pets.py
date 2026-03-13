from flask import Blueprint, render_template
from flask_login import login_required

pets_bp = Blueprint('pets', __name__)


@pets_bp.route('/')
@login_required
def index():
    return render_template('pets/index.html')
