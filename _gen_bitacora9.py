#!/usr/bin/env python3
"""
Genera la Bitácora Técnica — Avance 9 (POO Nivel I) con diagramas Mermaid.
"""
import subprocess
import shutil
from pathlib import Path
from fpdf import FPDF

BASE_DIR  = Path(__file__).parent
DOCS_DIR  = BASE_DIR / "Docs"
TMP_DIR   = BASE_DIR / "_tmp_bita9"
TMP_DIR.mkdir(exist_ok=True)

OUTPUT_PDF = DOCS_DIR / "Bitacora Tecnica - POO Nivel I (Guia 9).pdf"

ARIAL      = "C:/Windows/Fonts/Arial.ttf"
ARIAL_B    = "C:/Windows/Fonts/Arialbd.ttf"
ARIAL_I    = "C:/Windows/Fonts/Ariali.ttf"
ARIAL_BI   = "C:/Windows/Fonts/Arialbi.ttf"
COUR       = "C:/Windows/Fonts/cour.ttf"
COUR_B     = "C:/Windows/Fonts/courbd.ttf"

# ─────────────────────────────────────────────
# FUENTES MERMAID
# ─────────────────────────────────────────────
DIAGRAMS = {}

DIAGRAMS["d1_clases"] = """\
classDiagram
    class BaseModel {
        +from_db(document) classmethod
        +find_by_id(doc_id) classmethod
        +update(doc_id, data) classmethod
        +delete(doc_id) classmethod
    }
    class Pet {
        +id str
        +name str
        +species str
        +age_years float
        +weight_kg float
        -_owner_phone str
        -_owner_name str
        +owner_phone property
        +owner_name property
        +pertenece_a(phone) bool
        +from_db(doc) Pet
        +to_dict() dict
        +__str__() str
        +create() Pet
        +list_all() List
    }
    class Appointment {
        +id str
        +pet_id str
        +date datetime
        +reason str
        +veterinarian str
        -_status str
        +STATUSES list
        +status property
        +from_db(doc) Appointment
        +to_dict() dict
        +__str__() str
        +enriquecer_dashboard() dict
        +enriquecer_api() dict
        +create() Appointment
        +list_all(status) List
    }
    class Conversation {
        +id str
        +contact_name str
        +labels list
        +last_message dict
        -_phone_number str
        -_status str
        -_unread_count int
        +phone_number property
        +status property
        +unread_count property
        +from_db(doc) Conversation
        +to_dict() dict
        +__str__() str
        +find_or_create() Conversation
        +list_all(filters) List
    }
    class Message {
        +id str
        +conversation_id str
        +direction str
        +content dict
        +wa_message_id str
        +timestamp datetime
        -_status str
        +status property
        +from_db(doc) Message
        +to_dict() dict
        +__str__() str
        +create() Message
    }
    BaseModel <|-- Pet : hereda
    BaseModel <|-- Appointment : hereda
    BaseModel <|-- Conversation : hereda
    Appointment --> Pet : pet_id lookup
    Message --> Conversation : conversation_id
"""

DIAGRAMS["d2_template"] = """\
flowchart TD
    A["Ruta llama<br/>Pet.find_by_id(pet_id)"]:::blue --> B["BaseModel.find_by_id()"]
    B --> C{{"MongoDB<br/>find_one()"}}
    C -->|None| D["return None<br/>→ 404"]:::red
    C -->|document dict| E["cls.from_db(document)"]:::green
    E -->|Pet| F1["Pet instance"]:::green
    E -->|Appointment| F2["Appointment instance"]:::green
    E -->|Conversation| F3["Conversation instance"]:::green
    F1 --> G["obj.to_dict()"]:::blue
    F2 --> G
    F3 --> G
    G --> H["jsonify() → HTTP 200"]:::blue
    classDef blue fill:#1e3a5f,color:#fff,stroke:#0a1f3a
    classDef green fill:#1b6b3a,color:#fff,stroke:#0d4020
    classDef red fill:#8b1a1a,color:#fff,stroke:#5a0f0f
"""

DIAGRAMS["d3_webhook"] = """\
sequenceDiagram
    participant EA as Evolution API
    participant WH as webhook.py
    participant CV as Conversation
    participant HP as helpers.py
    participant MG as MongoDB
    participant FE as Frontend Socket.IO

    EA->>WH: POST /webhook {event: messages.upsert}
    WH->>CV: find_or_create(phone, contact_name)
    CV->>MG: find_one / insert_one
    MG-->>CV: document dict
    CV-->>WH: Conversation instance
    Note over WH: conv.id (no dict lookup)<br/>conv.contact_name (property)
    WH->>HP: save_message_and_notify(conv.id, ...)
    HP->>MG: Message.create() → insert_one
    MG-->>HP: document dict
    HP-->>HP: Message.from_db(doc) = instancia
    HP->>MG: Conversation.find_by_id(conv_id)
    MG-->>HP: Conversation instance
    HP->>FE: emit new_message  msg.to_dict()
    HP->>FE: emit conversation_updated  conv.to_dict()
"""

DIAGRAMS["d4_properties"] = """\
flowchart LR
    subgraph PET["Pet — Atributos PII"]
        direction TB
        P1["_owner_phone<br/>(private)"] <-->|"@property owner_phone<br/>setter: valida str no vacío"| P2["Acceso externo<br/>controlado"]
        P3["_owner_name<br/>(private)"] <-->|"@property owner_name<br/>setter: normaliza strip()"| P4["Nombre normalizado"]
    end
    subgraph APT["Appointment — Estado"]
        direction TB
        A1["_status<br/>(private)"] <-->|"@property status<br/>setter: valida STATUSES"| A2["'scheduled'<br/>'confirmed'<br/>'completed'<br/>'cancelled'"]
    end
    subgraph CONV["Conversation — PII Inmutable"]
        direction TB
        C1["_phone_number<br/>(private)"] -->|"@property phone_number<br/>SIN setter — read-only"| C2["Inmutable tras<br/>la creación"]
        C3["_unread_count<br/>(private)"] -->|"@property unread_count<br/>SIN setter — solo BD"| C4["Gestionado por<br/>update_last_message()"]
    end
"""


# ─────────────────────────────────────────────
# RENDERIZAR DIAGRAMAS
# ─────────────────────────────────────────────
def render(name: str, mmd: str) -> str | None:
    mmd_f = TMP_DIR / f"{name}.mmd"
    png_f = TMP_DIR / f"{name}.png"
    mmd_f.write_text(mmd, encoding="utf-8")
    cmd = (
        f'npx -y @mermaid-js/mermaid-cli '
        f'-i "{mmd_f}" -o "{png_f}" '
        f'--backgroundColor white -w 1400 -H 900'
    )
    r = subprocess.run(
        cmd, shell=True,
        capture_output=True, text=True, cwd=str(BASE_DIR), timeout=180
    )
    if r.returncode == 0 and png_f.exists():
        print(f"  OK  {name}")
        return str(png_f)
    print(f"  ERR {name}: {r.stderr[-300:]}")
    return None


# ─────────────────────────────────────────────
# CLASE PDF
# ─────────────────────────────────────────────
NAVY  = (15,  52,  96)
BLUE  = (0,  120, 180)
CYAN  = (0,  180, 216)
LGRAY = (240, 245, 250)
DGRAY = (50,  50,  50)
WHITE = (255, 255, 255)
ALTBG = (232, 241, 252)


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Ar",  "",  ARIAL)
        self.add_font("Ar",  "B", ARIAL_B)
        self.add_font("Ar",  "I", ARIAL_I)
        self.add_font("Ar",  "BI",ARIAL_BI)
        self.add_font("Co",  "",  COUR)
        self.add_font("Co",  "B", COUR_B)

    # ---- cabecera / pie ----
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 11, "F")
        self.set_font("Ar", "B", 8)
        self.set_text_color(*WHITE)
        self.set_xy(0, 1.5)
        self.cell(210, 8, "CONNECTA  ·  Bitácora Técnica  ·  Avance 9: POO Nivel I", align="C")
        self.set_text_color(*DGRAY)
        self.ln(6)

    def footer(self):
        self.set_y(-13)
        self.set_font("Ar", "I", 7.5)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"Página {self.page_no()}  ·  FESC — Diseño Funcional 2026", align="C")

    # ---- helpers ----
    def W(self):
        return self.w - self.l_margin - self.r_margin

    def h1(self, txt):
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        self.set_font("Ar", "B", 12)
        self.cell(0, 9, f"  {txt}", fill=True, ln=True)
        self.set_text_color(*DGRAY)
        self.ln(2)

    def h2(self, txt):
        self.set_font("Ar", "B", 10)
        self.set_text_color(*BLUE)
        self.set_x(self.l_margin + 2)
        self.cell(0, 7, txt, ln=True)
        self.set_text_color(*DGRAY)

    def body(self, txt, indent=4):
        self.set_font("Ar", "", 9.5)
        self.set_text_color(*DGRAY)
        self.set_x(self.l_margin + indent)
        self.multi_cell(self.W() - indent, 5.5, txt)
        self.ln(1)

    def bullet(self, txt, indent=8):
        self.set_font("Ar", "", 9.5)
        self.set_text_color(*DGRAY)
        self.set_x(self.l_margin + indent)
        self.cell(5, 5.5, "•")
        self.set_x(self.l_margin + indent + 5)
        self.multi_cell(self.W() - indent - 5, 5.5, txt)

    def code(self, txt):
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_font("Co", "", 7.5)
        self.set_text_color(30, 30, 100)
        self.multi_cell(self.W(), 4.8, txt, border=1, fill=True)
        self.set_text_color(*DGRAY)
        self.ln(2)

    def img(self, path, caption="", w=None):
        if not path or not Path(path).exists():
            self.set_font("Ar", "I", 9)
            self.set_text_color(180, 0, 0)
            self.cell(0, 7, "[Diagrama no disponible]", ln=True)
            self.set_text_color(*DGRAY)
            return
        iw = w or self.W()
        if self.get_y() > 230:
            self.add_page()
        x = self.l_margin + (self.W() - iw) / 2
        self.image(path, x=x, w=iw)
        if caption:
            self.set_font("Ar", "I", 7.5)
            self.set_text_color(110, 110, 110)
            self.cell(0, 5, caption, align="C", ln=True)
            self.set_text_color(*DGRAY)
        self.ln(3)

    def table(self, headers, rows, widths, alt=True):
        # header row
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        self.set_font("Ar", "B", 8)
        for h, w in zip(headers, widths):
            self.cell(w, 7, h, border=1, fill=True)
        self.ln()
        # data rows
        for i, row in enumerate(rows):
            if alt and i % 2 == 1:
                self.set_fill_color(*ALTBG)
            else:
                self.set_fill_color(*WHITE)
            self.set_text_color(*DGRAY)
            self.set_font("Ar", "", 8)
            for cell, w in zip(row, widths):
                self.cell(w, 6.5, str(cell), border=1, fill=True)
            self.ln()
        self.set_text_color(*DGRAY)
        self.ln(2)

    # ─────────────────────────────────────
    # PORTADA
    # ─────────────────────────────────────
    def portada(self):
        # banda navy
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 65, "F")
        # acento cyan
        self.set_fill_color(*CYAN)
        self.rect(0, 58, 210, 5, "F")

        self.set_text_color(*WHITE)
        self.set_font("Ar", "B", 34)
        self.set_xy(0, 12)
        self.cell(210, 16, "CONNECTA", align="C")
        self.set_font("Ar", "", 12)
        self.set_xy(0, 30)
        self.cell(210, 7, "Sistema Inteligente de Gestión Veterinaria  ·  B2B", align="C")
        self.set_font("Ar", "I", 9.5)
        self.set_xy(0, 40)
        self.cell(210, 6, "Python 3.11  ·  Flask 3.1.3  ·  MongoDB 7  ·  WhatsApp Business", align="C")

        # título principal
        self.set_text_color(*NAVY)
        self.set_font("Ar", "B", 20)
        self.set_xy(20, 78)
        self.multi_cell(170, 11, "Bitácora Técnica\nAvance 9 — Guía Práctica N°9", align="C")
        self.set_font("Ar", "B", 14)
        self.set_text_color(*BLUE)
        self.set_xy(20, 108)
        self.cell(170, 8, "Programación Orientada a Objetos (POO) Nivel I", align="C")

        # caja de datos
        self.set_fill_color(*LGRAY)
        self.set_draw_color(*BLUE)
        self.rect(28, 128, 154, 62, "FD")

        datos = [
            ("Curso",      "Diseño Funcional — FESC"),
            ("Estudiante", "Erick Santiago Ocampo Marciales"),
            ("Fecha",      "15 de mayo de 2026"),
            ("Commit",     "4401d08 → branch: main"),
            ("Archivos",   "13 modificados · +801 líneas / -368"),
            ("Stack",      "Python · Flask · MongoDB · Socket.IO"),
        ]
        y = 135
        for label, val in datos:
            self.set_font("Ar", "B", 8.5)
            self.set_text_color(*NAVY)
            self.set_xy(34, y)
            self.cell(32, 7, label + ":")
            self.set_font("Ar", "", 8.5)
            self.set_text_color(*DGRAY)
            self.set_xy(66, y)
            self.cell(108, 7, val)
            y += 9

        self.set_font("Ar", "I", 8)
        self.set_text_color(120, 120, 120)
        self.set_xy(0, 200)
        self.cell(210, 7, "github.com/AntionART/CONNECTA", align="C")


# ─────────────────────────────────────────────
# CONSTRUIR PDF
# ─────────────────────────────────────────────
def build(dp: dict) -> PDF:
    pdf = PDF()
    pdf.set_margins(15, 18, 15)
    pdf.set_auto_page_break(True, margin=20)

    # ── PORTADA ──────────────────────────────
    pdf.add_page()
    pdf.portada()

    # ── P1: RESUMEN EJECUTIVO ─────────────────
    pdf.add_page()
    pdf.h1("1. Resumen Ejecutivo")
    pdf.body(
        "El Avance 9 transforma los modelos de CONNECTA de \"namespaces con métodos "
        "estáticos\" a clases OOP completas con estado, comportamiento y encapsulamiento. "
        "El patrón Template Method aplicado en BaseModel permite que find_by_id() retorne "
        "instancias tipadas (Pet, Appointment, Conversation, Message) sin cambiar las rutas "
        "de Flask que ya las usaban."
    )
    pdf.ln(2)

    pdf.h2("Métricas del cambio")
    stats = [
        ["Entidades refactorizadas",  "4 (Pet, Appointment, Conversation, Message)"],
        ["Archivos modificados",       "13"],
        ["Líneas añadidas",            "+801"],
        ["Líneas eliminadas",          "-368"],
        ["@property / setters",        "9 (con validación)"],
        ["Métodos migrados a instancia","2 (enriquecer_dashboard, enriquecer_api)"],
        ["Atributos privados (_xxx)",   "7 en total (PII + estado)"],
        ["Commit hash",                 "4401d08 — rama main"],
    ]
    pdf.table(["Indicador", "Valor"], stats, [80, 100])

    # ── P2: ACTIVIDADES ──────────────────────
    pdf.h1("2. Actividades Implementadas")

    # Act 1
    pdf.h2("ACTIVIDAD 1 — Modelado de Entidades (__init__, from_db, to_dict, __str__, __repr__)")
    pdf.body(
        "Cada entidad ahora tiene un constructor explícito que declara todos sus atributos "
        "de instancia. from_db() actúa como factory desde MongoDB; to_dict() serializa de "
        "vuelta a JSON. Los atributos PII y de estado crítico se prefiján con _ para "
        "encapsulamiento según convención Python (PEP 8)."
    )
    headers1 = ["Clase", "Archivo", "__init__", "from_db", "to_dict", "__str__", "Privados"]
    rows1 = [
        ["Pet",          "models/pet.py",          "L23", "L49", "L68",  "L93",  "_owner_phone, _owner_name"],
        ["Appointment",  "models/appointment.py",  "L30", "L51", "L68",  "L95",  "_status"],
        ["Conversation", "models/conversation.py", "L23", "L54", "L73",  "L106", "_phone_number, _status, _unread_count"],
        ["Message",      "models/message.py",      "L22", "L44", "L63",  "L82",  "_status"],
        ["BaseModel",    "models/base.py",          "—",  "L22", "—",    "—",    "default from_db; find_by_id → cls.from_db"],
    ]
    pdf.table(headers1, rows1, [30, 48, 14, 14, 14, 14, 56])

    # Act 2
    pdf.h2("ACTIVIDAD 2 — Métodos y Properties")
    pdf.body(
        "@property con setter implementados para atributos sensibles. "
        "Dos funciones sueltas de rutas migradas como métodos de instancia con self."
    )
    headers2 = ["Property / Método", "Clase", "Línea", "Descripción"]
    rows2 = [
        ["owner_phone  +  setter",   "Pet",          "L108", "Valida str no vacío, strip()"],
        ["owner_name  +  setter",    "Pet",          "L121", "Normaliza: strip() o ''"],
        ["pertenece_a(phone)",        "Pet",          "L132", "Método instancia — compara PII"],
        ["status  +  setter",        "Appointment",  "L115", "Valida contra STATUSES[]"],
        ["enriquecer_dashboard()",   "Appointment",  "L133", "MIGRADO desde dashboard.py"],
        ["enriquecer_api()",         "Appointment",  "L148", "MIGRADO desde appointments.py"],
        ["phone_number (read-only)", "Conversation", "L124", "PII inmutable, sin setter"],
        ["status  +  setter",        "Conversation", "L130", "Valida 'open'/'closed'"],
        ["unread_count (read-only)", "Conversation", "L144", "Solo BD vía update_last_message"],
        ["status (read-only)",       "Message",      "L98",  "Pipeline entrega WhatsApp"],
    ]
    pdf.table(headers2, rows2, [58, 30, 14, 78])

    # Act 3
    pdf.h2("ACTIVIDAD 3 — Reingeniería del Sistema")
    pdf.body(
        "Las rutas Flask y el motor lógico (webhook, dashboard) usan ahora instancias "
        "tipadas: obj.to_dict() reemplaza serialize_doc(dict_crudo). El webhook accede a "
        "conv.id y conv.contact_name como atributos; el dashboard llama "
        "apt.enriquecer_dashboard() en lugar de una función suelta."
    )
    headers3 = ["Archivo", "Cambio clave", "Línea"]
    rows3 = [
        ["models/base.py",          "from_db() Template Method; find_by_id() delega",       "L22, L27"],
        ["routes/webhook.py",       "conv.id, conv.contact_name, ObjectId(msg.id)",         "L83, L87, L122"],
        ["routes/dashboard.py",     "Appointment.from_db(doc).enriquecer_dashboard()",       "L80"],
        ["routes/api/pets.py",      "[p.to_dict() for p in pets]",                          "L13"],
        ["routes/api/appointments.py","apt.enriquecer_api() — método del objeto",            "L29"],
        ["routes/api/conversations.py","[c.to_dict() for c in conversations]",               "L24"],
        ["routes/api/messages.py",  "conv.phone_number; msg.to_dict()",                     "L58, L69"],
        ["utils/helpers.py",        "msg.to_dict(), updated_conv.to_dict() en Socket.IO",   "L111, L113"],
    ]
    pdf.table(headers3, rows3, [65, 97, 18])

    # ── P3: DIAGRAMAS ───────────────────────
    pdf.add_page()
    pdf.h1("3. Diagramas Mermaid — Nueva Arquitectura OOP")

    pdf.h2("Diagrama 1 — Jerarquía de Clases (Mermaid classDiagram)")
    pdf.body(
        "Muestra la herencia BaseModel → Pet, Appointment, Conversation. "
        "Signos: + público, - privado (_atributo). Se omite Message de la jerarquía "
        "visual para simplificar; Message tiene la misma estructura OOP."
    )
    pdf.img(dp.get("d1_clases"), "Fig. 1 — Diagrama de clases OOP · CONNECTA Avance 9", w=174)

    pdf.add_page()
    pdf.h2("Diagrama 2 — Patrón Template Method en BaseModel (flowchart)")
    pdf.body(
        "BaseModel.find_by_id() llama a cls.from_db(doc) vía MRO de Python. "
        "Si el doc es None retorna None (→ 404 en la ruta). Si existe, la subclase "
        "construye su instancia tipada; la ruta llama obj.to_dict() para serializar a JSON."
    )
    pdf.img(dp.get("d2_template"), "Fig. 2 — Template Method: find_by_id() → cls.from_db() → obj.to_dict()", w=140)

    pdf.ln(3)
    pdf.h2("Diagrama 3 — Secuencia Webhook con Instancias OOP (sequenceDiagram)")
    pdf.body(
        "Flujo completo de un mensaje entrante de WhatsApp: find_or_create() retorna "
        "una instancia Conversation; el webhook accede a conv.id y conv.contact_name "
        "como atributos de objeto. Message.create() devuelve una instancia; helpers.py "
        "emite msg.to_dict() y conv.to_dict() a Socket.IO."
    )
    pdf.img(dp.get("d3_webhook"), "Fig. 3 — Secuencia: Evolution API → Webhook OOP → Frontend", w=174)

    pdf.add_page()
    pdf.h2("Diagrama 4 — Encapsulamiento con @property (flowchart)")
    pdf.body(
        "Muestra cómo los atributos privados son controlados: owner_phone valida str "
        "no vacío; status valida contra STATUSES[]; phone_number en Conversation no "
        "tiene setter (PII inmutable); unread_count solo es modificable por la BD."
    )
    pdf.img(dp.get("d4_properties"), "Fig. 4 — @property y setters: encapsulamiento de atributos sensibles", w=174)

    # ── P4: EVIDENCIA DE CÓDIGO ───────────────
    pdf.add_page()
    pdf.h1("4. Evidencia de Código")

    pdf.h2("Actividad 1 — Constructores y from_db (app/models/pet.py):")
    pdf.code("""\
# [GUÍA 9 - ACTIVIDAD 1] Constructor explícito con atributos tipados
def __init__(self, name: str, species: str, breed: str,
             age_years: float, weight_kg: float,
             owner_phone: str, owner_name: str = '',
             id: str = None, created_at=None, updated_at=None):
    self.id         = id
    self.name       = name
    self.species    = species
    self.age_years  = age_years      # float — 0.5 = 6 meses
    self.weight_kg  = weight_kg      # float — decimales
    self._owner_phone = owner_phone  # PII — prefijo _
    self._owner_name  = owner_name   # PII — prefijo _

# [GUÍA 9 - ACTIVIDAD 1] from_db — puente MongoDB → objeto Python
@classmethod
def from_db(cls, document: dict) -> 'Pet':
    if document is None:
        return None
    return cls(
        id=str(document['_id']),
        name=document.get('name', ''),
        owner_phone=document.get('owner_phone', ''),
        ...
    )

# [GUÍA 9 - ACTIVIDAD 1] to_dict — puente objeto Python → JSON REST
def to_dict(self) -> dict:
    return {
        '_id': self.id,
        'name': self.name,
        'owner_phone': self._owner_phone,   # accede al atributo privado
        'created_at': self.created_at.isoformat() if isinstance(...) else ...,
    }""")

    pdf.h2("Actividad 2 — @property, setter y método migrado (app/models/appointment.py):")
    pdf.code("""\
# [GUÍA 9 - ACTIVIDAD 2] @property con validación de ciclo de vida
@property
def status(self) -> str:
    return self._status

@status.setter
def status(self, value: str):
    if value not in Appointment.STATUSES:  # ['scheduled','confirmed','completed','cancelled']
        raise ValueError(f"status inválido '{value}'. Debe ser uno de: {Appointment.STATUSES}")
    self._status = value

# [GUÍA 9 - ACTIVIDAD 2] Método migrado desde dashboard.py._enriquecer_cita_dashboard()
def enriquecer_dashboard(self) -> dict:
    from app.models.pet import Pet          # import tardío — evita circularidad
    pet = Pet.find_by_id(self.pet_id)       # find_by_id → instancia Pet (no dict)
    result = self.to_dict()
    result['pet_name'] = pet.name if pet else 'Desconocida'
    return result

# [GUÍA 9 - ACTIVIDAD 2] Método migrado desde appointments.py._enrich_appointment()
def enriquecer_api(self) -> dict:
    from app.models.pet import Pet
    pet = Pet.find_by_id(self.pet_id)
    result = self.to_dict()
    result['pet'] = pet.to_dict() if pet else None
    return result""")

    pdf.h2("Actividad 3 — Reingeniería en webhook.py y dashboard.py:")
    pdf.code("""\
# app/routes/webhook.py  [GUÍA 9 - ACTIVIDAD 3]
# ANTES (dict crudo):
#   conv = Conversation.find_or_create(phone, name)  # → dict
#   conv_id = str(conv['_id'])
#   if contact_name and not conv.get('contact_name'):
#
# DESPUÉS (instancia Conversation):
conv = Conversation.find_or_create(phone, contact_name)  # → Conversation
conv_id = conv.id                         # atributo de instancia
if contact_name and not conv.contact_name:    # @property, no dict lookup
    Conversation.update(conv_id, {'contact_name': contact_name})

# app/routes/dashboard.py  [GUÍA 9 - ACTIVIDAD 3]
# ANTES: map(_enriquecer_cita_dashboard, upcoming_appointments)  ← función suelta
# DESPUÉS: método del objeto
upcoming_appointments = list(map(
    lambda doc: Appointment.from_db(doc).enriquecer_dashboard(),
    upcoming_apts_docs
))

# app/routes/api/pets.py  [GUÍA 9 - ACTIVIDAD 3]
# ANTES: return jsonify(serialize_docs(pets))   ← lista de dicts crudos
# DESPUÉS:
pets = Pet.list_all()                     # List[Pet] — instancias tipadas
return jsonify([p.to_dict() for p in pets])""")

    # ── P5: NOTAS ARQUITECTÓNICAS ─────────────
    pdf.add_page()
    pdf.h1("5. Notas Arquitectónicas y Decisiones de Diseño")

    notas = [
        ("Patrón Template Method en BaseModel",
         "BaseModel.find_by_id() llama a cls.from_db(doc). Gracias al MRO de Python, "
         "Pet.find_by_id() usa Pet.from_db() automáticamente. Modelos auxiliares (Label, "
         "Settings) usan el from_db() por defecto de BaseModel (retorna el dict crudo), "
         "garantizando compatibilidad backward sin cambios adicionales."),
        ("__init__ no hace queries a MongoDB",
         "El constructor solo inicializa atributos en memoria. La consulta a MongoDB ocurre "
         "exclusivamente en los métodos estáticos (create, find_by_id, list_all). Esto "
         "mantiene separación de capas: __init__ es Python puro, los métodos estáticos "
         "son la capa de acceso a datos."),
        ("phone_number es read-only en Conversation",
         "El número de teléfono es la clave primaria natural de un hilo WhatsApp. "
         "Cambiar el teléfono rompería la identidad de la conversación. Se define "
         "únicamente con getter (sin setter) para imponer esta invariante de dominio."),
        ("Imports tardíos para evitar circularidad",
         "Appointment.enriquecer_dashboard() hace `from app.models.pet import Pet` "
         "dentro del método. Esto evita el error de importación circular entre "
         "appointment.py y pet.py, los cuales están en el mismo paquete models/."),
        ("Funciones transversales NO migradas a clases",
         "validar_campos_requeridos() (helpers.py) opera sobre cualquier dict. "
         "_coincide, detectar_intencion(), generar_respuesta() (nlp.py) procesan texto "
         "puro sin relación con entidades del dominio. Migrarlas hubiera violado SRP. "
         "Cada una incluye un comentario explicando por qué permanece fuera de una clase."),
        ("to_dict() como reemplazo de serialize_doc()",
         "serialize_doc() sigue disponible para Label (que retorna dict crudo). "
         "Para las entidades refactorizadas (Pet, Appointment, Conversation, Message), "
         "to_dict() produce el mismo formato JSON — pero con manejo explícito de "
         "datetime.isoformat() y str(id), sin depender de inspección de tipos externa."),
    ]

    for i, (titulo, cuerpo) in enumerate(notas):
        pdf.set_font("Ar", "B", 9.5)
        pdf.set_text_color(*BLUE)
        pdf.set_x(pdf.l_margin + 2)
        pdf.cell(0, 7, f"  {i+1}.  {titulo}", ln=True)
        pdf.body(cuerpo, indent=10)
        pdf.ln(1)

    # ── P6: COMMIT ─────────────────────────────
    pdf.h1("6. Registro de Commit Git")
    pdf.code("""\
$ git log -1 --format="%H %s"
4401d08 feat(avance9): implement OOP Level I — classes, properties, instance methods

Branch: main
Remote: https://github.com/AntionART/CONNECTA.git
Status: pushed [OK]

Archivos modificados (13):
  ACTIVITY_MAPPING.md          | +150 líneas (sección Guía 9 + checklist)
  app/models/base.py           |  from_db() + find_by_id() Template Method
  app/models/pet.py            |  OOP completo + @property owner_phone/owner_name
  app/models/appointment.py    |  OOP completo + enriquecer_dashboard/api()
  app/models/conversation.py   |  OOP completo + @property (PII, estado, contador)
  app/models/message.py        |  OOP completo + @property status
  app/routes/webhook.py        |  conv.id, conv.contact_name, import Message
  app/routes/dashboard.py      |  from_db().enriquecer_dashboard() vía map()
  app/routes/api/pets.py       |  [p.to_dict() for p in pets]
  app/routes/api/appointments.py | apt.enriquecer_api()
  app/routes/api/conversations.py| [c.to_dict() for c in conversations]
  app/routes/api/messages.py   |  conv.phone_number, msg.to_dict()
  app/utils/helpers.py         |  msg.to_dict(), updated_conv.to_dict()

 13 files changed, 801 insertions(+), 368 deletions(-)\
""")

    return pdf


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Bitácora Técnica — Avance 9: POO Nivel I")
    print("=" * 60)

    print("\n[1/3] Renderizando diagramas Mermaid...")
    dp = {name: render(name, mmd) for name, mmd in DIAGRAMS.items()}

    print("\n[2/3] Construyendo PDF...")
    pdf = build(dp)

    print(f"\n[3/3] Guardando: {OUTPUT_PDF.name}")
    pdf.output(str(OUTPUT_PDF))

    shutil.rmtree(TMP_DIR, ignore_errors=True)
    print(f"\n  PDF listo: {OUTPUT_PDF}")
    print("=" * 60)


if __name__ == "__main__":
    main()
