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

from datetime import datetime


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

def normalizar_nombre(texto):
    """
    Normaliza nombres y apellidos.

    Ejemplos:
        " juan"              -> "Juan"
        "juan carlos"        -> "Juan Carlos"
        "  maria   jose "    -> "Maria Jose"
        "d'angelo"           -> "D'Angelo"
    """

    if texto is None:
        return ""

    texto = texto.strip()

    # elimina espacios repetidos
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

    El año debe tener exactamente 4 dígitos.

    Ejemplos inválidos:
        "01/06/20"     -> None
        "01/06/00"     -> None
        "01/06/0020"   -> None
        "31/02/2020"   -> None
        "01/13/2020"   -> None

    Retorna:
        str  -> Fecha normalizada.
        None -> Si la fecha no puede interpretarse.
    """

    if fecha is None:
        return None

    fecha = str(fecha).strip()

    # Si el usuario no ingresó una fecha,
    # devolvemos una cadena vacía.
    if fecha == "":
        return ""

    partes = fecha.split("/")

    if len(partes) != 3:
        return None

    dia, mes, anio = partes

    # Los tres componentes deben contener solamente dígitos.
    if not (dia.isdigit() and mes.isdigit() and anio.isdigit()):
        return None

    # El año DEBE tener exactamente 4 dígitos.
    # Esto evita convertir, por ejemplo:
    # 01/06/20 -> 01/06/0020
    if len(anio) != 4:
        return None

    dia = int(dia)
    mes = int(mes)
    anio = int(anio)

    # Validamos que la fecha exista realmente.
    try:
        fecha_valida = datetime(anio, mes, dia)
    except ValueError:
        return None

    return fecha_valida.strftime("%d/%m/%Y")


# ---------------------------------------------------------------------------

# ============================================================================
# NORMALIZACIÓN DE CUIL
# ============================================================================

def normalizar_cuil(cuil):
    """
    Normaliza un CUIL al formato XX-XXXXXXXX-X.

    Ejemplos:
        "20123456783"   -> "20-12345678-3"
        "20-12345678-3" -> "20-12345678-3"
        "20 12345678 3" -> "20-12345678-3"

    Retorna:
        str  -> CUIL normalizado.
        None -> Si no puede interpretarse.
    """

    if cuil is None:
        return None

    cuil = cuil.strip()

    # Campo opcional vacío
    if cuil == "":
        return ""

    # Eliminar espacios y guiones
    cuil = cuil.replace("-", "").replace(" ", "")

    # Deben quedar exactamente 11 dígitos
    if not cuil.isdigit() or len(cuil) != 11:
        return None

    return f"{cuil[:2]}-{cuil[2:10]}-{cuil[10]}"


# ---------------------------------------------------------------------------

# ======================== GENERAR CUIL AUTOMATICO ===========================

def generar_cuil(dni, prefijo="20"):
    """
    Genera un CUIL válido a partir de un DNI.

    Parámetros:
        dni  : str o int
        sexo : "M" (Masculino) o "F" (Femenino)

    Retorna:
        str -> CUIL válido con formato XX-XXXXXXXX-X
        None -> Si el DNI es inválido
    """

    dni = str(dni).replace(".", "").strip()

    if not dni.isdigit():
        return None

    if len(dni) not in (7, 8):
        return None

    # Completa con cero si tiene 7 dígitos
    dni = dni.zfill(8)

    # prefijo = "20" if sexo.upper() == "M" else "27"

    base = prefijo + dni

    coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    suma = sum(int(d) * c for d, c in zip(base, coeficientes))

    resto = suma % 11
    verificador = 11 - resto

    if verificador == 11:
        verificador = 0

    elif verificador == 10:

        # Regla especial
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


# ---------------------------------------------------------------------------

# ========================= NORMALIZACIÓN DE TELÉFONO =========================

def normalizar_telefono(telefono):
    """
    Normaliza un teléfono al formato 0336-1234567.

    Acepta:
        03361234567
        0336-1234567
        0336 1234567

    Retorna:
        str -> Teléfono normalizado.
        None -> Si no puede interpretarse.
    """

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


# ---------------------------------------------------------------------------

def generar_periodo():
    pass


def calcular_dias_trabajados():
    pass


# ======================== DAR FORMATO AL DNI PARA MOSTRAR ====================

def formatear_dni(dni):
    """
    Formatea un DNI para mostrar.

    Ejemplos:
        12345678 -> 12.345.678
        6543210  -> 6.543.210
    """

    if dni is None:
        return ""

    dni = str(dni).strip()

    if not dni.isdigit():
        return dni

    return f"{int(dni):,}".replace(",", ".")


# ------------------------------------------------------------------------------

# ==========================================================
# FORMATEO DE CUIL
# ==========================================================

def formatear_cuil(cuil):
    """
    Formatea un CUIL para mostrar.

    Ejemplos:
        20123456783  -> 20-12345678-3
        20-12345678-3 -> 20-12345678-3
    """

    if cuil is None:
        return ""

    cuil = str(cuil).strip()

    if cuil == "":
        return ""

    # Eliminar cualquier separador existente
    cuil = cuil.replace("-", "").replace(" ", "")

    # Si no son 11 dígitos, devolver el valor original
    if not cuil.isdigit() or len(cuil) != 11:
        return cuil

    return f"{cuil[:2]}-{cuil[2:10]}-{cuil[10]}"


# -----------------------------------------------------------------------------

# ===================== FORMATEO DE TELEFONO ================================

def formatear_telefono(telefono):
    """
    Devuelve el teléfono listo para mostrar.

    Si está vacío o es None devuelve una cadena vacía.
    """

    if telefono is None:
        return ""

    telefono = str(telefono).strip()

    if telefono == "":
        return ""

    return telefono


# -----------------------------------------------------------------------------

# ======================== FORMATEO DE FECHAS ================================

def formatear_fecha(fecha):
    """
    Devuelve una fecha lista para mostrar.
    """

    if fecha is None:
        return ""

    fecha = str(fecha).strip()

    if fecha == "":
        return ""

    return fecha


# -----------------------------------------------------------------------------