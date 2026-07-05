"""
=========================================================
Sistema de Gestión Educativa (SGE)

Archivo: utilidades.py

Descripción:
Contiene funciones auxiliares reutilizables.

Autor: Miguel Ángel Manente
=========================================================
"""

# ==========================================================
# IMPORTACIONES
# ==========================================================


# ==========================================================
# HORARIOS
# ==========================================================

def normalizar_hora(hora):
    """
    Normaliza una hora al formato HH:MM.

    Ejemplos:
        "8:00"   -> "08:00"
        " 7:30 " -> "07:30"
        "08:00"  -> "08:00"

    Retorna:
        str  -> Hora normalizada.
        None -> Si la hora no puede interpretarse.
    """

    if hora is None:
        return None

    hora = hora.strip()

    partes = hora.split(":")

    if len(partes) != 2:
        return None

    horas, minutos = partes

    if not horas.isdigit() or not minutos.isdigit():
        return None

    horas = int(horas)
    minutos = int(minutos)

    return f"{horas:02d}:{minutos:02d}"


def hora_a_minutos():
    pass

def minutos_a_hora():
    pass


# ==========================================================
# TEXTO
# ==========================================================

def normalizar_nombre():
    pass

def normalizar_apellido():
    pass


# ==========================================================
# FECHAS
# ==========================================================
def normalizar_fecha(fecha):
    """
    Normaliza una fecha al formato DD/MM/AAAA.

    Ejemplos:
        "5/7/2026"    -> "05/07/2026"
        "05/7/2026"   -> "05/07/2026"
        " 5/07/2026 " -> "05/07/2026"

    Retorna:
        str  -> Fecha normalizada.
        None -> Si la fecha no puede interpretarse.
    """

    if fecha is None:
        return None

    fecha = fecha.strip()

    # Si el usuario no ingresó una fecha,
    # devolvemos una cadena vacía.
    if fecha == "":
        return ""

    partes = fecha.split("/")

    if len(partes) != 3:
        return None

    dia, mes, anio = partes

    if not (dia.isdigit() and mes.isdigit() and anio.isdigit()):
        return None

    dia = int(dia)
    mes = int(mes)
    anio = int(anio)

    return f"{dia:02d}/{mes:02d}/{anio:04d}"
# ---------------------------------------------------------------------------

def generar_periodo():
    pass

def calcular_dias_trabajados():
    pass