"""
NLP Service — basic intent detection for WhatsApp messages.
Concept Validation: Rule-based NLP (keyword matching) as MVP approach.
Bilingualism: Keywords are in Spanish (matching user messages), responses in Spanish.
"""


def detectar_intencion(mensaje):
    """
    Detecta la intencion del mensaje del usuario.
    Retorna: 'agendar_cita' | 'consulta' | 'historial' | 'desconocido'

    List: Each keyword list checked with any() — short-circuit evaluation.
    Nested Logic: Multiple elif branches form a decision tree.
    Dynamic Input: User message text from WhatsApp.
    """
    mensaje = mensaje.lower()

    # List: Keyword list checked with any() — short-circuit evaluation
    if any(palabra in mensaje for palabra in ['cita', 'agendar', 'turno', 'reservar']):
        return 'agendar_cita'
    # Nested Logic: Multiple elif branches form a decision tree
    elif any(palabra in mensaje for palabra in ['historial', 'registro', 'consultas anteriores']):
        return 'historial'
    elif any(palabra in mensaje for palabra in ['síntoma', 'enfermo', 'dolor', 'consulta']):
        return 'consulta'
    else:
        return 'desconocido'


def generar_respuesta(intencion):
    """
    Genera una respuesta automatica segun la intencion detectada.

    Data Structure: respuestas dict maps intent strings to response strings.
    Professional Output: Returns appropriate response based on detected intent.
    """
    # Data Structure: respuestas dict maps intent strings to response strings
    respuestas = {
        'agendar_cita': 'Claro, te ayudo a agendar tu cita. ¿Qué fecha y hora prefieres?',
        'historial': 'Voy a consultar el historial clínico de tu mascota.',
        'consulta': 'Un veterinario te atenderá en breve. Por favor describe los síntomas.',
        'desconocido': 'Hola! Soy el asistente de CONNECTA. ¿En qué puedo ayudarte?'
    }
    return respuestas.get(intencion, respuestas['desconocido'])
