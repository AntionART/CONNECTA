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
        # [GUÍA 5 - ACTIVIDAD 4] Diccionario — headers HTTP como clave:valor
        return {'apikey': api_key, 'Content-Type': 'application/json'}

    @staticmethod
    def _validate_config(config=None):
        """Check that Evolution API is configured."""
        if config is None:
            config = WhatsAppService._get_config()
        # [GUÍA 3 - ACTIVIDAD 2] Operadores lógicos — not...or para validación múltiple
        if not config['api_url'] or not config['api_key'] or not config['instance_name']:
            return None
        return config

    @staticmethod
    def _api_call(method, path, payload=None, timeout=10):
        """
        Ejecuta una llamada HTTP a Evolution API.

        Centraliza: validate_config → construir URL → headers → try/except.
        Retorna (response, None) si la llamada fue exitosa,
        o (None, error_dict) si la configuración falta o hay excepción de red.

        Uso: response, err = WhatsAppService._api_call('POST', '/message/sendText/inst', payload)
        """
        config = WhatsAppService._validate_config()
        if not config:
            return None, {'error': 'Evolution API not configured'}

        # [GUÍA 4 - ACTIVIDAD 3] F-string — construcción dinámica de URL de endpoint
        url = f"{config['api_url']}{path}"
        headers = WhatsAppService._headers(config['api_key'])

        try:
            response = requests.request(
                method,
                url,
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            return response, None
        except requests.RequestException as e:
            return None, {'error': str(e)}

    # ------------------------------------------------------------------ #
    # Public API methods                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def send_text(phone, text):
        """Send a text message via Evolution API."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'error': 'Evolution API not configured'}

        path = f"/message/sendText/{config['instance_name']}"
        response, err = WhatsAppService._api_call('POST', path, {'number': phone, 'text': text})
        if err:
            return err
        return response.json()

    @staticmethod
    def test_connection():
        """Test the Evolution API connection by fetching instances."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        response, err = WhatsAppService._api_call('GET', '/instance/fetchInstances')
        if err:
            return {'success': False, **err}
        # [GUÍA 2 - ACTIVIDAD 5] Operador de comparación — == para verificar HTTP 200
        return {'success': response.status_code == 200, 'data': response.json()}

    @staticmethod
    def get_connection_state():
        """Get the WhatsApp connection state for the configured instance."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'state': 'unconfigured'}

        path = f"/instance/connectionState/{config['instance_name']}"
        response, err = WhatsAppService._api_call('GET', path)
        if err:
            return {'state': 'error', **err}

        # [GUÍA 3 - ACTIVIDAD 1] if/elif/else — manejo de estados de conexión
        if response.status_code == 200:
            state = response.json().get('instance', {}).get('state', 'close')
            return {'state': state}
        if response.status_code == 404:
            return {'state': 'not_found'}
        # [GUÍA 4 - ACTIVIDAD 3] F-string — código HTTP en mensaje de error
        return {'state': 'error', 'error': f'HTTP {response.status_code}'}

    @staticmethod
    def create_instance():
        """Create the WhatsApp instance and return the QR code."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado — payload de creación de instancia
        payload = {
            'instanceName': config['instance_name'],
            'integration': 'WHATSAPP-BAILEYS',
            'qrcode': True,
        }
        response, err = WhatsAppService._api_call('POST', '/instance/create', payload, timeout=15)
        if err:
            return {'success': False, **err}

        data = response.json()
        # [GUÍA 2 - ACTIVIDAD 5] Operador de comparación — in para verificar 200 o 201
        if response.status_code in (200, 201):
            return {'success': True, 'qrcode': data.get('qrcode', {}).get('base64', ''), 'data': data}
        return {'success': False, 'error': data.get('message', 'Failed to create instance')}

    @staticmethod
    def get_qr_code():
        """Get the QR code for connecting the instance."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        path = f"/instance/connect/{config['instance_name']}"
        response, err = WhatsAppService._api_call('GET', path, timeout=15)
        if err:
            return {'success': False, **err}

        if response.status_code == 200:
            data = response.json()
            return {'success': True, 'qrcode': data.get('base64', '') or data.get('qrcode', '')}
        return {'success': False, 'error': f'HTTP {response.status_code}'}

    @staticmethod
    def disconnect():
        """Disconnect/logout from WhatsApp."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        path = f"/instance/logout/{config['instance_name']}"
        response, err = WhatsAppService._api_call('POST', path)
        if err:
            return {'success': False, **err}
        return {'success': response.status_code == 200}

    @staticmethod
    def delete_instance():
        """Delete the WhatsApp instance entirely."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        path = f"/instance/delete/{config['instance_name']}"
        response, err = WhatsAppService._api_call('DELETE', path)
        if err:
            return {'success': False, **err}
        return {'success': response.status_code == 200}

    @staticmethod
    def set_webhook(webhook_url):
        """Register a webhook URL on the Evolution API instance."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        path = f"/webhook/set/{config['instance_name']}"
        # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado — payload con sub-objeto webhook
        # [GUÍA 6 - ACTIVIDAD 1] Vector — lista 1D de eventos a suscribir
        payload = {
            'webhook': {
                'enabled': True,
                'url': webhook_url,
                'webhookByEvents': False,
                'webhookBase64': False,
                'events': ['MESSAGES_UPSERT', 'MESSAGES_UPDATE', 'CONNECTION_UPDATE'],
            },
        }
        response, err = WhatsAppService._api_call('POST', path, payload)
        if err:
            return {'success': False, **err}

        if response.status_code in (200, 201):
            return {'success': True}
        return {'success': False, 'error': f'HTTP {response.status_code}', 'detail': response.text}

    @staticmethod
    def get_webhook():
        """Get the current webhook configuration."""
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — intenta paths alternativos hasta obtener 200
        # [GUÍA 6 - ACTIVIDAD 1] Vector — lista de paths alternativos a intentar
        for path in [
            f"/webhook/find/{config['instance_name']}",
            f"/webhook/instance/{config['instance_name']}",
        ]:
            response, err = WhatsAppService._api_call('GET', path)
            if err:
                return {'success': False, **err}
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}

        return {'success': False, 'error': f'HTTP {response.status_code}'}
