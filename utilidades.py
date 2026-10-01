

"""
=========================================================
Sistema de Gestión Educativa (SGE)

Archivo: utilidades.py

Descripción:
Contiene funciones auxiliares reutilizables.

Autor: Miguel Ángel Manente
=========================================================
"""

from datetime import datetime
from pathlib import Path
import os
import sys


# =========================================================
# RUTAS DEL SISTEMA
# =========================================================

def obtener_carpeta_reportes():
    """
    Devuelve la carpeta principal donde SGE almacena los reportes.

    Durante el desarrollo:
        Sistema Académico\\reportes

    Cuando SGE está compilado/instalado:
        C:\\ProgramData\\SGE\\reportes

    La carpeta se crea automáticamente si no existe.

    Returns:
        str: Ruta completa de la carpeta de reportes.
    """

    # -----------------------------------------------------
    # EJECUCIÓN COMO PROGRAMA COMPILADO
    # -----------------------------------------------------
    if getattr(sys, "frozen", False):

        program_data = os.environ.get("PROGRAMDATA")

        if not program_data:
            program_data = r"C:\ProgramData"

        carpeta_reportes = (
            Path(program_data)
            / "SGE"
            / "reportes"
        )

    # -----------------------------------------------------
    # EJECUCIÓN DURANTE EL DESARROLLO
    # -----------------------------------------------------
    else:

        carpeta_reportes = (
            Path(__file__).resolve().parent
            / "reportes"
        )

    # Crear la carpeta si no existe
    carpeta_reportes.mkdir(
        parents=True,
        exist_ok=True
    )

    return str(carpeta_reportes)


# =========================================================
# HORARIOS
# =========================================================

def normalizar_hora(hora):
    """
    Normaliza una hora al formato HH:MM.

    Examples:
        "8:00" -> "08:00"
        " 7:30 " -> "07:30"
        "08:00" -> "08:00"

    Returns str or None.
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


# =========================================================
# TEXTO
# =========================================================

def normalizar_nombre(texto):
    """
    Normaliza nombres y apellidos.

    Examples:
        " juan" -> "Juan"
        "juan carlos" -> "Juan Carlos"
        "  maria   jose " -> "Maria Jose"
        "d'angelo" -> "D'Angelo"
    """
    if texto is None:
        return ""

    texto = texto.strip()
    texto = " ".join(texto.split())

    palabras = []

    for palabra in texto.split():
        if "'" in palabra:
            partes = palabra.split("'")
            palabra = "'".join(p.capitalize() for p in partes)
        else:
            palabra = palabra.capitalize()

        palabras.append(palabra)

    return " ".join(palabras)


def normalizar_apellido():
    pass


# =========================================================
# FECHAS
# =========================================================

def normalizar_fecha(fecha):
    """
    Normaliza una fecha al formato DD/MM/AAAA.

    Examples:
        "5/7/2026" -> "05/07/2026"
        "05/7/2026" -> "05/07/2026"
        " 5/07/2026 " -> "05/07/2026"

    Reglas:
        - El año debe tener exactamente 4 dígitos.
        - El año debe estar entre 1900 y el año actual.
        - No se permiten fechas futuras.
        - La fecha debe existir realmente en el calendario.

    Invalid:
        "01/06/20"
        "01/06/00"
        "01/06/0020"
        "21/10/0060"
        "31/02/2020"
        "01/13/2020"
        "21/10/2030"
    """

    if fecha is None:
        return None

    fecha = str(fecha).strip()

    if fecha == "":
        return ""

    partes = fecha.split("/")

    if len(partes) != 3:
        return None

    dia, mes, anio = partes

    # Todos los componentes deben ser numéricos
    if not (dia.isdigit() and mes.isdigit() and anio.isdigit()):
        return None

    # El año debe tener exactamente 4 dígitos
    if len(anio) != 4:
        return None

    dia = int(dia)
    mes = int(mes)
    anio = int(anio)

    # Año mínimo permitido para nacimiento
    if anio < 1900:
        return None

    # Año máximo: año actual
    anio_actual = datetime.now().year

    if anio > anio_actual:
        return None

    # Verificar que la fecha exista realmente
    try:
        fecha_valida = datetime(anio, mes, dia)
    except ValueError:
        return None

    # No permitir una fecha futura dentro del año actual
    if fecha_valida.date() > datetime.now().date():
        return None

    return fecha_valida.strftime("%d/%m/%Y")


# =========================================================
# CUIL
# =========================================================

def normalizar_cuil(cuil):
    if cuil is None:
        return None

    cuil = cuil.strip()

    if cuil == "":
        return ""

    cuil = cuil.replace("-", "").replace(" ", "")

    if not cuil.isdigit() or len(cuil) != 11:
        return None

    return f"{cuil[:2]}-{cuil[2:10]}-{cuil[10]}"


def generar_cuil(dni, prefijo="20"):
    dni = str(dni).replace(".", "").strip()

    if not dni.isdigit():
        return None

    if len(dni) not in (7, 8):
        return None

    dni = dni.zfill(8)

    base = prefijo + dni

    coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    suma = sum(
        int(d) * c
        for d, c in zip(base, coeficientes)
    )

    resto = suma % 11
    verificador = 11 - resto

    if verificador == 11:
        verificador = 0

    elif verificador == 10:
        if prefijo == "20":
            prefijo = "23"
        elif prefijo == "27":
            prefijo = "23"

        base = prefijo + dni

        suma = sum(
            int(d) * c
            for d, c in zip(base, coeficientes)
        )

        resto = suma % 11
        verificador = 11 - resto

        if verificador == 11:
            verificador = 0

    return f"{prefijo}-{dni}-{verificador}"


# =========================================================
# TELEPHONE
# =========================================================

def normalizar_telefono(telefono):
    if telefono is None:
        return None

    telefono = telefono.strip()
    telefono = telefono.replace("-", "")
    telefono = telefono.replace(" ", "")

    if not telefono.isdigit():
        return None

    if len(telefono) != 11:
        return None

    return f"{telefono[:4]}-{telefono[4:]}"


# =========================================================
# OTRAS FUNCIONES
# =========================================================

def generar_periodo():
    pass


def calcular_dias_trabajados():
    pass


# =========================================================
# FORMATEO
# =========================================================

def formatear_dni(dni):
    if dni is None:
        return ""

    dni = str(dni).strip()

    if not dni.isdigit():
        return dni

    return f"{int(dni):,}".replace(",", ".")


def formatear_cuil(cuil):
    if cuil is None:
        return ""

    cuil = str(cuil).strip()

    if cuil == "":
        return ""

    cuil = cuil.replace("-", "").replace(" ", "")

    if not cuil.isdigit() or len(cuil) != 11:
        return cuil

    return f"{cuil[:2]}-{cuil[2:10]}-{cuil[10]}"


def formatear_telefono(telefono):
    if telefono is None:
        return ""

    telefono = str(telefono).strip()

    if telefono == "":
        return ""

    return telefono


def formatear_fecha(fecha):
    if fecha is None:
        return ""

    fecha = str(fecha).strip()

    if fecha == "":
        return ""

    return fecha

