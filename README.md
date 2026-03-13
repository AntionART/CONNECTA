# CONNECTA - Sistema Inteligente de Gestión Veterinaria

Plataforma SaaS integrada en **WhatsApp Business** para clínicas veterinarias colombianas. Permite atención al cliente, agendamiento de citas, gestión de historiales clínicos y seguimiento post-consulta mediante conversaciones naturales en WhatsApp.

**Proyecto académico** — Diseño Funcional, FESC
**Autores:** Erick Ocampo, Daniel Arteaga, Andrés Rodríguez
**Docente:** Robinson Damian Gómez Sánchez

---

## Arquitectura

```
Cliente WhatsApp → Evolution API → Backend Flask → MongoDB → Módulo IA
```

**Stack:**
- Backend: Python / Flask (Application Factory + Blueprints)
- Base de datos: MongoDB (Docker en desarrollo, Atlas en producción)
- Integración WhatsApp: Evolution API
- Contenerización: Docker + Docker Compose

## Estructura del proyecto

```
CONNECTA_Pets/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── extensions.py        # Instancia MongoDB
│   ├── routes/
│   │   ├── webhook.py       # Recibe mensajes de Evolution API
│   │   ├── citas.py         # Agendamiento de citas
│   │   └── historial.py     # Historiales clínicos
│   ├── models/
│   │   ├── mascota.py
│   │   └── cita.py
│   └── services/
│       ├── whatsapp.py      # Envío de mensajes vía Evolution API
│       └── nlp.py           # Detección de intención y respuestas
├── actividades/
│   └── main.py              # Entregables académicos
├── Docs/
│   └── CONNECTA Pets.pdf    # Documento del proyecto
├── config.py
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Instalación y ejecución

### Con Docker (recomendado)

```bash
cp .env.example .env
docker-compose up --build
```

### Sin Docker

```bash
pip install -r requirements.txt
cp .env.example .env
python run.py
```

La app queda disponible en `http://localhost:5000`.

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Flask |
| `MONGO_URI` | URI de conexión a MongoDB |
| `EVOLUTION_API_URL` | URL de tu instancia Evolution API |
| `EVOLUTION_API_KEY` | API Key de Evolution API |
| `EVOLUTION_INSTANCE` | Nombre de la instancia WhatsApp |

## Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/webhook/` | Recibe mensajes entrantes de WhatsApp |
| GET | `/citas/` | Lista citas agendadas |
| POST | `/citas/` | Agenda una nueva cita |
| GET | `/historial/<mascota_id>` | Obtiene historial clínico |
| POST | `/historial/<mascota_id>` | Agrega registro clínico |
