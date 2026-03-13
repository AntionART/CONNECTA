"""
Settings routes — admin-only configuration panel.
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.utils.auth_decorators import role_required
from app.models.settings import Settings
from app.services.whatsapp import WhatsAppService

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
@role_required('admin')
def index():
    """
    Render the settings page.

    Business Rule: All settings routes require admin role.
    """
    config = Settings.get_evolution_config()
    return render_template('settings/index.html', config=config)


@settings_bp.route('/save', methods=['POST'])
@login_required
@role_required('admin')
def save():
    """
    Save Evolution API configuration.

    Dynamic Input: JSON body with api_url, api_key, instance_name.
    Business Rule: URL is stripped of trailing slashes for consistency.
    Business Rule: All settings routes require admin role.
    """
    data = request.get_json()
    # Business Rule: URL is stripped of trailing slashes for consistency
    Settings.set_evolution_config(
        api_url=data.get('api_url', '').strip().rstrip('/'),
        api_key=data.get('api_key', '').strip(),
        instance_name=data.get('instance_name', '').strip(),
    )
    return jsonify({'status': 'saved'})


@settings_bp.route('/test-connection', methods=['POST'])
@login_required
@role_required('admin')
def test_connection():
    """
    Test the Evolution API connection.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.test_connection()
    return jsonify(result)


@settings_bp.route('/connection-state', methods=['GET'])
@login_required
@role_required('admin')
def connection_state():
    """
    Get the current WhatsApp connection state.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.get_connection_state()
    return jsonify(result)


@settings_bp.route('/create-instance', methods=['POST'])
@login_required
@role_required('admin')
def create_instance():
    """
    Create a new WhatsApp instance.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.create_instance()
    return jsonify(result)


@settings_bp.route('/get-qr', methods=['GET'])
@login_required
@role_required('admin')
def get_qr():
    """
    Get the QR code for WhatsApp connection.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.get_qr_code()
    return jsonify(result)


@settings_bp.route('/disconnect', methods=['POST'])
@login_required
@role_required('admin')
def disconnect():
    """
    Disconnect the WhatsApp instance.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.disconnect()
    return jsonify(result)


@settings_bp.route('/delete-instance', methods=['POST'])
@login_required
@role_required('admin')
def delete_instance():
    """
    Delete the WhatsApp instance entirely.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.delete_instance()
    return jsonify(result)


@settings_bp.route('/set-webhook', methods=['POST'])
@login_required
@role_required('admin')
def set_webhook():
    """
    Register a webhook URL on the Evolution API instance.

    Business Rule: All settings routes require admin role.
    """
    data = request.get_json()
    webhook_url = data.get('webhook_url', '').strip().rstrip('/')
    if not webhook_url:
        return jsonify({'success': False, 'error': 'webhook_url is required'}), 400
    result = WhatsAppService.set_webhook(webhook_url)
    return jsonify(result)


@settings_bp.route('/get-webhook', methods=['GET'])
@login_required
@role_required('admin')
def get_webhook():
    """
    Get the current webhook configuration.

    Business Rule: All settings routes require admin role.
    """
    result = WhatsAppService.get_webhook()
    return jsonify(result)
