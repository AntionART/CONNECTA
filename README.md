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
├── actividades/             # Academic deliverables
├── config.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

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
