"""
CONNECTA - Sistema Inteligente de Gestion Veterinaria
Integracion con WhatsApp Business mediante Evolution API

Proyecto: Diseno Funcional - FESC
Autores: Erick Ocampo, Daniel Arteaga, Andres Rodriguez
Fecha: Febrero 2026
Paradigma: Programacion Funcional
Lenguaje: Python 3.8+

Avance 2: Sintaxis Basica y Gestion de Colecciones
- Actividad 1: Validacion de Conceptos (Quiz completado)
- Actividad 2: Estructuracion del Core de Datos (Variables y Sintaxis)
- Actividad 3: Gestion de Cadenas y Colecciones (Strings y Lists)
- Actividad 4: Logica Aritmetica y Comparativa (Operadores)
"""

from datetime import datetime
from typing import List, Dict


# ============================================================================
# SECCION 1: VARIABLES GLOBALES - DATOS FIJOS DEL SISTEMA
# ============================================================================

# ---- VARIABLES ALFANUMERICAS (Strings) ----

clinic_name = "VetClinic Central Bogota"
clinic_phone = "+57 1 2345678"
clinic_phone_whatsapp = "+57 320 1234567"
clinic_address = "Carrera 5 #12-34, Bogota, Colombia"
clinic_email = "contacto@vetclinic-connecta.com"
clinic_website = "www.vetclinic-connecta.com"

system_version = "1.0.0"
system_name = "CONNECTA"
api_endpoint_evolution = "http://localhost:3000"

service_hours_start = "08:00"
service_hours_end = "18:00"
lunch_break_start = "12:00"
lunch_break_end = "13:00"

# ---- VARIABLES NUMERICAS ----

max_appointments_per_day = 15
appointment_duration_minutes = 30
emergency_buffer_minutes = 15

consultation_fee_base = 50000.0      # Pesos colombianos
vaccination_fee = 35000.0
surgical_fee = 150000.0
lab_test_fee = 25000.0

service_tax_percentage = 0.19        # IVA 19%
discount_percentage_loyalty = 0.10  # 10% clientes frecuentes

clinic_operational_hours_per_day = 9
working_days_per_week = 6

# ---- VARIABLES BOOLEANAS ----

system_active = True
enable_ai_responses = True
enable_whatsapp_integration = True
maintenance_mode = False
require_appointment_confirmation = True


# ============================================================================
# SECCION 2: LISTAS Y COLECCIONES DE DATOS
# ============================================================================

# ---- LISTA 1: PACIENTES ----

patients: List[Dict] = [
    {
        "id": "P001",
        "name": "Max",
        "species": "Canino",
        "breed": "Labrador Retriever",
        "owner": "Juan Perez Garcia",
        "age_years": 5,
        "weight_kg": 32.5,
        "health_status": "Saludable"
    },
    {
        "id": "P002",
        "name": "Luna",
        "species": "Felino",
        "breed": "Siames",
        "owner": "Maria Lopez Gonzalez",
        "age_years": 3,
        "weight_kg": 3.8,
        "health_status": "Saludable"
    },
    {
        "id": "P003",
        "name": "Rocky",
        "species": "Canino",
        "breed": "Pastor Aleman",
        "owner": "Carlos Rodriguez",
        "age_years": 7,
        "weight_kg": 35.0,
        "health_status": "Con seguimiento"
    },
    {
        "id": "P004",
        "name": "Whiskers",
        "species": "Felino",
        "breed": "Persa",
        "owner": "Ana Martinez",
        "age_years": 2,
        "weight_kg": 4.2,
        "health_status": "Saludable"
    },
    {
        "id": "P005",
        "name": "Buddy",
        "species": "Canino",
        "breed": "Beagle",
        "owner": "Roberto Sanchez",
        "age_years": 4,
        "weight_kg": 12.0,
        "health_status": "Saludable"
    }
]

# ---- LISTA 2: SERVICIOS VETERINARIOS ----

services: List[Dict] = [
    {
        "id": "S001",
        "name": "Consulta General",
        "description": "Evaluacion clinica completa del paciente",
        "price": 50000.0,
        "duration_minutes": 30,
        "category": "Consulta"
    },
    {
        "id": "S002",
        "name": "Vacunacion",
        "description": "Administracion de vacunas segun esquema",
        "price": 35000.0,
        "duration_minutes": 20,
        "category": "Preventiva"
    },
    {
        "id": "S003",
        "name": "Cirugia General",
        "description": "Procedimiento quirurgico mayor",
        "price": 150000.0,
        "duration_minutes": 90,
        "category": "Quirurgica"
    },
    {
        "id": "S004",
        "name": "Laboratorio Clinico",
        "description": "Examenes de sangre y analisis",
        "price": 25000.0,
        "duration_minutes": 15,
        "category": "Diagnostico"
    },
    {
        "id": "S005",
        "name": "Limpieza Dental",
        "description": "Limpieza profesional de dientes",
        "price": 80000.0,
        "duration_minutes": 45,
        "category": "Preventiva"
    },
    {
        "id": "S006",
        "name": "Ecografia",
        "description": "Estudio ecografico del paciente",
        "price": 60000.0,
        "duration_minutes": 30,
        "category": "Diagnostico"
    }
]

# ---- LISTA 3: CITAS AGENDADAS ----

appointments: List[Dict] = [
    {
        "id": "A001",
        "patient_id": "P001",
        "patient_name": "Max",
        "date": "2026-02-21",
        "time": "09:00",
        "service_name": "Consulta General",
        "veterinarian": "Dr. Lopez",
        "owner": "Juan Perez Garcia",
        "status": "Confirmada"
    },
    {
        "id": "A002",
        "patient_id": "P002",
        "patient_name": "Luna",
        "date": "2026-02-21",
        "time": "10:00",
        "service_name": "Vacunacion",
        "veterinarian": "Dra. Rodriguez",
        "owner": "Maria Lopez Gonzalez",
        "status": "Confirmada"
    },
    {
        "id": "A003",
        "patient_id": "P003",
        "patient_name": "Rocky",
        "date": "2026-02-21",
        "time": "14:00",
        "service_name": "Laboratorio Clinico",
        "veterinarian": "Dr. Martinez",
        "owner": "Carlos Rodriguez",
        "status": "Pendiente confirmacion"
    }
]

# ---- LISTA 4: PERSONAL VETERINARIO ----

veterinarians: List[Dict] = [
    {
        "id": "V001",
        "name": "Dr. Luis Lopez",
        "specialization": "Medicina General",
        "phone": "+57 320 1111111",
        "email": "llopez@vetclinic.com",
        "license": "MV-2015-001"
    },
    {
        "id": "V002",
        "name": "Dra. Carmen Rodriguez",
        "specialization": "Cirugia Veterinaria",
        "phone": "+57 320 2222222",
        "email": "crodriguez@vetclinic.com",
        "license": "MV-2016-002"
    },
    {
        "id": "V003",
        "name": "Dr. Jorge Martinez",
        "specialization": "Diagnostico por Imagen",
        "phone": "+57 320 3333333",
        "email": "jmartinez@vetclinic.com",
        "license": "MV-2014-003"
    }
]

# ---- LISTA 5: CONSULTAS FRECUENTES (FAQ) ----

common_queries: List[str] = [
    "Cual es el horario de atencion de la clinica?",
    "Cuanto cuesta una consulta general?",
    "Como agendar una cita en CONNECTA?",
    "Mi mascota esta enferma, que hago?",
    "Cuales son los requisitos para agendar cirugia?",
    "Ofrecen servicio de urgencias 24/7?",
    "Se puede hacer seguimiento remoto de mi mascota?",
    "Cuales son los metodos de pago aceptados?",
    "Necesito vacunas previas antes de una cirugia?",
    "Cual es el protocolo de emergencia veterinaria?"
]


# ============================================================================
# SECCION 3: FUNCIONES - OPERADORES DE STRINGS
# ============================================================================

def normalize_veterinary_text(text: str) -> str:
    """
    Normaliza texto veterinario eliminando espacios extras y convirtiendo
    a minusculas para consistencia en el procesamiento NLP.

    Args:
        text (str): Texto a normalizar

    Returns:
        str: Texto normalizado

    Ejemplo:
        >>> normalize_veterinary_text("  MI GATO TIENE DIARREA  ")
        'mi gato tiene diarrea'
    """
    normalized = text.strip().lower()
    normalized = normalized.replace("  ", " ")
    return normalized


def format_clinic_contact_info() -> str:
    """
    Formatea la informacion de contacto de la clinica como string
    listo para enviarse por WhatsApp.

    Returns:
        str: Texto formateado con datos de contacto
    """
    contact_info = (
        f"{clinic_name}\n"
        f"Telefono: {clinic_phone}\n"
        f"WhatsApp: {clinic_phone_whatsapp}\n"
        f"Email: {clinic_email}\n"
        f"Direccion: {clinic_address}\n"
        f"Horario: {service_hours_start} - {service_hours_end}"
    )
    return contact_info


# ============================================================================
# SECCION 4: FUNCIONES - OPERADORES ARITMETICOS
# ============================================================================

def calculate_total_service_cost(
    service_price: float,
    tax_percentage: float = service_tax_percentage
) -> float:
    """
    Calcula el costo total del servicio incluyendo IVA.
    Operadores: + (suma), * (multiplicacion)

    Args:
        service_price (float): Precio base del servicio
        tax_percentage (float): Porcentaje de impuesto (default 0.19)

    Returns:
        float: Precio total incluyendo IVA

    Ejemplo:
        >>> calculate_total_service_cost(50000)
        59500.0
    """
    tax_amount = service_price * tax_percentage
    total_cost = service_price + tax_amount
    return round(total_cost, 2)


def calculate_appointment_duration_block(
    num_appointments: int,
    duration_per_appointment: int = appointment_duration_minutes
) -> int:
    """
    Calcula la duracion total de un bloque de citas.
    Operadores: * (multiplicacion)

    Args:
        num_appointments (int): Numero de citas en el bloque
        duration_per_appointment (int): Minutos por cita (default 30)

    Returns:
        int: Duracion total en minutos

    Ejemplo:
        >>> calculate_appointment_duration_block(5)
        150
    """
    return num_appointments * duration_per_appointment


def calculate_clinic_daily_revenue(
    appointments_completed: int,
    average_service_price: float = consultation_fee_base
) -> float:
    """
    Calcula los ingresos diarios de la clinica.
    Operadores: * (multiplicacion)

    Args:
        appointments_completed (int): Citas realizadas en el dia
        average_service_price (float): Precio promedio de servicio

    Returns:
        float: Ingresos totales del dia
    """
    return appointments_completed * average_service_price


def calculate_weight_change_percentage(
    initial_weight: float,
    final_weight: float
) -> float:
    """
    Calcula el porcentaje de cambio de peso de un paciente.
    Operadores: - (resta), / (division), * (multiplicacion)

    Args:
        initial_weight (float): Peso inicial en kg
        final_weight (float): Peso final en kg

    Returns:
        float: Porcentaje de cambio de peso
    """
    if initial_weight == 0:
        return 0.0
    weight_difference = final_weight - initial_weight
    percentage = (weight_difference / initial_weight) * 100
    return round(percentage, 2)


# ============================================================================
# SECCION 5: FUNCIONES - OPERADORES DE COMPARACION
# ============================================================================

def is_clinic_open(current_time: str) -> bool:
    """
    Verifica si la clinica esta abierta en la hora dada.
    Operadores: >= , <=, not

    Args:
        current_time (str): Hora en formato HH:MM

    Returns:
        bool: True si esta abierta, False si esta cerrada
    """
    is_after_opening = current_time >= service_hours_start
    is_before_closing = current_time <= service_hours_end
    is_not_lunch = not (lunch_break_start <= current_time <= lunch_break_end)
    return is_after_opening and is_before_closing and is_not_lunch


def is_appointment_slot_available(slots_remaining: int) -> bool:
    """
    Verifica si hay espacios disponibles para agendar.
    Operadores: > (mayor que)

    Args:
        slots_remaining (int): Espacios restantes en el dia

    Returns:
        bool: True si hay disponibilidad
    """
    return slots_remaining > 0


def is_valid_phone_format(phone: str) -> bool:
    """
    Valida si el formato del telefono colombiano es correcto.
    Formato esperado: +57 3XX XXXXXXX

    Args:
        phone (str): Numero telefonico a validar

    Returns:
        bool: True si el formato es valido
    """
    has_country_code = phone.startswith("+57")
    digits_only = "".join(c for c in phone if c.isdigit())
    correct_length = len(digits_only) == 12
    return has_country_code and correct_length


def is_patient_adult(age_years: int) -> bool:
    """
    Verifica si el paciente es adulto (criterio: mayor de 2 anos).
    Operadores: > (mayor que)

    Args:
        age_years (int): Edad del paciente en anos

    Returns:
        bool: True si es adulto
    """
    return age_years > 2


# ============================================================================
# SECCION 6: FUNCIONES - OPERADORES LOGICOS
# ============================================================================

def can_schedule_appointment(
    clinic_is_open: bool,
    slots_available: bool,
    patient_registered: bool
) -> bool:
    """
    Determina si es posible agendar una cita.
    Todas las condiciones deben cumplirse.
    Operador: and

    Args:
        clinic_is_open (bool): Si la clinica esta abierta
        slots_available (bool): Si hay espacios disponibles
        patient_registered (bool): Si el paciente esta registrado

    Returns:
        bool: True si se puede agendar
    """
    return clinic_is_open and slots_available and patient_registered


def needs_immediate_attention(
    is_symptomatic: bool,
    is_emergency: bool
) -> bool:
    """
    Determina si el paciente necesita atencion inmediata.
    Basta con que una condicion sea verdadera.
    Operador: or

    Args:
        is_symptomatic (bool): Si tiene sintomas
        is_emergency (bool): Si es emergencia

    Returns:
        bool: True si necesita atencion inmediata
    """
    return is_symptomatic or is_emergency


def should_send_reminder(
    appointment_is_tomorrow: bool,
    patient_has_phone: bool
) -> bool:
    """
    Determina si debe enviarse recordatorio de cita por WhatsApp.
    Operador: and

    Args:
        appointment_is_tomorrow (bool): Si la cita es manana
        patient_has_phone (bool): Si tiene telefono registrado

    Returns:
        bool: True si debe enviar recordatorio
    """
    return appointment_is_tomorrow and patient_has_phone


def is_eligible_for_discount(
    has_membership: bool,
    is_returning_customer: bool,
    appointment_count: int
) -> bool:
    """
    Determina si el paciente es elegible para descuento por lealtad.
    Basta con cumplir una condicion.
    Operador: or

    Args:
        has_membership (bool): Si tiene membresia
        is_returning_customer (bool): Si es cliente frecuente
        appointment_count (int): Numero de citas previas

    Returns:
        bool: True si es elegible para descuento
    """
    return has_membership or is_returning_customer or appointment_count >= 5


# ============================================================================
# SECCION 7: FUNCION PRINCIPAL
# ============================================================================

def main() -> None:
    """Funcion principal que demuestra todas las actividades del Avance 2."""

    sep = "=" * 70

    # ---- Inicio ----
    print(f"\n{sep}")
    print(f"  {system_name} v{system_version} - INICIALIZANDO")
    print(f"{sep}")
    print(f"  Sistema activo:              {system_active}")
    print(f"  Integracion WhatsApp:        {enable_whatsapp_integration}")
    print(f"  Respuestas IA habilitadas:   {enable_ai_responses}")
    print(f"  Modo mantenimiento:          {maintenance_mode}")

    # ---- ACTIVIDAD 2: Variables del sistema ----
    print(f"\n{sep}")
    print("  ACTIVIDAD 2: DATOS FIJOS DEL SISTEMA")
    print(f"{sep}")
    print(f"\n{format_clinic_contact_info()}")
    print(f"\n  Parametros operacionales:")
    print(f"    Maximo citas/dia:    {max_appointments_per_day}")
    print(f"    Duracion por cita:   {appointment_duration_minutes} min")
    print(f"    Tarifa base:         ${consultation_fee_base:,.0f}")
    print(f"    IVA:                 {service_tax_percentage * 100:.0f}%")
    print(f"    Descuento lealtad:   {discount_percentage_loyalty * 100:.0f}%")

    # ---- ACTIVIDAD 3: Colecciones ----
    print(f"\n{sep}")
    print("  ACTIVIDAD 3: GESTION DE COLECCIONES")
    print(f"{sep}")

    print(f"\n  PACIENTES ({len(patients)}):")
    for p in patients:
        print(f"    [{p['id']}] {p['name']} - {p['breed']} | "
              f"Dueno: {p['owner']} | Edad: {p['age_years']} anos")

    print(f"\n  SERVICIOS ({len(services)}):")
    for s in services:
        print(f"    [{s['id']}] {s['name']:<20} "
              f"${s['price']:>8,.0f}  |  {s['duration_minutes']} min")

    print(f"\n  CITAS AGENDADAS ({len(appointments)}):")
    for a in appointments:
        print(f"    [{a['id']}] {a['patient_name']:<10} "
              f"{a['date']} {a['time']}  |  {a['service_name']}")

    print(f"\n  VETERINARIOS ({len(veterinarians)}):")
    for v in veterinarians:
        print(f"    [{v['id']}] {v['name']:<25} {v['specialization']}")

    print(f"\n  PREGUNTAS FRECUENTES ({len(common_queries)}):")
    for i, q in enumerate(common_queries, 1):
        print(f"    {i:>2}. {q}")

    # ---- ACTIVIDAD 4: Operadores ----
    print(f"\n{sep}")
    print("  ACTIVIDAD 4: OPERADORES ARITMETICOS Y LOGICOS")
    print(f"{sep}")

    print("\n  -- ARITMETICOS --")

    total = calculate_total_service_cost(50000)
    print(f"  Consulta $50,000 + IVA 19% = ${total:,.0f}")

    block = calculate_appointment_duration_block(5)
    print(f"  5 citas x 30 min = {block} minutos")

    revenue = calculate_clinic_daily_revenue(10)
    print(f"  10 citas x $50,000 = ${revenue:,.0f}/dia")

    pct = calculate_weight_change_percentage(32.0, 35.2)
    print(f"  Cambio de peso 32kg -> 35.2kg = {pct}%")

    print("\n  -- COMPARACION --")

    for time in ["09:00", "12:30", "19:00"]:
        status = "ABIERTA" if is_clinic_open(time) else "CERRADA"
        print(f"  {time} -> Clinica {status}")

    for slots in [0, 5]:
        status = "Hay espacios" if is_appointment_slot_available(slots) else "Sin disponibilidad"
        print(f"  Espacios restantes {slots} -> {status}")

    for phone in ["+57 320 1234567", "320 1234567"]:
        status = "VALIDO" if is_valid_phone_format(phone) else "INVALIDO"
        print(f"  {phone} -> {status}")

    print("\n  -- LOGICOS --")

    result = can_schedule_appointment(True, True, True)
    print(f"  Agendar cita (abierta AND espacios AND registrado): {result}")

    result = needs_immediate_attention(True, False)
    print(f"  Atencion inmediata (sintomat. OR emergencia): {result}")

    result = should_send_reminder(True, True)
    print(f"  Enviar recordatorio (manana AND tiene telefono): {result}")

    result = is_eligible_for_discount(False, True, 7)
    print(f"  Descuento (membresia OR frecuente OR >=5 citas): {result}")

    # ---- Cierre ----
    print(f"\n{sep}")
    print("  Avance 2 completado | Paradigma funcional aplicado | PEP 8")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
