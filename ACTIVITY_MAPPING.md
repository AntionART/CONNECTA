# CONNECTA - Rastreabilidad de Guías Prácticas

Este documento mapea cada actividad de las Guías Prácticas de Diseño Funcional
al código real del proyecto CONNECTA. Permite navegar directamente al archivo y
línea donde se implementa cada concepto.

> **Importante:** CONNECTA es una API REST con MongoDB — no usa consola ni `input()`.
> Los conceptos de Input/Output se implementan via HTTP requests; las colecciones
> viven en MongoDB, no en listas locales. PEP 8 aplicado en todo el proyecto.

---

## Tabla de Navegación por Guía

---

## **GUÍA 1: Investigación Técnica y Constitución del Proyecto** ✅
**Estado:** Completado en fase previa
**Sesión:** 13/02/2026

**Evidencia de Completitud:**
- `CONNECTA_Pets.pdf` - Documento oficial del proyecto (Investigación técnica + justificación)
- `README.md` - Descripción inicial del proyecto
- `https://github.com/AntionART/CONNECTA` - Repositorio Git activo

**Criterios Verificados:**
| Requisito | Cumplido |
|-----------|----------|
| Título oficial del proyecto | ✅ CONNECTA: Sistema Inteligente de Gestión Veterinaria |
| Definición del problema | ✅ Canales de comunicación fragmentados en clínicas veterinarias |
| Investigación paradigma funcional | ✅ Sección 6 de CONNECTA_Pets.pdf |
| Justificación Python + Evolution API | ✅ Sección 6 de CONNECTA_Pets.pdf |
| Repositorio con README | ✅ GitHub con descripción inicial |

**Notas:**
- Guía 1 establece el escenario general: CONNECTA es un sistema veterinario integrado con WhatsApp
- Las Guías 2-6 son desarrollo incremental de este proyecto base
- Rastreabilidad de Guías 2-6 disponible en secciones siguientes

---

### GUÍA 2 — Sintaxis & Colecciones

**Objetivo:** Declaración de variables, manipulación de strings, listas y operadores.

| Actividad | Archivo + Líneas aproximadas | Estado |
|---|---|---|
| Act 1: Variables (int, str, float, bool) | `app/models/pet.py` ~24-51 | ✅ |
| Act 1: Variables (int, str, float, bool) | `app/models/conversation.py` ~24-52 | ✅ |
| Act 1: Variables (int, str, float, bool) | `app/models/appointment.py` ~28-41 | ✅ |
| Act 1: Variables (int) contadores dashboard | `app/routes/dashboard.py` ~33-41 | ✅ |
| Act 2: String manipulation (.lower()) | `app/services/nlp.py` ~11-19 | ✅ |
| Act 2: String manipulation (.strip().lower().replace()) | `app/routes/api/conversations.py` ~91-96 | ✅ |
| Act 2: String manipulation (.replace() limpiar teléfono) | `app/routes/webhook.py` ~58-63 | ✅ |
| Act 3: Lista como campo de documento | `app/models/conversation.py` ~34-39 | ✅ |
| Act 3: Lista como resultado de consulta | `app/models/pet.py` ~62-66 | ✅ |
| Act 3: Lista como resultado de consulta | `app/models/appointment.py` ~52-57 | ✅ |
| Act 3: Lista serialización de array | `app/utils/helpers.py` ~67-80 | ✅ |
| Act 3: Lista de conversaciones recientes | `app/routes/dashboard.py` ~62-68 | ✅ |
| Act 4: Operadores aritméticos (week_start) | `app/routes/dashboard.py` ~20-24 | ✅ |
| Act 4: Operadores aritméticos ($inc contador) | `app/models/conversation.py` ~108-115 | ✅ |
| Act 4: Operadores aritméticos (rango de fechas) | `app/models/appointment.py` ~74-83 | ✅ |
| Act 4: Aritmética implícita en paginación | `app/routes/api/messages.py` ~32-37 | ✅ |
| Act 5: Operadores de comparación (== HTTP 200) | `app/services/whatsapp.py` ~67-72 | ✅ |
| Act 5: Operadores de comparación (in (200,201)) | `app/services/whatsapp.py` ~144-149 | ✅ |
| Act 5: Operadores de comparación ($gt unread) | `app/routes/dashboard.py` ~53-57 | ✅ |

**Cómo encontrarlo:**
```bash
grep -rn "\[GUÍA 2" app/
```

**Ejemplo real — Act 2 (.strip().lower().replace()):**
```python
# app/routes/api/conversations.py
name = data.get('name', '').strip().lower().replace(' ', '_')
# '  VIP Cliente  ' → 'vip_cliente'
```

**Ejemplo real — Act 4 (operador aritmético):**
```python
# app/routes/dashboard.py
week_start = today_start - timedelta(days=today_start.weekday())
# hoy=miércoles(2) → week_start = hoy - 2 días = lunes
```

---

### GUÍA 3 — Estructuras de Control Lógico

**Objetivo:** if/elif/else, operadores lógicos y validaciones de parámetros.

| Actividad | Archivo + Líneas aproximadas | Estado |
|---|---|---|
| Act 1: if/elif/else árbol de decisión NLP | `app/services/nlp.py` ~23-35 | ✅ |
| Act 1: if/elif/else enrutamiento de eventos | `app/routes/webhook.py` ~34-39 | ✅ |
| Act 1: if/elif/else estado de conexión WhatsApp | `app/services/whatsapp.py` ~93-107 | ✅ |
| Act 1: if/elif construcción de query MongoDB | `app/models/conversation.py` ~83-91 | ✅ |
| Act 1: if/elif construcción de PATCH parcial | `app/routes/api/conversations.py` ~53-63 | ✅ |
| Act 1: if/else find-or-create idempotente | `app/models/conversation.py` ~64-68 | ✅ |
| Act 1: if/else normalización de tipo updates | `app/routes/webhook.py` ~136-141 | ✅ |
| Act 1: if/elif despacho por tipo en serialización | `app/utils/helpers.py` ~29-55 | ✅ |
| Act 2: Operador lógico (not) excluir mensajes propios | `app/routes/webhook.py` ~50-54 | ✅ |
| Act 2: Operador lógico (and) actualizar contact_name | `app/routes/webhook.py` ~111-116 | ✅ |
| Act 2: Operador lógico (and) acceso seguro a dict | `app/routes/api/messages.py` ~65-70 | ✅ |
| Act 2: Operador lógico (and) en updates de estado | `app/routes/webhook.py` ~162-167 | ✅ |
| Act 2: Operador lógico (not...or) validar config | `app/services/whatsapp.py` ~32-36 | ✅ |
| Act 2: Operador lógico (not...or) validar label | `app/routes/api/conversations.py` ~100-104 | ✅ |
| Act 3: Validación — datos requeridos en webhook | `app/routes/webhook.py` ~26-30 | ✅ |
| Act 3: Validación — phone vacío | `app/routes/webhook.py` ~66-70 | ✅ |
| Act 3: Validación — campos requeridos de mascota | `app/routes/api/pets.py` ~46-58 | ✅ |
| Act 3: Validación — texto vacío antes de enviar | `app/routes/api/messages.py` ~57-61 | ✅ |
| Act 3: Validación — mascota existe antes de cita | `app/routes/api/appointments.py` ~83-87 | ✅ |
| Act 3: Validación — filtro status opcional | `app/models/appointment.py` ~63-67 | ✅ |

**Cómo encontrarlo:**
```bash
grep -rn "\[GUÍA 3" app/
```

**Ejemplo real — Act 1 (árbol de decisión NLP):**
```python
# app/services/nlp.py
if any(palabra in mensaje for palabra in ['cita', 'agendar', 'turno', 'reservar']):
    return 'agendar_cita'
elif any(palabra in mensaje for palabra in ['historial', 'registro']):
    return 'historial'
elif any(palabra in mensaje for palabra in ['síntoma', 'enfermo', 'dolor']):
    return 'consulta'
else:
    return 'desconocido'
```

**Ejemplo real — Act 2 (operadores lógicos):**
```python
# app/routes/webhook.py
if contact_name and not conv.get('contact_name'):
    Conversation.update(conv_id, {'contact_name': contact_name})
```

---

### GUÍA 4 — Input/Output

**Objetivo:** Captura de datos, casting de tipos, f-strings y print formateado.

| Actividad | Archivo + Líneas aproximadas | Estado |
|---|---|---|
| Act 1: Captura de datos (query params) | `app/routes/api/conversations.py` ~8-23 | ✅ |
| Act 1: Captura de datos (query params paginación) | `app/routes/api/messages.py` ~23-29 | ✅ |
| Act 1: Captura de datos (JSON body mensaje) | `app/routes/api/messages.py` ~49-53 | ✅ |
| Act 1: Captura de datos (JSON body label) | `app/routes/api/conversations.py` ~83-87 | ✅ |
| Act 1: Captura de datos (JSON webhook Evolution) | `app/routes/webhook.py` ~19-23 | ✅ |
| Act 1: Captura de datos (JSON body mascota) | `app/routes/api/pets.py` ~38-42 | ✅ |
| Act 1: Captura de datos (JSON body cita) | `app/routes/api/appointments.py` ~67-71 | ✅ |
| Act 2: Casting (type=int en args.get) | `app/routes/api/messages.py` ~23-28 | ✅ |
| Act 2: Casting (str ISO → datetime) | `app/routes/api/appointments.py` ~89-94 | ✅ |
| Act 2: Casting (str ISO → datetime en update) | `app/routes/api/appointments.py` ~115-120 | ✅ |
| Act 2: Casting (ObjectId → str) | `app/utils/helpers.py` ~36-40 | ✅ |
| Act 2: Casting (datetime → ISO string) | `app/utils/helpers.py` ~42-46 | ✅ |
| Act 3: F-string en URL de Evolution API | `app/services/whatsapp.py` ~50-55 | ✅ |
| Act 3: F-string en test de conexión | `app/services/whatsapp.py` ~85-89 | ✅ |
| Act 3: F-string en código de error HTTP | `app/services/whatsapp.py` ~103-107 | ✅ |
| Act 3: F-string en log de error webhook | `app/routes/webhook.py` ~123-128 | ✅ |
| Act 3: F-string en mensaje de campo faltante | `app/routes/api/pets.py` ~60-64 | ✅ |
| Act 4: print() formateado | — | ⏳ NO IMPLEMENTADO |

> **[GUÍA 4 - ACTIVIDAD 4] NO IMPLEMENTADO**
> **Razón:** CONNECTA es una API REST de producción. En lugar de `print()`, usamos
> `current_app.logger.error()` / `.info()` que es el estándar de Flask para logging
> estructurado. Los logs van a stdout en Docker y son capturados por el orquestador.
> **Ejemplo alternativo:** `current_app.logger.error(f'Webhook error: {e}')` en `webhook.py`

**Cómo encontrarlo:**
```bash
grep -rn "\[GUÍA 4" app/
```

**Ejemplo real — Act 3 (F-string URL dinámica):**
```python
# app/services/whatsapp.py
url = f"{config['api_url']}/message/sendText/{config['instance_name']}"
# → 'https://api.evolution.io/message/sendText/connecta-vet'
```

**Ejemplo real — Act 2 (casting type=int):**
```python
# app/routes/api/messages.py
page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 50, type=int)
# '2' (str de URL) → 2 (int para cálculos de paginación)
```

---

### GUÍA 5 — Loops & Diccionarios

**Objetivo:** for, while, break/continue, diccionarios y string methods en ciclos.

| Actividad | Archivo + Líneas aproximadas | Estado |
|---|---|---|
| Act 1: for — serialización de conversaciones | `app/routes/dashboard.py` ~71-75 | ✅ |
| Act 1: for — enriquecimiento de citas | `app/routes/dashboard.py` ~86-97 | ✅ |
| Act 1: for — iterar actualizaciones de estado | `app/routes/webhook.py` ~153-158 | ✅ |
| Act 1: for — iterar tipos de media | `app/routes/webhook.py` ~85-90 | ✅ |
| Act 1: for — validar campos requeridos | `app/routes/api/pets.py` ~53-58 | ✅ |
| Act 1: for — construcción de update selectivo | `app/routes/api/pets.py` ~86-91 | ✅ |
| Act 1: for — historial de citas por mascota | `app/routes/api/appointments.py` ~43-48 | ✅ |
| Act 1: for — construcción de update de cita | `app/routes/api/appointments.py` ~106-111 | ✅ |
| Act 1: for — sobre campos dict MongoDB | `app/utils/helpers.py` ~21-55 | ✅ |
| Act 1: for — paths alternativos webhook | `app/services/whatsapp.py` ~207-215 | ✅ |
| Act 2: while | — | ⏳ NO IMPLEMENTADO |
| Act 3: break — detener búsqueda de media type | `app/routes/webhook.py` ~101-106 | ✅ |
| Act 4: Dict lookup table NLP | `app/services/nlp.py` ~39-44 | ✅ |
| Act 4: Dict sub-documento last_message | `app/models/conversation.py` ~42-48 | ✅ |
| Act 4: Dict filtros de query params | `app/routes/api/conversations.py` ~17-22 | ✅ |
| Act 4: Dict status_map código → string | `app/routes/webhook.py` ~145-150 | ✅ |
| Act 4: Dict headers HTTP | `app/services/whatsapp.py` ~18-22 | ✅ |
| Act 4: Dict enriquecimiento con pet_name | `app/routes/dashboard.py` ~93-98 | ✅ |
| Act 5: Lista de dicts citas + mascota embebida | `app/routes/api/appointments.py` ~20-29 | ✅ |
| Act 5: Lista de dicts citas dashboard | `app/routes/dashboard.py` ~78-98 | ✅ |
| Act 6: String method en ciclo (.replace()) | `app/routes/webhook.py` ~93-98 | ✅ |

> **[GUÍA 5 - ACTIVIDAD 2] NO IMPLEMENTADO — while**
> **Razón:** Los ciclos del sistema son sobre colecciones finitas y conocidas
> (documentos de MongoDB, listas de campos). No hay condición de "mientras algo
> sea true" indefinidamente — Flask-SocketIO maneja el loop de eventos async.
> **Alternativa usada:** `for` sobre cursores MongoDB con `.limit()` acotado.

**Cómo encontrarlo:**
```bash
grep -rn "\[GUÍA 5" app/
```

**Ejemplo real — Act 4 (dict lookup table):**
```python
# app/services/nlp.py
respuestas = {
    'agendar_cita': 'Claro, te ayudo a agendar tu cita...',
    'historial': 'Voy a consultar el historial clínico...',
    'consulta': 'Un veterinario te atenderá en breve...',
    'desconocido': 'Hola! Soy el asistente de CONNECTA...'
}
return respuestas.get(intencion, respuestas['desconocido'])
```

**Ejemplo real — Act 6 (string method en ciclo):**
```python
# app/routes/webhook.py
for media_type in ['imageMessage', 'videoMessage', 'audioMessage', 'documentMessage']:
    if media_type in msg_content:
        content['type'] = media_type.replace('Message', '')  # 'imageMessage' → 'image'
        break
```

---

### GUÍA 6 — Arrays & Matrices

**Objetivo:** Vectores 1D, matrices 2D, ciclos anidados y acceso por índices dobles.

| Actividad | Archivo + Líneas aproximadas | Estado |
|---|---|---|
| Act 1: Vector — STATUSES ciclo de vida de cita | `app/models/appointment.py` ~21-25 | ✅ |
| Act 1: Vector — required fields de mascota | `app/routes/api/pets.py` ~46-50 | ✅ |
| Act 1: Vector — allowed fields update mascota | `app/routes/api/pets.py` ~79-83 | ✅ |
| Act 1: Vector — required fields de cita | `app/routes/api/appointments.py` ~74-79 | ✅ |
| Act 1: Vector — media types WhatsApp | `app/routes/webhook.py` ~79-83 | ✅ |
| Act 1: Vector — events webhook Evolution API | `app/services/whatsapp.py` ~167-175 | ✅ |
| Act 1: Vector — paths alternativos get_webhook | `app/services/whatsapp.py` ~199-210 | ✅ |
| Act 2: Matriz — índice compuesto lista de tuplas | `app/models/conversation.py` ~140-148 | ✅ |
| Act 3: Ciclo anidado — for citas + find mascota | `app/routes/dashboard.py` ~86-97 | ✅ |
| Act 3: Ciclo anidado — for citas API + find pet | `app/routes/api/appointments.py` ~27-35 | ✅ |
| Act 3: Ciclo anidado — for dict + for list | `app/utils/helpers.py` ~8-55 | ✅ |
| Act 4: Acceso [i][j] — índices dobles | — | ⏳ NO IMPLEMENTADO |

> **[GUÍA 6 - ACTIVIDAD 2] Matriz — índice compuesto:**
> MongoDB no usa matrices 2D de Python, pero el índice compuesto es estructuralmente
> equivalente: una lista de tuplas `[('campo', dirección)]` donde cada tupla es
> `[fila][columna]` conceptualmente.

> **[GUÍA 6 - ACTIVIDAD 4] NO IMPLEMENTADO — acceso [i][j]**
> **Razón:** CONNECTA no procesa matrices numéricas (imágenes, sensores, coordenadas).
> Los datos multidimensionales se modelan como dicts anidados en MongoDB, no como
> listas de listas. El equivalente funcional es `doc['last_message']['timestamp']`
> (acceso anidado a sub-documentos) en lugar de `matriz[i][j]`.

**Cómo encontrarlo:**
```bash
grep -rn "\[GUÍA 6" app/
```

**Ejemplo real — Act 1 (vector de estados):**
```python
# app/models/appointment.py
STATUSES = ['scheduled', 'confirmed', 'completed', 'cancelled']
# STATUSES[0] == 'scheduled', STATUSES[-1] == 'cancelled'
```

**Ejemplo real — Act 3 (ciclo anidado):**
```python
# app/routes/dashboard.py
for apt in upcoming_appointments:           # ciclo externo: cada cita
    apt['_id'] = str(apt['_id'])
    pet = mongo.db.pets.find_one(...)       # ciclo interno: query MongoDB
    apt['pet_name'] = pet['name'] if pet else 'Desconocida'
```

**Ejemplo real — Act 2 (matriz como índice compuesto):**
```python
# app/models/conversation.py
mongo.db[Conversation.COLLECTION].create_index([('last_message.timestamp', -1)])
# [('campo', orden)] → estructura [fila][columna] equivalente a matriz
```

---

### GUÍA 7 — Subalgoritmos y Refactorización Funcional

**Objetivo:** Modularización con `def` de responsabilidad única, `lambda` con `filter`/`map`, y refactoring de lógica dispersa en el proyecto real.

| Actividad | Archivo | Líneas aprox. | Descripción |
|-----------|---------|---------------|-------------|
| Act 1: `validar_campos_requeridos()` | `app/utils/helpers.py` | ~129-155 | Subalgorithm reutilizable: reemplaza el for+if de validación en 2 endpoints |
| Act 1: `_enriquecer_cita_dashboard()` | `app/routes/dashboard.py` | ~14-30 | Extrae lógica inline del for-loop: serializa _id y embebe pet_name |
| Act 3: Refactoring `create_pet` | `app/routes/api/pets.py` | ~55-58 | Reemplaza for+if por `validar_campos_requeridos()` |
| Act 3: Refactoring `create_appointment` | `app/routes/api/appointments.py` | ~67-70 | Reemplaza for+if por `validar_campos_requeridos()` |
| Act 2: `_coincide` lambda | `app/services/nlp.py` | ~8-10 | `lambda mensaje, palabras: any(p in mensaje for p in palabras)` |
| Act 2: Uso de `_coincide` × 3 | `app/services/nlp.py` | ~32-38 | Reemplaza 3 expresiones `any(p in mensaje for p in [...])` repetidas |
| Act 2: `map + lambda` serializar convs | `app/routes/dashboard.py` | ~97-100 | `map(lambda c: {**c, '_id': str(c['_id'])}, recent_conversations)` |
| Act 2: `map + función` enriquecer citas | `app/routes/dashboard.py` | ~109-112 | `map(_enriquecer_cita_dashboard, upcoming_appointments)` |
| Act 2: `filter + lambda` update pets | `app/routes/api/pets.py` | ~88-90 | `{c: data[c] for c in filter(lambda c: c in data, campos_permitidos)}` |
| Act 2: `filter + lambda` update appointments | `app/routes/api/appointments.py` | ~113-114 | Mismo patrón filter+lambda para campos de cita |

**Cómo encontrarlo:**
```bash
grep -rn "\[GUÍA 7" app/
```

**Ejemplo real — Act 1 (`validar_campos_requeridos` en helpers.py):**
```python
# app/utils/helpers.py
def validar_campos_requeridos(data: dict, campos: list):
    """Retorna el primer campo faltante o None si todo está OK."""
    # [GUÍA 7 - ACTIVIDAD 2] filter + lambda internamente
    return next(filter(lambda campo: not data.get(campo), campos), None)

# Uso en pets.py y appointments.py — reemplaza el for+if repetido:
campo_faltante = validar_campos_requeridos(data, ['name', 'species', 'owner_phone'])
if campo_faltante:
    return jsonify({'error': f'{campo_faltante} is required'}), 400
```

**Ejemplo real — Act 2 (`_coincide` lambda en nlp.py):**
```python
# app/services/nlp.py
# [GUÍA 7 - ACTIVIDAD 2] — reemplaza any(p in mensaje for p in lista) repetido 3 veces
_coincide = lambda mensaje, palabras: any(p in mensaje for p in palabras)

if _coincide(mensaje, ['cita', 'agendar', 'turno', 'reservar']):
    return 'agendar_cita'
```

**Ejemplo real — Act 2 (`map` en dashboard.py):**
```python
# app/routes/dashboard.py
# Antes: for conv in recent_conversations: conv['_id'] = str(conv['_id'])
recent_conversations = list(map(
    lambda c: {**c, '_id': str(c['_id'])}, recent_conversations
))

# Antes: for apt in upcoming_appointments: apt['_id'] = str(...) / apt['pet_name'] = ...
upcoming_appointments = list(map(_enriquecer_cita_dashboard, upcoming_appointments))
```

**Ejemplo real — Act 2 (`filter+lambda` dict comprehension en pets.py):**
```python
# app/routes/api/pets.py
# Antes: for field in allowed: if field in data: update[field] = data[field]
campos_permitidos = ['name', 'species', 'breed', 'age_years', 'weight_kg', 'owner_phone', 'owner_name']
update = {c: data[c] for c in filter(lambda c: c in data, campos_permitidos)}
```

---

## Patrones de Búsqueda

```bash
# Buscar todos los comentarios de una guía específica
grep -rn "\[GUÍA 2" app/
grep -rn "\[GUÍA 3" app/
grep -rn "\[GUÍA 4" app/
grep -rn "\[GUÍA 5" app/
grep -rn "\[GUÍA 6" app/
grep -rn "\[GUÍA 7" app/

# Buscar una actividad específica
grep -rn "\[GUÍA 3 - ACTIVIDAD 1\]" app/
grep -rn "\[GUÍA 5 - ACTIVIDAD 4\]" app/

# Buscar conceptos NO IMPLEMENTADOS
grep -rn "NO IMPLEMENTADO" app/

# Buscar todos los comentarios de guías de una vez
grep -rn "\[GUÍA" app/
```

---

## Checklist de Completitud

| Guía | Código | Documentación | Entrega |
|---|---|---|---|
| Guía 1 — Investigación Técnica | ✅ | ✅ | ✅ |
| Guía 2 — Sintaxis & Colecciones | ✅ | ✅ | ✅ |
| Guía 3 — Control Lógico | ✅ | ✅ | ✅ |
| Guía 4 — Input/Output | ✅ | ✅ | ✅ |
| Guía 5 — Loops & Diccionarios | ✅ | ✅ | ✅ |
| Guía 6 — Arrays & Matrices | ✅ | ✅ | ✅ |
| Guía 7 — Subalgoritmos & Lambdas | ✅ | ✅ | ✅ |

---

## Estructura de Directorios — Referencia por Guía

```
CONNECTA_Pets/
│
├── app/
│   ├── models/
│   │   ├── appointment.py     → GUÍA 2 (Act 1, 3, 4), GUÍA 3 (Act 1, 3), GUÍA 6 (Act 1)
│   │   ├── conversation.py    → GUÍA 2 (Act 1, 3, 4), GUÍA 3 (Act 1), GUÍA 5 (Act 4), GUÍA 6 (Act 2)
│   │   ├── pet.py             → GUÍA 2 (Act 1, 3)
│   │   ├── message.py         → (serialización via helpers)
│   │   ├── label.py           → (uso en conversations API)
│   │   ├── settings.py        → (uso en whatsapp service)
│   │   └── user.py            → (auth, bool is_active)
│   │
│   ├── routes/
│   │   ├── dashboard.py       → GUÍA 2 (Act 1, 3, 4, 5), GUÍA 5 (Act 1, 4, 5), GUÍA 6 (Act 3)
│   │   ├── webhook.py         → GUÍA 2 (Act 2), GUÍA 3 (Act 1, 2, 3), GUÍA 4 (Act 1, 3),
│   │   │                         GUÍA 5 (Act 1, 3, 4, 6), GUÍA 6 (Act 1)
│   │   └── api/
│   │       ├── conversations.py → GUÍA 3 (Act 1, 2), GUÍA 4 (Act 1), GUÍA 5 (Act 4)
│   │       │                       GUÍA 2 (Act 2)
│   │       ├── messages.py      → GUÍA 3 (Act 2, 3), GUÍA 4 (Act 1, 2), GUÍA 2 (Act 4)
│   │       ├── pets.py          → GUÍA 4 (Act 1, 3), GUÍA 5 (Act 1), GUÍA 6 (Act 1)
│   │       │                       GUÍA 3 (Act 3)
│   │       └── appointments.py  → GUÍA 4 (Act 1, 2), GUÍA 5 (Act 1, 5), GUÍA 6 (Act 1, 3)
│   │                               GUÍA 3 (Act 3)
│   │
│   ├── services/
│   │   ├── nlp.py             → GUÍA 2 (Act 2, 3), GUÍA 3 (Act 1), GUÍA 5 (Act 4)
│   │   └── whatsapp.py        → GUÍA 2 (Act 5), GUÍA 3 (Act 1, 2), GUÍA 4 (Act 3),
│   │                             GUÍA 5 (Act 1, 4), GUÍA 6 (Act 1)
│   │
│   └── utils/
│       └── helpers.py         → GUÍA 2 (Act 3), GUÍA 3 (Act 1), GUÍA 4 (Act 2),
│                                  GUÍA 5 (Act 1), GUÍA 6 (Act 3)
│
└── ACTIVITY_MAPPING.md        ← este archivo
```

---

## Notas Importantes

1. **API REST, no consola:** CONNECTA recibe datos vía HTTP (JSON bodies, query params),
   no via `input()`. El equivalente a "leer del usuario" es `request.get_json()` y
   `request.args.get()`.

2. **MongoDB, no listas locales:** Las colecciones de datos (mascotas, citas, conversaciones)
   viven en MongoDB. Las listas Python aparecen como resultados de queries (`list(cursor)`)
   o como estructuras auxiliares (campos requeridos, estados válidos, tipos de media).

3. **Paradigma funcional con clases de servicio:** Los modelos son clases con métodos
   estáticos — actúan como namespaces de funciones puras, no como OOP clásico con estado.

4. **PEP 8 obligatorio:** Nombres en snake_case, líneas ≤ 79 caracteres en comentarios,
   imports organizados (stdlib → third-party → local), docstrings en funciones públicas.

5. **Logging en lugar de print():** `current_app.logger.error(f'...')` es el estándar
   de producción en Flask. `print()` no aparece en el código de la app (solo podría
   usarse en scripts de utilidad fuera de la app).
