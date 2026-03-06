def detectar_intencion(mensaje):
    """
    Detecta la intención del mensaje del usuario.
    Retorna: 'agendar_cita' | 'consulta' | 'historial' | 'desconocido'
    """
    mensaje = mensaje.lower()

    if any(palabra in mensaje for palabra in ['cita', 'agendar', 'turno', 'reservar']):
        return 'agendar_cita'
    elif any(palabra in mensaje for palabra in ['historial', 'registro', 'consultas anteriores']):
        return 'historial'
    elif any(palabra in mensaje for palabra in ['síntoma', 'enfermo', 'dolor', 'consulta']):
        return 'consulta'
    else:
        return 'desconocido'


def generar_respuesta(intencion):
    """Genera una respuesta automática según la intención detectada."""
    respuestas = {
        'agendar_cita': 'Claro, te ayudo a agendar tu cita. ¿Qué fecha y hora prefieres?',
        'historial': 'Voy a consultar el historial clínico de tu mascota.',
        'consulta': 'Un veterinario te atenderá en breve. Por favor describe los síntomas.',
        'desconocido': 'Hola! Soy el asistente de CONNECTA. ¿En qué puedo ayudarte?'
    }
    return respuestas.get(intencion, respuestas['desconocido'])
