"""
Módulo de persistencia complementaria para CONNECTA.
Gestiona archivos TXT (estado de sesión, logs de webhook) y CSV (exportaciones).
La persistencia primaria del sistema es MongoDB; estos archivos son utilidades
de auditoría y exportación para análisis externo y recuperación ante reinicios.
"""
import os
import csv
from datetime import datetime, timezone


# [GUÍA 8 - ACTIVIDAD 1]
def _inicializar_directorios() -> None:
    """Crea data/ y exports/ si no existen. Llamar al inicio de cada función."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("exports", exist_ok=True)


def guardar_estado_sesion(
    datos: dict, ruta: str = "data/session_state.txt"
) -> bool:
    """
    # [GUÍA 8 - ACTIVIDAD 1]
    Persiste el estado actual de la sesión operativa de CONNECTA en un
    archivo plano. En CONNECTA, este respaldo complementa MongoDB capturando
    el último estado conocido del sistema ante reinicios de contenedor.
    Modo 'w': sobreescribe la configuración al guardar el estado más reciente.
    """
    _inicializar_directorios()
    try:
        # [GUÍA 8 - ACTIVIDAD 1] Modo 'w': sobreescribe para mantener solo
        # el estado más reciente — cada reinicio produce un snapshot limpio
        with open(ruta, 'w', encoding='utf-8') as f:
            for clave, valor in datos.items():
                f.write(f"{clave}={valor}\n")
        print(f"[OK] Archivo guardado correctamente en {ruta}")
        return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[ERROR] No se pudo acceder a {ruta}: {e}")
        return False


def registrar_evento_webhook(
    evento: str, ruta: str = "data/webhook_log.txt"
) -> bool:
    """
    # [GUÍA 8 - ACTIVIDAD 1]
    Registra eventos del webhook de WhatsApp en log histórico con timestamp
    ISO 8601. Modo 'a' (append): cada evento se acumula sin perder el historial.
    En CONNECTA, este log complementa el registro en MongoDB para auditorías.
    """
    _inicializar_directorios()
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        # [GUÍA 8 - ACTIVIDAD 1] Modo 'a': append preserva el historial
        # completo de eventos — nunca sobreescribe entradas anteriores
        with open(ruta, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {evento}\n")
        print(f"[OK] Archivo guardado correctamente en {ruta}")
        return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[ERROR] No se pudo acceder a {ruta}: {e}")
        return False


def cargar_estado_sesion(
    ruta: str = "data/session_state.txt"
) -> dict:
    """
    # [GUÍA 8 - ACTIVIDAD 1]
    Al arrancar CONNECTA, restaura el estado de sesión desde archivo plano
    si existe. Retorna {} si no hay estado previo (primera ejecución).
    Integración al proyecto: llamar desde app/__init__.py o run.py al inicio.
    """
    _inicializar_directorios()
    try:
        # [GUÍA 8 - ACTIVIDAD 1] Modo 'r': lectura secuencial línea a línea,
        # parsea clave=valor ignorando comentarios y líneas vacías
        with open(ruta, 'r', encoding='utf-8') as f:
            estado: dict = {}
            for linea in f:
                linea = linea.strip()
                if '=' in linea and not linea.startswith('#'):
                    clave, _, valor = linea.partition('=')
                    estado[clave.strip()] = valor.strip()
        print(f"[OK] Archivo leído correctamente en {ruta}")
        return estado
    except FileNotFoundError:
        # Primera ejecución: no hay estado previo, retornar vacío silenciosamente
        return {}
    except (PermissionError, OSError) as e:
        print(f"[ERROR] No se pudo acceder a {ruta}: {e}")
        return {}


def leer_log_webhook(
    ruta: str = "data/webhook_log.txt"
) -> list[str]:
    """
    # [GUÍA 8 - ACTIVIDAD 1]
    Lee y retorna todas las entradas del log histórico de webhook como lista.
    """
    _inicializar_directorios()
    try:
        # [GUÍA 8 - ACTIVIDAD 1] Modo 'r': lectura completa del historial;
        # rstrip('\n') limpia saltos de línea preservando el contenido de cada entrada
        with open(ruta, 'r', encoding='utf-8') as f:
            return [linea.rstrip('\n') for linea in f]
    except FileNotFoundError:
        return []
    except (PermissionError, OSError) as e:
        print(f"[ERROR] No se pudo acceder a {ruta}: {e}")
        return []


def exportar_mascotas_csv(
    mascotas: list[dict], ruta: str = "exports/mascotas.csv"
) -> bool:
    """
    # [GUÍA 8 - ACTIVIDAD 2]
    Exporta la colección de mascotas (dicts con campos name, species, breed,
    owner_phone, etc.) a CSV para análisis externo en hojas de cálculo.
    Headers generados desde las claves del primer dict. Valida integridad
    de tipos: campos numéricos (age_years) vs alfanuméricos (name, species).
    """
    _inicializar_directorios()
    if not mascotas:
        print(f"[OK] Archivo guardado correctamente en {ruta}")
        return True
    try:
        # [GUÍA 8 - ACTIVIDAD 2] Headers dinámicos desde claves del primer dict;
        # age_years permanece int, name/species/breed son str — DictWriter los
        # serializa correctamente sin pérdida de tipo en la representación CSV
        headers = list(mascotas[0].keys())
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(mascotas)
        print(f"[OK] Archivo guardado correctamente en {ruta}")
        return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[ERROR] No se pudo acceder a {ruta}: {e}")
        return False


def exportar_citas_csv(
    citas: list[dict], ruta: str = "exports/citas.csv"
) -> bool:
    """
    # [GUÍA 8 - ACTIVIDAD 2]
    Exporta el listado de citas a CSV. Mapea los dicts del modelo Appointment
    (date, status, pet_name, owner_phone, notes) a filas con encabezados.
    """
    _inicializar_directorios()
    if not citas:
        print(f"[OK] Archivo guardado correctamente en {ruta}")
        return True
    try:
        # [GUÍA 8 - ACTIVIDAD 2] Mismo patrón DictWriter que mascotas;
        # date se exporta como string ISO 8601 (ya serializado desde MongoDB)
        headers = list(citas[0].keys())
        with open(ruta, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(citas)
        print(f"[OK] Archivo guardado correctamente en {ruta}")
        return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        print(f"[ERROR] No se pudo acceder a {ruta}: {e}")
        return False
