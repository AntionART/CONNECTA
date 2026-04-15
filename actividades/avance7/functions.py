"""
CONNECTA - Modulo de Funciones Refactorizadas
Avance 7: Subalgoritmos y Refactorizacion Funcional

Proyecto: Diseno Funcional - FESC
Autores: Erick Ocampo, Daniel Arteaga, Andres Rodriguez
Fecha: Abril 2026
Sesion: 10/04/2026
Paradigma: Programacion Funcional - Modular

Contenido:
- Actividad 1: Subalgorithms (funciones def con responsabilidad unica)
- Actividad 2: Lambda Functions (paradigma funcional con filter/map/sorted)
"""

from typing import List, Dict, Optional


# ============================================================================
# ACTIVIDAD 1: MODULARIZACION DEL CORE - SUBALGORITHMS
# ============================================================================


# [GUIA 7 - ACTIVIDAD 1] - Configuracion de clinica encapsulada en funcion
def crear_configuracion_clinica() -> Dict:
    """
    Encapsula la configuracion base de la clinica eliminando variables globales.
    Principio: Single Responsibility - solo retorna datos de config.

    Returns:
        Dict: Configuracion completa de la clinica
    """
    return {
        "nombre": "VetClinic Central Bogota",
        "telefono": "+57 1 2345678",
        "whatsapp": "+57 320 1234567",
        "email": "contacto@vetclinic-connecta.com",
        "direccion": "Carrera 5 #12-34, Bogota, Colombia",
        "hora_apertura": "08:00",
        "hora_cierre": "18:00",
        "inicio_almuerzo": "12:00",
        "fin_almuerzo": "13:00",
        "max_citas_dia": 15,
        "duracion_cita_min": 30,
        "tarifa_base": 50000.0,
        "iva": 0.19,
        "descuento_lealtad": 0.10,
        "version": "1.0.0",
        "sistema": "CONNECTA",
    }


# [GUIA 7 - ACTIVIDAD 1] - Validacion de datos de paciente
def validar_entrada_paciente(paciente: Dict) -> Dict:
    """
    Valida que un diccionario de paciente contenga todos los campos requeridos
    y que los valores sean coherentes.

    Params:
        paciente (Dict): Diccionario con datos del paciente

    Returns:
        Dict: {"valido": bool, "errores": List[str]}
    """
    errores: List[str] = []
    campos_requeridos = ["id", "name", "species", "breed", "owner", "age_years", "weight_kg"]

    for campo in campos_requeridos:
        if campo not in paciente or paciente[campo] is None:
            errores.append(f"Campo requerido ausente: '{campo}'")

    if "age_years" in paciente and isinstance(paciente["age_years"], int):
        if paciente["age_years"] < 0 or paciente["age_years"] > 30:
            errores.append(f"Edad fuera de rango: {paciente['age_years']} anos")

    if "weight_kg" in paciente and isinstance(paciente["weight_kg"], (int, float)):
        if paciente["weight_kg"] <= 0 or paciente["weight_kg"] > 200:
            errores.append(f"Peso invalido: {paciente['weight_kg']} kg")

    return {"valido": len(errores) == 0, "errores": errores}


# [GUIA 7 - ACTIVIDAD 1] - Validacion de telefono colombiano
def validar_telefono(telefono: str) -> bool:
    """
    Valida si el numero de telefono cumple el formato colombiano +57 3XX XXXXXXX.

    Params:
        telefono (str): Numero a validar

    Returns:
        bool: True si el formato es valido
    """
    if not telefono or not isinstance(telefono, str):
        return False
    tiene_codigo = telefono.startswith("+57")
    solo_digitos = "".join(c for c in telefono if c.isdigit())
    longitud_correcta = len(solo_digitos) == 12
    return tiene_codigo and longitud_correcta


# [GUIA 7 - ACTIVIDAD 1] - Procesamiento de servicios: agrega precio con IVA
def procesar_servicios_con_iva(servicios: List[Dict], iva: float = 0.19) -> List[Dict]:
    """
    Agrega el campo 'precio_con_iva' a cada servicio.
    Paso por referencia: recibe la lista original sin modificarla,
    retorna una nueva lista con los datos enriquecidos.

    Params:
        servicios (List[Dict]): Lista de servicios veterinarios
        iva (float): Porcentaje de IVA a aplicar (default 0.19)

    Returns:
        List[Dict]: Nueva lista de servicios con campo 'precio_con_iva' agregado
    """
    resultado: List[Dict] = []
    for servicio in servicios:
        servicio_enriquecido = {**servicio, "precio_con_iva": round(servicio["price"] * (1 + iva), 2)}
        resultado.append(servicio_enriquecido)
    return resultado


# [GUIA 7 - ACTIVIDAD 1] - Procesamiento: filtrar citas por fecha
def procesar_citas_del_dia(citas: List[Dict], fecha: str) -> List[Dict]:
    """
    Filtra las citas agendadas para una fecha especifica.

    Params:
        citas (List[Dict]): Lista completa de citas
        fecha (str): Fecha en formato YYYY-MM-DD

    Returns:
        List[Dict]: Citas correspondientes a la fecha indicada
    """
    return [cita for cita in citas if cita.get("date") == fecha]


# [GUIA 7 - ACTIVIDAD 1] - Calculo de resumen financiero del dia
def calcular_resumen_financiero(servicios: List[Dict], num_citas: int) -> Dict:
    """
    Calcula metricas financieras estimadas para el dia de operacion.

    Params:
        servicios (List[Dict]): Catalogo de servicios disponibles
        num_citas (int): Numero de citas completadas en el dia

    Returns:
        Dict: Resumen con precio_promedio, ingreso_estimado e ingreso_con_iva
    """
    if not servicios:
        return {"precio_promedio": 0.0, "ingreso_estimado": 0.0, "ingreso_con_iva": 0.0}

    precio_promedio = sum(s["price"] for s in servicios) / len(servicios)
    ingreso_estimado = precio_promedio * num_citas
    ingreso_con_iva = round(ingreso_estimado * 1.19, 2)

    return {
        "citas_completadas": num_citas,
        "precio_promedio": round(precio_promedio, 2),
        "ingreso_estimado": round(ingreso_estimado, 2),
        "ingreso_con_iva": ingreso_con_iva,
    }


# [GUIA 7 - ACTIVIDAD 1] - Transformacion: paciente a linea de tabla
def transformar_paciente_a_linea(paciente: Dict) -> str:
    """
    Convierte un diccionario de paciente a una cadena formateada para consola.

    Params:
        paciente (Dict): Datos del paciente

    Returns:
        str: Linea formateada lista para imprimir
    """
    return (
        f"  [{paciente['id']}] {paciente['name']:<10} "
        f"{paciente['breed']:<22} | "
        f"Dueno: {paciente['owner']:<20} | "
        f"Edad: {paciente['age_years']} anos"
    )


# [GUIA 7 - ACTIVIDAD 1] - Transformacion: servicio a linea de tabla
def transformar_servicio_a_linea(servicio: Dict) -> str:
    """
    Convierte un diccionario de servicio a una cadena formateada para consola.

    Params:
        servicio (Dict): Datos del servicio veterinario

    Returns:
        str: Linea formateada lista para imprimir
    """
    precio_iva = round(servicio["price"] * 1.19, 2)
    return (
        f"  [{servicio['id']}] {servicio['name']:<20} "
        f"${servicio['price']:>8,.0f}  ->  ${precio_iva:>9,.0f} c/IVA  |  "
        f"{servicio['duration_minutes']} min"
    )


# [GUIA 7 - ACTIVIDAD 1] - Busqueda de paciente por ID (retorno explicito)
def buscar_paciente_por_id(pacientes: List[Dict], patient_id: str) -> Optional[Dict]:
    """
    Busca un paciente por su identificador unico.
    Retorno explicito: None si no se encuentra (nunca lanza excepcion).

    Params:
        pacientes (List[Dict]): Lista de pacientes registrados
        patient_id (str): ID del paciente a buscar (ej: 'P001')

    Returns:
        Optional[Dict]: Datos del paciente o None si no existe
    """
    for paciente in pacientes:
        if paciente.get("id") == patient_id:
            return paciente
    return None


# [GUIA 7 - ACTIVIDAD 1] - Generar estadisticas del catalogo de servicios
def generar_estadisticas_servicios(servicios: List[Dict]) -> Dict:
    """
    Genera estadisticas agregadas sobre el catalogo de servicios.

    Params:
        servicios (List[Dict]): Lista de servicios veterinarios

    Returns:
        Dict: Estadisticas: total, precio_min, precio_max, precio_promedio
    """
    if not servicios:
        return {"total": 0, "precio_min": 0.0, "precio_max": 0.0, "precio_promedio": 0.0}

    precios = [s["price"] for s in servicios]
    return {
        "total": len(servicios),
        "precio_min": min(precios),
        "precio_max": max(precios),
        "precio_promedio": round(sum(precios) / len(precios), 2),
    }


# ============================================================================
# ACTIVIDAD 2: LAMBDA FUNCTIONS - PARADIGMA FUNCIONAL
# ============================================================================

# [GUIA 7 - ACTIVIDAD 2] - Filtros con lambda + filter()
# Ventaja tecnica: expresion concisa de un predicado sin definir una funcion completa

filtrar_caninos = lambda pacientes: list(
    filter(lambda p: p["species"] == "Canino", pacientes)
)

filtrar_felinos = lambda pacientes: list(
    filter(lambda p: p["species"] == "Felino", pacientes)
)

filtrar_saludables = lambda pacientes: list(
    filter(lambda p: p["health_status"] == "Saludable", pacientes)
)

filtrar_citas_confirmadas = lambda citas: list(
    filter(lambda c: c["status"] == "Confirmada", citas)
)

filtrar_citas_pendientes = lambda citas: list(
    filter(lambda c: c["status"] != "Confirmada", citas)
)

# [GUIA 7 - ACTIVIDAD 2] - Transformaciones con lambda + map()
# Ventaja tecnica: aplica una transformacion uniforme a toda la coleccion sin for explicito

obtener_nombres_pacientes = lambda pacientes: list(
    map(lambda p: p["name"], pacientes)
)

calcular_precios_con_iva = lambda precios: list(
    map(lambda precio: round(precio * 1.19, 2), precios)
)

extraer_precios_servicios = lambda servicios: list(
    map(lambda s: s["price"], servicios)
)

# [GUIA 7 - ACTIVIDAD 2] - Ordenamientos con lambda + sorted()
# Ventaja tecnica: criterio de ordenamiento expresado inline sin funcion auxiliar

ordenar_servicios_por_precio_asc = lambda servicios: sorted(
    servicios, key=lambda s: s["price"]
)

ordenar_servicios_por_precio_desc = lambda servicios: sorted(
    servicios, key=lambda s: s["price"], reverse=True
)

ordenar_citas_por_hora = lambda citas: sorted(
    citas, key=lambda c: c["time"]
)

ordenar_pacientes_por_edad = lambda pacientes: sorted(
    pacientes, key=lambda p: p["age_years"]
)

ordenar_pacientes_por_peso = lambda pacientes: sorted(
    pacientes, key=lambda p: p["weight_kg"], reverse=True
)
