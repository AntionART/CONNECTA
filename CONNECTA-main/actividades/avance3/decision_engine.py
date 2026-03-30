"""
CONNECTA - Motor de Decisiones
Avance 3: Estructuras de Control y Logica de Negocio

Proyecto: Diseno Funcional - FESC
Autores: Erick Ocampo, Daniel Arteaga, Andres Rodriguez
Fecha: Febrero 2026
Sesion: 27/02/2026

Contenido:
- Regla 1: Clasificacion y enrutamiento de consultas (if/elif/else)
- Regla 2: Gestion de disponibilidad de citas (logica anidada)
- Regla 3: Evaluacion de prioridad (operadores logicos)
- Regla 4: Seguimiento post-consulta
- Regla 5: Validacion de datos y edge cases
"""

from typing import Optional


# ============================================================================
# SECCION 1: CONSTANTES DEL SISTEMA
# ============================================================================

CLINIC_NAME = "CONNECTA Veterinaria"
VETERINARIANS_AVAILABLE = 3
AVAILABLE_SLOTS = ["08:00", "09:00", "10:00", "14:00", "15:00", "16:00"]

# Rangos validos de temperatura (grados Celsius)
TEMP_MIN_NORMAL = 37.5
TEMP_MAX_NORMAL = 39.0
TEMP_CRITICAL_HIGH = 40.0
TEMP_CRITICAL_LOW = 36.0

# Rangos validos de edad (anos)
AGE_MIN = 0
AGE_MAX = 30

# Dias de seguimiento por tipo de diagnostico
FOLLOWUP_DAYS_CRITICAL = 1
FOLLOWUP_DAYS_STANDARD = 3
FOLLOWUP_DAYS_MONITORING = 7


# ============================================================================
# SECCION 2: REGLA 1 - CLASIFICACION DE CONSULTAS (if/elif/else)
# ============================================================================

def classify_query(query_type: str, urgent: bool = False) -> dict:
    """
    Clasifica la consulta entrante de WhatsApp y determina su destino
    y nivel de urgencia.

    Regla de negocio: Las consultas informativas las resuelve el chatbot.
    Las medicas y de diagnostico las atiende un veterinario humano.

    Args:
        query_type (str): Tipo de consulta recibida
        urgent (bool): Si el cliente indico urgencia

    Returns:
        dict: Destino, urgencia y accion a tomar
    """
    if query_type == "emergencia" and urgent:
        destination = "veterinario_inmediato"
        urgency = "alta"
        action = "Notificar veterinario de turno de inmediato"

    elif query_type == "diagnostico":
        destination = "veterinario_humano"
        urgency = "media"
        action = "Asignar a cola de veterinario disponible"

    elif query_type == "urgencia_medica":
        destination = "veterinario_humano"
        urgency = "alta"
        action = "Escalar a veterinario y registrar caso"

    elif query_type == "cita_agendada":
        destination = "chatbot_confirmar"
        urgency = "baja"
        action = "Confirmar detalles de cita existente"

    elif query_type == "pregunta_general" or query_type == "horarios":
        destination = "chatbot_responder"
        urgency = "baja"
        action = "Responder automaticamente con informacion de la clinica"

    elif query_type == "seguimiento":
        destination = "chatbot_seguimiento"
        urgency = "baja"
        action = "Consultar historial y enviar recomendaciones"

    else:
        destination = "cola_general"
        urgency = "normal"
        action = "Agregar a cola de espera general"

    return {
        "query_type": query_type,
        "destination": destination,
        "urgency": urgency,
        "action": action
    }


# ============================================================================
# SECCION 3: REGLA 2 - DISPONIBILIDAD DE CITAS (Logica Anidada)
# ============================================================================

def validate_appointment(
    client_registered: bool,
    pet_valid: bool,
    requested_slot: str,
    vet_id: int
) -> dict:
    """
    Valida si es posible agendar una cita aplicando logica anidada.

    Regla de negocio: Primero se validan los datos del cliente y mascota,
    luego se verifica disponibilidad de horario y veterinario.

    Args:
        client_registered (bool): Si el cliente existe en el sistema
        pet_valid (bool): Si la mascota tiene datos completos
        requested_slot (str): Horario solicitado (formato HH:MM)
        vet_id (int): ID del veterinario solicitado

    Returns:
        dict: Estado de la cita, reminder y motivo si fue rechazada
    """
    if client_registered and pet_valid:
        slot_available = requested_slot in AVAILABLE_SLOTS
        vet_active = 1 <= vet_id <= VETERINARIANS_AVAILABLE

        if slot_available and vet_active:
            status = "confirmada"
            send_reminder = True
            propose_alternatives = False
            reason = None
        else:
            status = "en_espera"
            send_reminder = False
            propose_alternatives = True
            reason = "Horario o veterinario no disponible"
    else:
        status = "rechazada"
        send_reminder = False
        propose_alternatives = False
        reason = "Datos incompletos: cliente o mascota no registrados"

    return {
        "status": status,
        "send_reminder": send_reminder,
        "propose_alternatives": propose_alternatives,
        "reason": reason
    }


# ============================================================================
# SECCION 4: REGLA 3 - PRIORIDAD DE ATENCION (Operadores Logicos)
# ============================================================================

def evaluate_priority(
    is_frequent_client: bool,
    is_emergency: bool,
    is_blocked: bool,
    is_followup: bool,
    has_complete_history: bool
) -> dict:
    """
    Determina la prioridad de atencion usando operadores logicos (and, or, not).

    Regla de negocio: Clientes frecuentes o emergencias se atienden
    inmediatamente siempre que no esten bloqueados.

    Args:
        is_frequent_client (bool): Si es cliente frecuente
        is_emergency (bool): Si es una emergencia
        is_blocked (bool): Si el cliente esta bloqueado en el sistema
        is_followup (bool): Si es una consulta de seguimiento
        has_complete_history (bool): Si tiene historial clinico completo

    Returns:
        dict: Nivel de prioridad y accion asignada
    """
    if (is_frequent_client or is_emergency) and not is_blocked:
        priority = "inmediata"
        attend_now = True
        action = "Atender de inmediato, notificar veterinario"

    elif is_followup and has_complete_history:
        priority = "en_turno"
        attend_now = False
        action = "Atender en proximo turno disponible con historial cargado"

    elif is_blocked:
        priority = "suspendida"
        attend_now = False
        action = "Notificar bloqueo al cliente y derivar a administracion"

    else:
        priority = "general"
        attend_now = False
        action = "Agregar a cola general de atencion"

    return {
        "priority": priority,
        "attend_now": attend_now,
        "action": action
    }


# ============================================================================
# SECCION 5: REGLA 4 - SEGUIMIENTO POST-CONSULTA
# ============================================================================

def handle_post_consultation(
    consultation_completed: bool,
    diagnosis_registered: bool,
    requires_followup: bool,
    medicines_prescribed: bool
) -> dict:
    """
    Determina las acciones automaticas despues de completar una consulta.

    Regla de negocio: Toda consulta completada con diagnostico genera
    acciones automaticas de seguimiento via WhatsApp.

    Args:
        consultation_completed (bool): Si la consulta fue completada
        diagnosis_registered (bool): Si el diagnostico fue registrado
        requires_followup (bool): Si el diagnostico requiere seguimiento
        medicines_prescribed (bool): Si se prescribieron medicamentos

    Returns:
        dict: Acciones post-consulta a ejecutar
    """
    if consultation_completed and diagnosis_registered:
        create_reminder = False
        followup_days = None
        generate_recommendations = False
        monitoring_only = False
        record_incident = False

        if requires_followup:
            create_reminder = True
            followup_days = FOLLOWUP_DAYS_STANDARD

        if medicines_prescribed:
            generate_recommendations = True
        else:
            monitoring_only = True

    else:
        create_reminder = False
        followup_days = None
        generate_recommendations = False
        monitoring_only = False
        record_incident = True

    return {
        "create_reminder": create_reminder,
        "followup_days": followup_days,
        "generate_recommendations": generate_recommendations,
        "monitoring_only": monitoring_only,
        "record_incident": record_incident
    }


# ============================================================================
# SECCION 6: REGLA 5 - VALIDACION DE DATOS Y EDGE CASES
# ============================================================================

def validate_patient_data(
    temperature: Optional[float],
    age_years: Optional[int],
    history: Optional[list],
    phone: Optional[str]
) -> dict:
    """
    Valida los datos de entrada del paciente y detecta valores invalidos.

    Caja gris: Se cubren edge cases conocidos como temperaturas imposibles,
    edades negativas, historiales nulos y telefonos invalidos.

    Args:
        temperature (float): Temperatura corporal del paciente en Celsius
        age_years (int): Edad del paciente en anos
        history (list): Lista de registros clinicos anteriores
        phone (str): Numero de telefono del propietario

    Returns:
        dict: Resultado de validacion por campo y estado general
    """
    errors = []
    alerts = []
    allow_operation = True

    # Validar temperatura
    if temperature is None:
        errors.append("Temperatura no proporcionada")
        allow_operation = False
    elif temperature < TEMP_CRITICAL_LOW or temperature > 45:
        errors.append(f"Temperatura imposible: {temperature}C")
        allow_operation = False
    elif temperature < TEMP_MIN_NORMAL or temperature > TEMP_CRITICAL_HIGH:
        alerts.append(f"Temperatura critica: {temperature}C - requiere atencion urgente")
    elif temperature > TEMP_MAX_NORMAL:
        alerts.append(f"Temperatura elevada: {temperature}C - monitorear")

    # Validar edad
    if age_years is None:
        errors.append("Edad no proporcionada")
        allow_operation = False
    elif age_years < AGE_MIN or age_years > AGE_MAX:
        errors.append(f"Edad invalida: {age_years} anos")
        allow_operation = False

    # Validar historial
    if history is None:
        alerts.append("Historial no disponible - operacion con restricciones")
        allow_operation = False
    elif len(history) == 0:
        alerts.append("Historial vacio - primer registro del paciente")

    # Validar telefono
    if phone is None or phone.strip() == "":
        errors.append("Telefono no registrado - no se podran enviar notificaciones")
    else:
        digits = "".join(c for c in phone if c.isdigit())
        if not phone.startswith("+57") or len(digits) != 12:
            errors.append(f"Formato de telefono invalido: {phone}")

    return {
        "allow_operation": allow_operation and len(errors) == 0,
        "errors": errors,
        "alerts": alerts
    }


# ============================================================================
# SECCION 7: FUNCION PRINCIPAL - PRUEBAS
# ============================================================================

def print_result(title: str, result: dict) -> None:
    """Imprime el resultado de una prueba con formato."""
    print(f"  {title}")
    for key, value in result.items():
        print(f"    {key}: {value}")
    print()


def main() -> None:
    """
    Ejecuta casos de prueba para todas las reglas de negocio del Avance 3.
    Incluye casos normales y edge cases (caja gris).
    """
    sep = "=" * 70

    print(f"\n{sep}")
    print(f"  {CLINIC_NAME} - MOTOR DE DECISIONES | Avance 3")
    print(f"{sep}\n")

    # ----------------------------------------------------------------
    # REGLA 1: Clasificacion de consultas
    # ----------------------------------------------------------------
    print(f"  {'-'*68}")
    print("  REGLA 1: CLASIFICACION DE CONSULTAS")
    print(f"  {'-'*68}\n")

    casos_consulta = [
        ("emergencia", True),
        ("diagnostico", False),
        ("horarios", False),
        ("cita_agendada", False),
        ("seguimiento", False),
        ("otro", False),
    ]

    for query_type, urgent in casos_consulta:
        result = classify_query(query_type, urgent)
        print_result(
            f"Tipo: '{query_type}' | Urgente: {urgent}",
            result
        )

    # ----------------------------------------------------------------
    # REGLA 2: Disponibilidad de citas
    # ----------------------------------------------------------------
    print(f"  {'-'*68}")
    print("  REGLA 2: DISPONIBILIDAD DE CITAS")
    print(f"  {'-'*68}\n")

    casos_citas = [
        (True,  True,  "10:00", 2, "Todo valido"),
        (True,  True,  "13:00", 2, "Horario no disponible"),
        (True,  True,  "09:00", 5, "Veterinario invalido"),
        (False, True,  "10:00", 1, "Cliente no registrado"),
        (True,  False, "10:00", 1, "Mascota sin datos"),
    ]

    for registered, pet_ok, slot, vet, label in casos_citas:
        result = validate_appointment(registered, pet_ok, slot, vet)
        print_result(f"Caso: {label}", result)

    # ----------------------------------------------------------------
    # REGLA 3: Prioridad de atencion
    # ----------------------------------------------------------------
    print(f"  {'-'*68}")
    print("  REGLA 3: PRIORIDAD DE ATENCION")
    print(f"  {'-'*68}\n")

    casos_prioridad = [
        (True,  False, False, False, True,  "Cliente frecuente"),
        (False, True,  False, False, False, "Emergencia"),
        (False, False, False, True,  True,  "Seguimiento con historial"),
        (True,  True,  True,  False, False, "Bloqueado (sin importar urgencia)"),
        (False, False, False, False, False, "Cola general"),
    ]

    for freq, emerg, blocked, followup, history, label in casos_prioridad:
        result = evaluate_priority(freq, emerg, blocked, followup, history)
        print_result(f"Caso: {label}", result)

    # ----------------------------------------------------------------
    # REGLA 4: Seguimiento post-consulta
    # ----------------------------------------------------------------
    print(f"  {'-'*68}")
    print("  REGLA 4: SEGUIMIENTO POST-CONSULTA")
    print(f"  {'-'*68}\n")

    casos_postconsulta = [
        (True,  True,  True,  True,  "Consulta completa con medicamentos"),
        (True,  True,  True,  False, "Consulta completa sin medicamentos"),
        (True,  True,  False, False, "Sin seguimiento requerido"),
        (False, False, False, False, "Consulta incompleta"),
    ]

    for completed, diagnosed, followup, medicines, label in casos_postconsulta:
        result = handle_post_consultation(completed, diagnosed, followup, medicines)
        print_result(f"Caso: {label}", result)

    # ----------------------------------------------------------------
    # REGLA 5: Validacion de datos - Edge Cases
    # ----------------------------------------------------------------
    print(f"  {'-'*68}")
    print("  REGLA 5: VALIDACION DE DATOS (EDGE CASES)")
    print(f"  {'-'*68}\n")

    casos_validacion = [
        (38.5,  3, ["consulta_01"], "+57 320 1234567", "Datos completamente validos"),
        (500.0, 3, ["consulta_01"], "+57 320 1234567", "Temperatura imposible"),
        (-100,  3, ["consulta_01"], "+57 320 1234567", "Temperatura negativa"),
        (40.5,  3, ["consulta_01"], "+57 320 1234567", "Temperatura critica alta"),
        (38.5, -5, ["consulta_01"], "+57 320 1234567", "Edad negativa"),
        (38.5, 150, ["consulta_01"], "+57 320 1234567", "Edad imposible"),
        (38.5,  3, None,            "+57 320 1234567", "Historial nulo"),
        (38.5,  3, [],              "+57 320 1234567", "Historial vacio"),
        (38.5,  3, ["consulta_01"], None,              "Sin telefono"),
        (38.5,  3, ["consulta_01"], "3201234567",      "Telefono sin codigo pais"),
        (None,  None, None,         None,              "Todos los datos nulos"),
    ]

    for temp, age, history, phone, label in casos_validacion:
        result = validate_patient_data(temp, age, history, phone)
        print_result(f"Caso: {label}", result)

    # ----------------------------------------------------------------
    # Cierre
    # ----------------------------------------------------------------
    print(f"{sep}")
    print("  Avance 3 completado | Motor de decisiones con 5 reglas de negocio")
    print(f"{sep}\n")


if __name__ == "__main__":
    main()
