import requests
import os


EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY')
INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE')


def enviar_mensaje(telefono, mensaje):
    """Envía un mensaje de texto vía Evolution API."""
    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {'apikey': EVOLUTION_API_KEY}
    payload = {
        'number': telefono,
        'text': mensaje
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
