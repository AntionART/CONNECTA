"""
CONNECTA - Orquestador Principal Refactorizado
Avance 7: Subalgoritmos y Refactorizacion Funcional

Proyecto: Diseno Funcional - FESC
Autores: Erick Ocampo, Daniel Arteaga, Andres Rodriguez
Fecha: Abril 2026
Sesion: 10/04/2026

Actividad 3: Refactoring Integral
- main.py es 90%+ llamadas a funciones
- Funcion run() orquesta todo el flujo
- Logica dispersa encapsulada en funciones modulo
- Sin variables globales: datos inicializados en funciones
- Importa funciones de avance7/functions.py
"""

import sys
import os

# Permite importar functions.py desde el mismo directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functions import (
    # ACTIVIDAD 1: Subalgorithms
    crear_configuracion_clinica,
    validar_entrada_paciente,
    validar_telefono,
    procesar_servicios_con_iva,
    procesar_citas_del_dia,
    calcular_resumen_financiero,
    transformar_paciente_a_linea,
    transformar_servicio_a_linea,
    buscar_paciente_por_id,
    generar_estadisticas_servicios,
    # ACTIVIDAD 2: Lambda Functions
    filtrar_caninos,
    filtrar_felinos,
    filtrar_saludables,
    filtrar_citas_confirmadas,
    filtrar_citas_pendientes,
    obtener_nombres_pacientes,
    calcular_precios_con_iva,
    extraer_precios_servicios,
    ordenar_servicios_por_precio_asc,
    ordenar_servicios_por_precio_desc,
    ordenar_citas_por_hora,
    ordenar_pacientes_por_edad,
    ordenar_pacientes_por_peso,
)

from typing import List, Dict


# ============================================================================
# DATOS DEL SISTEMA - Inicializados como constantes de modulo (no globales)
# ============================================================================

PACIENTES: List[Dict] = [
    {"id": "P001", "name": "Max",      "species": "Canino", "breed": "Labrador Retriever",
     "owner": "Juan Perez Garcia",     "age_years": 5, "weight_kg": 32.5, "health_status": "Saludable"},
    {"id": "P002", "name": "Luna",     "species": "Felino", "breed": "Siames",
     "owner": "Maria Lopez Gonzalez",  "age_years": 3, "weight_kg": 3.8,  "health_status": "Saludable"},
    {"id": "P003", "name": "Rocky",    "species": "Canino", "breed": "Pastor Aleman",
     "owner": "Carlos Rodriguez",      "age_years": 7, "weight_kg": 35.0, "health_status": "Con seguimiento"},
    {"id": "P004", "name": "Whiskers", "species": "Felino", "breed": "Persa",
     "owner": "Ana Martinez",          "age_years": 2, "weight_kg": 4.2,  "health_status": "Saludable"},
    {"id": "P005", "name": "Buddy",    "species": "Canino", "breed": "Beagle",
     "owner": "Roberto Sanchez",       "age_years": 4, "weight_kg": 12.0, "health_status": "Saludable"},
]

SERVICIOS: List[Dict] = [
    {"id": "S001", "name": "Consulta General",   "price": 50000.0, "duration_minutes": 30, "category": "Consulta"},
    {"id": "S002", "name": "Vacunacion",          "price": 35000.0, "duration_minutes": 20, "category": "Preventiva"},
    {"id": "S003", "name": "Cirugia General",     "price": 150000.0,"duration_minutes": 90, "category": "Quirurgica"},
    {"id": "S004", "name": "Laboratorio Clinico", "price": 25000.0, "duration_minutes": 15, "category": "Diagnostico"},
    {"id": "S005", "name": "Limpieza Dental",     "price": 80000.0, "duration_minutes": 45, "category": "Preventiva"},
    {"id": "S006", "name": "Ecografia",           "price": 60000.0, "duration_minutes": 30, "category": "Diagnostico"},
]

CITAS: List[Dict] = [
    {"id": "A001", "patient_id": "P001", "patient_name": "Max",      "date": "2026-02-21",
     "time": "09:00", "service_name": "Consulta General",   "veterinarian": "Dr. Lopez",    "status": "Confirmada"},
    {"id": "A002", "patient_id": "P002", "patient_name": "Luna",     "date": "2026-02-21",
     "time": "10:00", "service_name": "Vacunacion",          "veterinarian": "Dra. Rodriguez","status": "Confirmada"},
    {"id": "A003", "patient_id": "P003", "patient_name": "Rocky",    "date": "2026-02-21",
     "time": "14:00", "service_name": "Laboratorio Clinico", "veterinarian": "Dr. Martinez", "status": "Pendiente confirmacion"},
]

VETERINARIOS: List[Dict] = [
    {"id": "V001", "name": "Dr. Luis Lopez",       "specialization": "Medicina General"},
    {"id": "V002", "name": "Dra. Carmen Rodriguez", "specialization": "Cirugia Veterinaria"},
    {"id": "V003", "name": "Dr. Jorge Martinez",    "specialization": "Diagnostico por Imagen"},
]

CONSULTAS_FRECUENTES: List[str] = [
    "Cual es el horario de atencion de la clinica?",
    "Cuanto cuesta una consulta general?",
    "Como agendar una cita en CONNECTA?",
    "Mi mascota esta enferma, que hago?",
    "Cuales son los requisitos para agendar cirugia?",
    "Ofrecen servicio de urgencias 24/7?",
    "Cuales son los metodos de pago aceptados?",
    "Necesito vacunas previas antes de una cirugia?",
]


# ============================================================================
# ACTIVIDAD 3: REFACTORING INTEGRAL - FUNCIONES DE PRESENTACION
# ============================================================================


# [GUIA 7 - ACTIVIDAD 3] - Cabecera del sistema
def imprimir_cabecera(config: Dict, sep: str) -> None:
    """
    Imprime la cabecera de inicializacion del sistema.

    Params:
        config (Dict): Configuracion de la clinica
        sep (str): Separador de seccion
    """
    print(f"\n{sep}")
    print(f"  {config['sistema']} v{config['version']} - INICIALIZANDO")
    print(f"{sep}")
    print(f"  Clinica:            {config['nombre']}")
    print(f"  WhatsApp:           {config['whatsapp']}")
    print(f"  Horario:            {config['hora_apertura']} - {config['hora_cierre']}")
    print(f"  Max citas/dia:      {config['max_citas_dia']}")
    print(f"  Tarifa base:        ${config['tarifa_base']:,.0f}")
    print(f"  IVA:                {config['iva'] * 100:.0f}%")


# [GUIA 7 - ACTIVIDAD 3] - Seccion de Actividad 1 (Modularizacion)
def imprimir_seccion_modularizacion(
    pacientes: List[Dict],
    servicios: List[Dict],
    citas: List[Dict],
    sep: str,
) -> None:
    """
    Demuestra todas las funciones def de la Actividad 1: validacion,
    procesamiento y transformacion usando subalgorithms.

    Params:
        pacientes (List[Dict]): Lista de pacientes
        servicios (List[Dict]): Catalogo de servicios
        citas (List[Dict]): Citas agendadas
        sep (str): Separador de seccion
    """
    print(f"\n{sep}")
    print("  ACTIVIDAD 1: MODULARIZACION - SUBALGORITHMS")
    print(f"{sep}")

    # --- Validacion de entrada ---
    print(f"\n  [validar_entrada_paciente] - Validacion de datos:")
    for p in pacientes:
        resultado = validar_entrada_paciente(p)
        estado = "OK" if resultado["valido"] else f"ERRORES: {resultado['errores']}"
        print(f"    {p['name']:<10} -> {estado}")

    # --- Validacion de telefono ---
    print(f"\n  [validar_telefono] - Validacion de telefonos:")
    telefonos_prueba = ["+57 320 1234567", "320 1234567", "+57 301 9876543", None]
    for tel in telefonos_prueba:
        estado = "VALIDO" if validar_telefono(tel) else "INVALIDO"
        print(f"    {str(tel):<22} -> {estado}")

    # --- Transformacion: pacientes a lineas ---
    print(f"\n  [transformar_paciente_a_linea] - Pacientes ({len(pacientes)}):")
    for p in pacientes:
        print(transformar_paciente_a_linea(p))

    # --- Procesamiento: servicios con IVA ---
    print(f"\n  [procesar_servicios_con_iva] - Servicios con IVA 19% ({len(servicios)}):")
    servicios_con_iva = procesar_servicios_con_iva(servicios)
    for s in servicios_con_iva:
        print(transformar_servicio_a_linea(s))

    # --- Procesamiento: citas del dia ---
    fecha_demo = "2026-02-21"
    citas_dia = procesar_citas_del_dia(citas, fecha_demo)
    print(f"\n  [procesar_citas_del_dia] - Citas para {fecha_demo} ({len(citas_dia)}):")
    citas_ordenadas = ordenar_citas_por_hora(citas_dia)
    for c in citas_ordenadas:
        print(f"    [{c['id']}] {c['patient_name']:<10} {c['time']}  |  {c['service_name']:<22} -> {c['status']}")

    # --- Busqueda por ID ---
    print(f"\n  [buscar_paciente_por_id] - Busquedas:")
    for pid in ["P002", "P999"]:
        resultado = buscar_paciente_por_id(pacientes, pid)
        if resultado:
            print(f"    ID '{pid}' -> Encontrado: {resultado['name']} ({resultado['species']})")
        else:
            print(f"    ID '{pid}' -> No encontrado")

    # --- Resumen financiero ---
    resumen = calcular_resumen_financiero(servicios, num_citas=10)
    print(f"\n  [calcular_resumen_financiero] - Proyeccion 10 citas:")
    print(f"    Precio promedio:   ${resumen['precio_promedio']:,.0f}")
    print(f"    Ingreso estimado:  ${resumen['ingreso_estimado']:,.0f}")
    print(f"    Ingreso c/IVA:     ${resumen['ingreso_con_iva']:,.0f}")

    # --- Estadisticas de servicios ---
    stats = generar_estadisticas_servicios(servicios)
    print(f"\n  [generar_estadisticas_servicios] - Catalogo:")
    print(f"    Total servicios:  {stats['total']}")
    print(f"    Precio minimo:    ${stats['precio_min']:,.0f}")
    print(f"    Precio maximo:    ${stats['precio_max']:,.0f}")
    print(f"    Precio promedio:  ${stats['precio_promedio']:,.0f}")


# [GUIA 7 - ACTIVIDAD 3] - Seccion de Actividad 2 (Lambdas)
def imprimir_seccion_lambdas(
    pacientes: List[Dict],
    servicios: List[Dict],
    citas: List[Dict],
    sep: str,
) -> None:
    """
    Demuestra todas las lambda functions de la Actividad 2:
    filter, map y sorted con funciones anonimas.

    Params:
        pacientes (List[Dict]): Lista de pacientes
        servicios (List[Dict]): Catalogo de servicios
        citas (List[Dict]): Citas agendadas
        sep (str): Separador de seccion
    """
    print(f"\n{sep}")
    print("  ACTIVIDAD 2: LAMBDA FUNCTIONS - PARADIGMA FUNCIONAL")
    print(f"{sep}")

    # --- filter() con lambda ---
    print(f"\n  filter(lambda ...) - Filtros por condicion:")

    caninos = filtrar_caninos(pacientes)
    print(f"    filtrar_caninos    -> {obtener_nombres_pacientes(caninos)}")

    felinos = filtrar_felinos(pacientes)
    print(f"    filtrar_felinos    -> {obtener_nombres_pacientes(felinos)}")

    saludables = filtrar_saludables(pacientes)
    print(f"    filtrar_saludables -> {obtener_nombres_pacientes(saludables)}")

    confirmadas = filtrar_citas_confirmadas(citas)
    print(f"    filtrar_citas_confirmadas -> {len(confirmadas)} de {len(citas)} citas")

    pendientes = filtrar_citas_pendientes(citas)
    print(f"    filtrar_citas_pendientes  -> {[c['patient_name'] for c in pendientes]}")

    # --- map() con lambda ---
    print(f"\n  map(lambda ...) - Transformaciones uniformes:")

    nombres = obtener_nombres_pacientes(pacientes)
    print(f"    obtener_nombres_pacientes  -> {nombres}")

    precios_base = extraer_precios_servicios(servicios)
    precios_iva = calcular_precios_con_iva(precios_base)
    print(f"    extraer_precios_servicios  -> {[f'${p:,.0f}' for p in precios_base]}")
    print(f"    calcular_precios_con_iva   -> {[f'${p:,.0f}' for p in precios_iva]}")

    # --- sorted() con lambda ---
    print(f"\n  sorted(..., key=lambda ...) - Ordenamientos dinamicos:")

    por_precio_asc = ordenar_servicios_por_precio_asc(servicios)
    print(f"    precio ascendente  -> {[s['name'] for s in por_precio_asc]}")

    por_precio_desc = ordenar_servicios_por_precio_desc(servicios)
    print(f"    precio descendente -> {[s['name'] for s in por_precio_desc]}")

    por_edad = ordenar_pacientes_por_edad(pacientes)
    print(f"    pacientes por edad -> {[(p['name'], p['age_years']) for p in por_edad]}")

    por_peso = ordenar_pacientes_por_peso(pacientes)
    print(f"    pacientes por peso -> {[(p['name'], p['weight_kg']) for p in por_peso]}")

    citas_hora = ordenar_citas_por_hora(citas)
    print(f"    citas por hora     -> {[(c['patient_name'], c['time']) for c in citas_hora]}")


# [GUIA 7 - ACTIVIDAD 3] - Seccion de informacion de colecciones
def imprimir_seccion_colecciones(
    pacientes: List[Dict],
    servicios: List[Dict],
    citas: List[Dict],
    veterinarios: List[Dict],
    consultas: List[str],
    sep: str,
) -> None:
    """
    Imprime el resumen de todas las colecciones del sistema.

    Params:
        pacientes, servicios, citas, veterinarios (List[Dict]): Colecciones CONNECTA
        consultas (List[str]): FAQ del sistema
        sep (str): Separador de seccion
    """
    print(f"\n{sep}")
    print("  RESUMEN DE COLECCIONES DEL SISTEMA")
    print(f"{sep}")

    print(f"\n  VETERINARIOS ({len(veterinarios)}):")
    for v in veterinarios:
        print(f"    [{v['id']}] {v['name']:<28} {v['specialization']}")

    print(f"\n  PREGUNTAS FRECUENTES ({len(consultas)}):")
    for i, q in enumerate(consultas, 1):
        print(f"    {i:>2}. {q}")


# ============================================================================
# ACTIVIDAD 3: FUNCION PRINCIPAL ORQUESTADORA
# ============================================================================


# [GUIA 7 - ACTIVIDAD 3] - Orquestador principal (run)
def run() -> None:
    """
    Funcion principal que orquesta todo el flujo de demostracion de Avance 7.
    Principio de refactoring: main es 90% llamadas a funciones, sin logica dispersa.

    Flujo:
        1. Carga configuracion via funcion (sin globales)
        2. Llama funciones de Actividad 1 (Modularizacion)
        3. Llama funciones de Actividad 2 (Lambdas)
        4. Imprime resumen de colecciones
        5. Cierra con pie de pagina
    """
    # [GUIA 7 - ACTIVIDAD 3] - Toda la logica encapsulada en funciones
    config = crear_configuracion_clinica()
    sep = "=" * 70

    imprimir_cabecera(config, sep)

    imprimir_seccion_modularizacion(PACIENTES, SERVICIOS, CITAS, sep)

    imprimir_seccion_lambdas(PACIENTES, SERVICIOS, CITAS, sep)

    imprimir_seccion_colecciones(
        PACIENTES, SERVICIOS, CITAS, VETERINARIOS, CONSULTAS_FRECUENTES, sep
    )

    print(f"\n{sep}")
    print("  Avance 7 completado | Subalgorithms + Lambda Functions | PEP 8")
    print(f"  Funciones def: 10  |  Lambda functions: 13  |  Orchestrator: run()")
    print(f"{sep}\n")


if __name__ == "__main__":
    run()
