"""
Helper utilities for MongoDB document serialization.
"""
from bson import ObjectId
from datetime import datetime, timezone


# [GUÍA 6 - ACTIVIDAD 3] Ciclo anidado — iteración sobre dict + iteración sobre lista
# Uso en CONNECTA: El for externo recorre cada campo del documento MongoDB;
# cuando el valor es una lista, el comprehension interno itera sus elementos
# → doble nivel de iteración para serialización recursiva de documentos anidados
# Ejemplo: doc = {'labels': ['vip', 'urgente'], 'last_message': {'text': 'Hola'}}
#          → for key, value → value es lista → itera cada item de la lista
def serialize_doc(doc):
    """
    Convert a MongoDB document to a JSON-serializable dict.
    """
    if doc is None:
        return None
    result = {}

    # [GUÍA 5 - ACTIVIDAD 1] Ciclo for — iteración sobre pares clave:valor del dict
    # Uso en CONNECTA: Recorre cada campo del documento MongoDB para convertir
    # tipos no serializables (ObjectId, datetime) a sus equivalentes JSON (str, ISO str)
    # Ejemplo: for key, value in {'_id': ObjectId('...'), 'name': 'Luna'}.items()
    for key, value in doc.items():
        # [GUÍA 3 - ACTIVIDAD 1] if/elif — despacho por tipo de valor
        # Uso en CONNECTA: Cada elif maneja un tipo diferente; ObjectId→str,
        # datetime→ISO, dict→recursivo, list→comprehension, resto→tal cual
        # Ejemplo: ObjectId('64abc') → '64abc', datetime(2025,3,27) → '2025-03-27T...'
        if isinstance(value, ObjectId):
            # [GUÍA 4 - ACTIVIDAD 2] Casting — ObjectId de MongoDB → str serializable
            # Uso en CONNECTA: JavaScript/JSON no entiende ObjectId; str() lo convierte
            # a su representación hexadecimal para enviarlo al frontend
            # Ejemplo: ObjectId('64abc123def456') → '64abc123def456'
            result[key] = str(value)
        elif isinstance(value, datetime):
            # [GUÍA 4 - ACTIVIDAD 2] Casting — datetime → string ISO 8601
            # Uso en CONNECTA: El frontend JavaScript parsea fechas en formato ISO;
            # .isoformat() genera '2025-03-27T10:00:00+00:00' compatible con Date()
            # Ejemplo: datetime(2025,3,27,10,0,tzinfo=UTC) → '2025-03-27T10:00:00+00:00'
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            # [GUÍA 6 - ACTIVIDAD 3] Recursión — dict anidado procesado por el mismo ciclo
            # Uso en CONNECTA: last_message es un sub-documento dict dentro de conversation;
            # la recursión garantiza que su datetime interno también se serialice
            # Ejemplo: {'last_message': {'timestamp': datetime(...)}} → {'timestamp': '2025-...'}
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            # [GUÍA 5 - ACTIVIDAD 1] List comprehension — iteración sobre lista de valores
            # Uso en CONNECTA: El campo labels de conversation es una lista ['vip', 'urgente'];
            # el comprehension serializa cada elemento según su tipo
            # Ejemplo: [ObjectId('...'), 'urgente'] → ['64abc...', 'urgente']
            result[key] = [
                serialize_doc(item) if isinstance(item, dict)
                else str(item) if isinstance(item, ObjectId)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


# [GUÍA 2 - ACTIVIDAD 3] Lista — serialización de array de documentos
# Uso en CONNECTA: Los endpoints de listado (GET /api/pets, GET /api/conversations)
# retornan listas; serialize_docs aplica serialize_doc a cada elemento del array
# Ejemplo: serialize_docs([{'_id': ObjectId(...), 'name': 'Luna'}, ...]) → lista serializable
def serialize_docs(docs):
    """
    Convert a list of MongoDB documents.
    """
    # [GUÍA 5 - ACTIVIDAD 1] List comprehension — aplicación masiva de serialización
    # Uso en CONNECTA: Convierte toda la lista de documentos MongoDB en una lista
    # de dicts serializables a JSON con una sola línea
    # Ejemplo: [serialize_doc(doc) for doc in pets_cursor] → lista JSON-ready
    return [serialize_doc(doc) for doc in docs]
