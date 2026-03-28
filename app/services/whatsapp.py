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
        # Uso en CONNECTA: Evolution API requiere 'apikey' en cada request;
        # el dict de headers se construye una vez y se reutiliza en todos los métodos
        # Ejemplo: {'apikey': 'abc123', 'Content-Type': 'application/json'}
        return {'apikey': api_key, 'Content-Type': 'application/json'}

    @staticmethod
    def _validate_config(config=None):
        """
        Check that Evolution API is configured.
        """
        if config is None:
            config = WhatsAppService._get_config()
        # [GUÍA 3 - ACTIVIDAD 2] Operadores lógicos — not...or para validación múltiple
        # Uso en CONNECTA: Los 3 valores de configuración son necesarios para enviar
        # mensajes; si cualquiera falta, la validación falla y retorna None
        # Ejemplo: if not api_url or not api_key or not instance_name → return None
        if not config['api_url'] or not config['api_key'] or not config['instance_name']:
            return None
        return config

    @staticmethod
    def send_text(phone, text):
        """
        Send a text message via Evolution API.
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'error': 'Evolution API not configured'}

        # [GUÍA 4 - ACTIVIDAD 3] F-string — construcción dinámica de URL de endpoint
        # Uso en CONNECTA: La URL de Evolution API se construye combinando api_url,
        # el path del endpoint y el nombre de la instancia configurada en settings
        # Ejemplo: f"{config['api_url']}/message/sendText/{config['instance_name']}"
        #          → 'https://api.evolution.io/message/sendText/connecta-vet'
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
            # [GUÍA 4 - ACTIVIDAD 3] F-string — URL dinámica para test de conexión
            # Uso en CONNECTA: Verifica que la API Key es válida haciendo GET
            # a /instance/fetchInstances; si responde 200, la conexión es correcta
            # Ejemplo: f"{config['api_url']}/instance/fetchInstances"
            url = f"{config['api_url']}/instance/fetchInstances"
            response = requests.get(
                url,
                headers=WhatsAppService._headers(config['api_key']),
                timeout=10,
            )
            # [GUÍA 2 - ACTIVIDAD 5] Operador de comparación — == para verificar HTTP 200
            # Uso en CONNECTA: response.status_code == 200 determina si la conexión
            # con Evolution API fue exitosa y se incluye en la respuesta
            # Ejemplo: {'success': True} si status_code==200, {'success': False} si no
            return {'success': response.status_code == 200, 'data': response.json()}
        except requests.RequestException as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_connection_state():
        """
        Get the WhatsApp connection state for the configured instance.
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
            # [GUÍA 3 - ACTIVIDAD 1] if/elif/else — manejo de estados de conexión
            # Uso en CONNECTA: El estado de WhatsApp puede ser open (conectado),
            # close (desconectado) o not_found (instancia no existe); cada rama
            # retorna el dict apropiado para el frontend del panel de settings
            # Ejemplo: 200 → {'state': 'open'}, 404 → {'state': 'not_found'}
            if response.status_code == 200:
                data = response.json()
                state = data.get('instance', {}).get('state', 'close')
                return {'state': state}
            if response.status_code == 404:
                return {'state': 'not_found'}
            # [GUÍA 4 - ACTIVIDAD 3] F-string — mensaje de error con código HTTP
            # Uso en CONNECTA: Si Evolution API responde con un código inesperado,
            # el error incluye el código para facilitar el diagnóstico
            # Ejemplo: f'HTTP {response.status_code}' → 'HTTP 503'
            return {'state': 'error', 'error': f'HTTP {response.status_code}'}
        except requests.RequestException as e:
            return {'state': 'error', 'error': str(e)}

    @staticmethod
    def create_instance():
        """
        Create the WhatsApp instance and return the QR code.
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/instance/create"
            # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado — payload de creación de instancia
            # Uso en CONNECTA: El payload combina el nombre de instancia con configuración
            # de integración; la clave 'qrcode': True indica que la API debe retornar el QR
            # Ejemplo: {'instanceName': 'connecta-vet', 'integration': 'WHATSAPP-BAILEYS', 'qrcode': True}
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

            # [GUÍA 2 - ACTIVIDAD 5] Operador de comparación — in para verificar códigos exitosos
            # Uso en CONNECTA: Evolution API puede responder 200 o 201 al crear una instancia;
            # 'in' verifica ambos sin necesidad de or
            # Ejemplo: if response.status_code in (200, 201) → instancia creada exitosamente
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
        """
        config = WhatsAppService._validate_config()
        if not config:
            return {'success': False, 'error': 'Evolution API not configured'}

        try:
            url = f"{config['api_url']}/webhook/set/{config['instance_name']}"
            payload = {
                # [GUÍA 5 - ACTIVIDAD 4] Diccionario anidado — payload con sub-objeto webhook
                # Uso en CONNECTA: La spec de Evolution API v2 requiere que la configuración
                # del webhook vaya dentro de una clave 'webhook' anidada en el payload
                # Ejemplo: {'webhook': {'enabled': True, 'url': 'https://...', 'events': [...]}}
                'webhook': {
                    'enabled': True,
                    'url': webhook_url,
                    'webhookByEvents': False,
                    'webhookBase64': False,
                    # [GUÍA 6 - ACTIVIDAD 1] Vector — lista 1D de eventos a suscribir
                    # Uso en CONNECTA: Solo nos interesan mensajes nuevos y actualizaciones
                    # de estado; suscribirse a todos los eventos generaría tráfico innecesario
                    # Ejemplo: ['MESSAGES_UPSERT', 'MESSAGES_UPDATE', 'CONNECTION_UPDATE']
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
            # [GUÍA 6 - ACTIVIDAD 1] Vector — lista de paths alternativos a intentar
            # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — intenta cada path hasta obtener 200
            # Uso en CONNECTA: Diferentes versiones de Evolution API usan paths distintos
            # para obtener la config del webhook; el for prueba ambos en orden
            # Ejemplo: for path in ['/webhook/find/...', '/webhook/instance/...']
            #          → si el primero da 200, retorna; si no, intenta el segundo
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
