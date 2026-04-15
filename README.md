# CONNECTA - Veterinary Management System

SaaS platform integrated with **WhatsApp Business** for veterinary clinics. Enables customer service, appointment scheduling, clinical record management, and post-consultation follow-up through WhatsApp conversations.

**Academic project** — Functional Design, FESC
**Authors:** Erick Ocampo, Daniel Arteaga, Andrés Rodríguez
**Instructor:** Robinson Damian Gómez Sánchez

---

## Architecture

```
WhatsApp Client → Evolution API → Flask Backend → MongoDB → AI Module
```

**Paradigm:** Functional programming — pure functions, immutable returns, lambda expressions, and single-responsibility modules throughout the codebase.

**Stack:**
- Backend: Python 3.11 / Flask 3.1 (Application Factory + Blueprints)
- Database: MongoDB 7 (Docker for dev, Atlas for production)
- WhatsApp Integration: Evolution API
- Real-time: Flask-SocketIO + gevent
- Auth: Flask-Login + Flask-Bcrypt
- Containerization: Docker + Docker Compose

## Project Structure

```
CONNECTA/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── extensions.py        # MongoDB, SocketIO, Login, Bcrypt
│   ├── models/              # MongoDB schemas (User, Pet, Appointment, etc.)
│   ├── routes/              # Blueprints (auth, chat, dashboard, pets, appointments)
│   │   └── api/             # REST API endpoints
│   ├── services/
│   │   ├── whatsapp.py      # Message sending via Evolution API
│   │   └── nlp.py           # Intent detection & responses
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS & JS assets
│   └── utils/               # Helpers & decorators
├── actividades/             # Academic deliverables — functional design modules
│   ├── main.py              # Avance 2: variables, strings, collections, operators
│   ├── avance2/main.py      # Avance 2 (mirror)
│   ├── avance3/
│   │   └── decision_engine.py   # Avance 3: if/elif/else, business logic rules
│   └── avance7/
│       ├── functions.py     # Avance 7: subalgorithms (def) + lambda functions
│       └── main.py          # Avance 7: refactored orchestrator with run()
├── ACTIVITY_MAPPING.md      # Traceability: guides → source code line references
├── config.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Functional Design — Academic Modules

The `actividades/` folder contains standalone Python modules that demonstrate functional programming concepts applied to the CONNECTA domain. Each module runs independently (`python main.py`) and maps to a practical guide (Guía Práctica).

| Module | Guide | Concepts |
|--------|-------|----------|
| `actividades/main.py` | Guía 2 | Variables, strings, lists, arithmetic & logical operators |
| `actividades/avance3/decision_engine.py` | Guía 3 | `if/elif/else`, nested logic, business rules, edge-case validation |
| `actividades/avance7/functions.py` | Guía 7 — Act 1 & 2 | `def` subalgorithms, `lambda` + `filter` / `map` / `sorted` |
| `actividades/avance7/main.py` | Guía 7 — Act 3 | Refactored orchestrator: `run()` with 100% function calls |

### Functional Patterns Applied (Avance 7)

**Subalgorithms (`def`) — single-responsibility functions:**
```python
# actividades/avance7/functions.py
def procesar_servicios_con_iva(servicios: List[Dict], iva: float = 0.19) -> List[Dict]:
    """Enriches each service dict with precio_con_iva. Returns a new list (no mutation)."""
    return [{**s, "precio_con_iva": round(s["price"] * (1 + iva), 2)} for s in servicios]

def buscar_paciente_por_id(pacientes: List[Dict], patient_id: str) -> Optional[Dict]:
    """Explicit return: None if not found — never raises on missing data."""
    for p in pacientes:
        if p.get("id") == patient_id:
            return p
    return None
```

**Lambda functions — `filter` / `map` / `sorted`:**
```python
# actividades/avance7/functions.py
filtrar_saludables         = lambda ps: list(filter(lambda p: p["health_status"] == "Saludable", ps))
calcular_precios_con_iva   = lambda precios: list(map(lambda p: round(p * 1.19, 2), precios))
ordenar_por_precio_desc    = lambda ss: sorted(ss, key=lambda s: s["price"], reverse=True)
```

**Refactored orchestrator — `run()` with no inline logic:**
```python
# actividades/avance7/main.py
def run() -> None:
    config = crear_configuracion_clinica()   # config via function, no globals
    sep    = "=" * 70
    imprimir_cabecera(config, sep)
    imprimir_seccion_modularizacion(PACIENTES, SERVICIOS, CITAS, sep)
    imprimir_seccion_lambdas(PACIENTES, SERVICIOS, CITAS, sep)
    imprimir_seccion_colecciones(PACIENTES, SERVICIOS, CITAS, VETERINARIOS, CONSULTAS_FRECUENTES, sep)
```

**Run any academic module:**
```bash
python actividades/main.py                  # Avance 2
python actividades/avance3/decision_engine.py   # Avance 3
python actividades/avance7/main.py          # Avance 7
```

Full traceability of every guide → source line: see [`ACTIVITY_MAPPING.md`](ACTIVITY_MAPPING.md).

## Setup

### With Docker (recommended)

```bash
cp .env.example .env
docker-compose up --build
```

### Without Docker

```bash
pip install -r requirements.txt
cp .env.example .env
python run.py
```

App runs at `http://localhost:5000`. Default admin: `admin` / `admin`.

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Flask secret key |
| `MONGO_URI` | MongoDB connection URI |
| `EVOLUTION_API_URL` | Evolution API instance URL |
| `EVOLUTION_API_KEY` | Evolution API key |
| `EVOLUTION_INSTANCE` | WhatsApp instance name |

## Features

- **Real-time chat** — WhatsApp integration via webhook + Socket.IO live messaging
- **Pet management** — CRUD for patient records
- **Appointments** — Scheduling and tracking
- **Dashboard** — Clinic activity overview
- **Auth** — Login with role-based access
- **Settings** — Configurable clinic parameters
