"""
WhatsApp Service — abstraction layer over Evolution API REST endpoints.
Paradigm Analysis: Static methods provide a service-oriented pattern (no instance state).
Concept Validation: Config read from DB (not env vars) allows runtime configuration.
"""
import requests
from app.models.settings import Settings


class WhatsAppService:
    """Service to interact with Evolution API for WhatsApp messaging."""

    @staticmethod
    def _get_config():
        return Settings.get_evolution_config()

    @staticmethod
    def _headers(api_key):
        return {'apikey': api_key, 'Content-Type': 'application/json'}

    @staticmethod
    def _validate_config(config=None):
        """
        Check that Evolution API is configured.

        Business Rule: All three config values must be present to proceed.
        """
        if config is None:
            config = WhatsAppService._get_config()
        if not config['api_url'] or not config['api_key'] or not config['instance_name']:
            return None
        return config

    @staticmethod
    def send_text(phone, text):
        """
        Send a text message via Evolution API.

        Dynamic Input: phone and text from user action.
        Professional Output: Returns JSON response from Evolution API.
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'error': 'Evolution API not configured'}

        url = f"{config['api_url']}/message/sendText/{config['instance_name']}"
        payload = {'number': phone, 'text': text}
        response = requests.post(
            url,
            json=payload,
            headers=WhatsAppService._headers(config['api_key']),
            timeout=10,
        )
        return response.json()

    @staticmethod
    def test_connection():
        """Test the Evolution API connection by fetching instances."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/instance/fetchInstances"
            response = requests.get(
                url,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=10,
            )
            return {'success': response.status_code == 200, 'data': response.json()}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_connection_state():
        """
        Get the WhatsApp connection state for the configured instance.

        Data Structure: Returns dict with 'state' key (open|close|connecting|not_found|unconfigured).
        Debugging: Handles HTTP 404 as 'not_found' state gracefully.
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'state': 'unconfigured'}

        try:
            url = f"{config['api_url']}/instance/connectionState/{config['instance_name']}"
            response = requests.get(
                url,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                state = data.get('instance', {}).get('state', 'close')
                return {'state': state}
            # Debugging: Handles HTTP 404 as 'not_found' state gracefully
            if response.status_code == 404:
                return {'state': 'not_found'}
            return {'state': 'error', 'error': f'HTTP {response.status_code}'}
        except requests.RequestException as e:
            return {'state': 'error', 'error': str(e)}

    @staticmethod
    def create_instance():
        """
        Create the WhatsApp instance and return the QR code.

        MVP Integration: Instance creation is the first step to connect WhatsApp.
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/instance/create"
            payload = {
                'instanceName': config['instance_name'],
                'integration': 'WHATSAPP-BAILEYS',
                'qrcode': True,
            }
            response = requests.post(
                url,
                json=payload,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=15,
            )
            data = response.json()

            if response.status_code in (200, 201):
                qr_base64 = data.get('qrcode', {}).get('base64', '')
                return {'success': True, 'qrcode': qr_base64, 'data': data}

            return {'success': False, 'error': data.get('message', 'Failed to create instance')}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_qr_code():
        """Get the QR code for connecting the instance."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/instance/connect/{config['instance_name']}"
            response = requests.get(
                url,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=15,
            )

            if response.status_code == 200:
                data = response.json()
                qr_base64 = data.get('base64', '') or data.get('qrcode', '')
                return {'success': True, 'qrcode': qr_base64}

            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def disconnect():
        """Disconnect/logout from WhatsApp."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/instance/logout/{config['instance_name']}"
            response = requests.post(
                url,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=10,
            )
            return {'success': response.status_code == 200}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def delete_instance():
        """Delete the WhatsApp instance entirely."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/instance/delete/{config['instance_name']}"
            response = requests.delete(
                url,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=10,
            )
            return {'success': response.status_code == 200}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def set_webhook(webhook_url):
        """
        Register a webhook URL on the Evolution API instance.

        Nested Structure: Payload has nested 'webhook' object (Evolution API v2 format).
        List: events array specifies which webhook events to subscribe to.
        Business Rule: Webhook must be configured for the system to receive messages.
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/webhook/set/{config['instance_name']}"
            # Nested Structure: Payload has nested 'webhook' object
            payload = {
                'webhook': {
                    'enabled': True,
                    'url': webhook_url,
                    'webhookByEvents': False,
                    'webhookBase64': False,
                    # List: events array specifies which webhook events to subscribe to
                    'events': [
                        'MESSAGES_UPSERT',
                        'MESSAGES_UPDATE',
                        'CONNECTION_UPDATE',
                    ],
                },
            }
            response = requests.post(
                url,
                json=payload,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=10,
            )
            if response.status_code in (200, 201):
                return {'success': True}

            return {
                'success': False,
                'error': f'HTTP {response.status_code}',
                'detail': response.text,
            }
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_webhook():
        """Get the current webhook configuration."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            # Try /webhook/find/{instance} first, then /webhook/instance/{instance}
            for path in [
                f"/webhook/find/{config['instance_name']}",
                f"/webhook/instance/{config['instance_name']}",
            ]:
                url = f"{config['api_url']}{path}"
                response = requests.get(
                    url,
                    headers=WhatsAppService._headers(config['api_key']),
                    timeout=10,
                )
                if response.status_code == 200:
                    return {'success': True, 'data': response.json()}
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}
