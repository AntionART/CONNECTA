"""
NLP Service — basic intent detection for WhatsApp messages.
Concept Validation: Rule-based NLP (keyword matching) as MVP approach.
Bilingualism: Keywords are in Spanish (matching user messages), responses in Spanish.
"""


# [GUÍA 2 - ACTIVIDAD 2] String manipulation — .lower() para normalizar entrada
# Uso en CONNECTA: El mensaje del usuario se convierte a minúsculas antes de comparar,
# garantizando que 'Cita', 'CITA' y 'cita' sean tratados igual.
# Ejemplo: 'QUIERO UNA CITA' → 'quiero una cita'
def detectar_intencion(mensaje):
    """
    Detecta la intencion del mensaje del usuario.
    Retorna: 'agendar_cita' | 'consulta' | 'historial' | 'desconocido'
    """
    # [GUÍA 2 - ACTIVIDAD 2] .lower() normaliza el texto del mensaje WhatsApp
    # Uso en CONNECTA: Evita falsos negativos por mayúsculas en mensajes de usuarios
    # Ejemplo: mensaje.lower() → 'quiero agendar una cita'
    mensaje = mensaje.lower()

    # [GUÍA 2 - ACTIVIDAD 3] Lista de palabras clave por intención
    # Uso en CONNECTA: Cada intención tiene su propia lista de palabras trigger;
    # any() evalúa la lista en cortocircuito (para al primer match)
    # Ejemplo: ['cita', 'agendar', 'turno', 'reservar'] — si el usuario escribe
    # 'quiero un turno', la función retorna 'agendar_cita'

    # [GUÍA 3 - ACTIVIDAD 1] if/elif/else — árbol de decisión de intenciones
    # Uso en CONNECTA: Clasifica el mensaje en 4 ramas posibles según palabras clave;
    # el orden importa (cita tiene prioridad sobre consulta)
    # Ejemplo: si mensaje contiene 'agendar' → rama 1; si contiene 'historial' → rama 2
    if any(palabra in mensaje for palabra in ['cita', 'agendar', 'turno', 'reservar']):
        return 'agendar_cita'
    elif any(palabra in mensaje for palabra in ['historial', 'registro', 'consultas anteriores']):
        return 'historial'
    elif any(palabra in mensaje for palabra in ['síntoma', 'enfermo', 'dolor', 'consulta']):
        return 'consulta'
    else:
        return 'desconocido'


# [GUÍA 5 - ACTIVIDAD 4] Diccionario clave:valor — mapa de intención → respuesta
# Uso en CONNECTA: El dict `respuestas` actúa como lookup table en lugar de if/elif;
# la clave es la intención detectada y el valor es el mensaje automático a enviar
# Ejemplo: respuestas['agendar_cita'] → 'Claro, te ayudo a agendar tu cita...'
def generar_respuesta(intencion):
    """
    Genera una respuesta automatica segun la intencion detectada.
    """
    # [GUÍA 5 - ACTIVIDAD 4] Dict como lookup table de intención → respuesta WhatsApp
    # Uso en CONNECTA: Centraliza todos los mensajes automáticos; agregar una nueva
    # intención solo requiere añadir una entrada al dict
    # Ejemplo: respuestas.get('historial') → 'Voy a consultar el historial...'
    respuestas = {
        'agendar_cita': 'Claro, te ayudo a agendar tu cita. ¿Qué fecha y hora prefieres?',
        'historial': 'Voy a consultar el historial clínico de tu mascota.',
        'consulta': 'Un veterinario te atenderá en breve. Por favor describe los síntomas.',
        'desconocido': 'Hola! Soy el asistente de CONNECTA. ¿En qué puedo ayudarte?'
    }

    # [GUÍA 3 - ACTIVIDAD 1] Rama else implícita vía .get() con valor default
    # Uso en CONNECTA: Si la intención no existe en el dict (caso borde),
    # retorna la respuesta genérica 'desconocido' sin lanzar KeyError
    # Ejemplo: respuestas.get('xyz', respuestas['desconocido']) → mensaje genérico
    return respuestas.get(intencion, respuestas['desconocido'])
