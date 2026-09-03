"""
=========================================================
Sistema de Gestión Educativa (SGE)

Archivo: validaciones.py

Descripción:
Contiene todas las validaciones del sistema.

Autor: Miguel Ángel Manente
=========================================================
"""

# ==========================================================
# IMPORTACIONES
# ==========================================================
from database import conectar
from datetime import datetime
import re
# ==========================================================
# VALIDACIONES DE DOCENTES
# ==========================================================

# ========================  Validar Apellidos y Nombres ==========================
def validar_nombre(texto):
    """
    Permite:
        Letras
        Espacios
        Tildes
        Ñ
        Apóstrofo
        Guión
    """

    if texto is None:
        return False

    texto = texto.strip()

    patron = r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü' -]+$"

    return re.fullmatch(patron, texto) is not None
# --------------------------------------------------------------------------------

# ------------------- Chequea si el DNI es válido ----------------------------
def validar_dni(dni, id_docente=None):
    """
    Valida un DNI argentino.

    Retorna:
        True  -> Si el DNI es válido.
        False -> Si es inválido.
    """

    if dni is None:
        return False

    dni = dni.replace(".", "").replace("-", "").replace(" ", "")

    if not dni.isdigit():
        return False

    if len(dni) > 8:
        return False

    return True

# ------------- Chequea si el DNI ya existe en la base de datos -------------

def dni_existente(dni, id_docente=None):

    conn = conectar()
    cursor = conn.cursor()

    if id_docente is None:
        cursor.execute("""
            SELECT COUNT(*)
            FROM profesores
            WHERE dni = ?
        """, (dni,))
    else:
        cursor.execute("""
            SELECT COUNT(*)
            FROM profesores
            WHERE dni = ?
            AND id_docente <> ?
        """, (dni, id_docente))

    existe = cursor.fetchone()[0] > 0

    conn.close()

    return existe

# ----------------------------------------------------------------------------

# ========================= VALIDAR CUIL ===================================
def validar_cuil(cuil):
    """
    Valida un CUIL argentino.

    Retorna:
        True  -> Si el CUIL es válido.
        False -> Si es inválido.
    """

    if cuil is None:
        return False

    cuil = cuil.replace("-", "").replace(" ", "")

    if not cuil.isdigit():
        return False

    if len(cuil) != 11:
        return False

    # Coeficientes oficiales
    coeficientes = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

    suma = 0

    for i in range(10):
        suma += int(cuil[i]) * coeficientes[i]

    resto = suma % 11
    verificador = 11 - resto

    if verificador == 11:
        verificador = 0
    elif verificador == 10:
        verificador = 9

    return verificador == int(cuil[10])

# --------------------------------------------------------------------------
def cuil_existente():
    pass

def validar_email():
    pass


# ==========================================================
# VALIDACIONES DE ASIGNACIONES
# ==========================================================

def existe_asignacion(id_docente, id_materia, dia, cargo,
                      modulos, curso, turno,
                      hentrada, hsalida):
    """
    Verifica si ya existe una asignación idéntica.

    Parámetros:
        id_docente : ID del docente.
        id_materia : ID de la materia (None para cargos).
        dia        : Día de la asignación.
        cargo      : Cargo docente.
        modulos    : Cantidad de módulos.
        curso      : Curso.
        turno      : Turno.
        hentrada   : Hora de entrada.
        hsalida    : Hora de salida.

    Retorna:
        True  -> la asignación ya existe.
        False -> la asignación no existe.
    """

    conn = conectar()
    cursor = conn.cursor()

    # ---------------------------------------------------------
    # ASIGNACIÓN CON MATERIA
    # ---------------------------------------------------------
    if id_materia is not None:

        cursor.execute("""
            SELECT COUNT(*)
            FROM asignacion
            WHERE id_docente = ?
              AND id_materia = ?
              AND dia = ?
              AND cargo = ?
              AND modulos = ?
              AND curso = ?
              AND turno = ?
              AND hentrada = ?
              AND hsalida = ?
        """, (
            id_docente,
            id_materia,
            dia,
            cargo,
            modulos,
            curso,
            turno,
            hentrada,
            hsalida
        ))

    # ---------------------------------------------------------
    # CARGO INSTITUCIONAL
    # ---------------------------------------------------------
    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM asignacion
            WHERE id_docente = ?
              AND cargo = ?
              AND dia = ?
              AND modulos = ?
              AND turno = ?
              AND hentrada = ?
              AND hsalida = ?
        """, (
            id_docente,
            cargo,
            dia,
            modulos,
            turno,
            hentrada,
            hsalida
        ))

    existe = cursor.fetchone()[0] > 0

    conn.close()

    return existe

# ==========================================================
# VALIDACIONES DE MATERIAS
# ==========================================================
def materia_existente():
    pass

# ==========================================================
# VALIDACIONES DE CURSOS
# ==========================================================


# ==========================================================
# VALIDACIONES DE HORARIOS
# ==========================================================

def validar_horario(hentrada, hsalida):
    """
    Verifica que la hora de entrada sea menor que la hora de salida.

    Parámetros:
        hentrada (str): Hora de entrada en formato HH:MM.
        hsalida (str): Hora de salida en formato HH:MM.

    Retorna:
        bool: True si el horario es válido, False en caso contrario.
    """

    return hentrada < hsalida
#------------------------------------------------------------------ 

# ======================== Incompatibilidad horaria ========================
def hay_incompatibilidad_horaria(
        id_docente,
        dia,
        hentrada,
        hsalida,
        id_asignacion=None):

    conn = conectar()
    cursor = conn.cursor()

    # -------------------------------------------------------------
    # ALTA DE ASIGNACIÓN
    # -------------------------------------------------------------
    if id_asignacion is None:

        cursor.execute("""
            SELECT COUNT(*)
            FROM asignacion
            WHERE id_docente = ?
            AND dia = ?
            AND ? < hsalida
            AND ? > hentrada
        """, (
            id_docente,
            dia,
            hentrada,
            hsalida
        ))

    # -------------------------------------------------------------
    # MODIFICACIÓN DE ASIGNACIÓN
    # -------------------------------------------------------------
    else:

        cursor.execute("""
            SELECT COUNT(*)
            FROM asignacion
            WHERE id_docente = ?
            AND dia = ?
            AND ? < hsalida
            AND ? > hentrada
            AND id_asignacion <> ?
        """, (
            id_docente,
            dia,
            hentrada,
            hsalida,
            id_asignacion
        ))

    existe = cursor.fetchone()[0] > 0

    conn.close()

    return existe

# -------------------------------------------------------------------------

# ==========================================================
# VALIDACIONES DE FECHAS
# ==========================================================

def validar_fecha(fecha):
    """
    Verifica que una fecha exista y tenga formato DD/MM/AAAA.

    Parámetros:
        fecha (str): Fecha en formato DD/MM/AAAA.

    Retorna:
        bool: True si la fecha es válida, False en caso contrario.
    """

    try:
        datetime.strptime(fecha, "%d/%m/%Y")
        return True

    except ValueError:
        return False
# -------------------------------------------------------------------------------

# ========================= VALIDAR RANGO DE FECHAS =============================

def validar_rango_fechas(fecha_inicio, fecha_fin):
    """
    Verifica que la fecha de fin sea igual o posterior
    a la fecha de inicio.

    Si la fecha de fin está vacía, se considera válida.
    """

    if not fecha_fin:
        return True

    inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
    fin = datetime.strptime(fecha_fin, "%d/%m/%Y")

    return fin >= inicio
# -------------------------------------------------------------------------------

# ===============================================================================
#                       VALIDAR FECHA DE NACIMIENTO
# ===============================================================================
def validar_fecha_nacimiento(fecha, edad_minima=18, edad_maxima=100):
    """
    Verifica que una fecha de nacimiento sea razonable
    para una persona docente.

    Reglas:
        - La fecha debe tener formato DD/MM/AAAA.
        - La fecha debe existir.
        - No puede ser una fecha futura.
        - La edad debe ser como mínimo 18 años.
        - La edad no puede superar 100 años.

    Parámetros:
        fecha (str):
            Fecha en formato DD/MM/AAAA.

        edad_minima (int):
            Edad mínima permitida.

        edad_maxima (int):
            Edad máxima permitida.

    Retorna:
        True  -> La fecha es válida.
        False -> La fecha no es válida.
    """

    if not validar_fecha(fecha):
        return False

    fecha_nacimiento = datetime.strptime(
        fecha,
        "%d/%m/%Y"
    )

    hoy = datetime.now()

    # ------------------------------------------------------
    # No puede ser una fecha futura
    # ------------------------------------------------------

    if fecha_nacimiento > hoy:
        return False

    # ------------------------------------------------------
    # Calcular edad
    # ------------------------------------------------------

    edad = hoy.year - fecha_nacimiento.year

    # Si todavía no cumplió años este año
    if (
        (hoy.month, hoy.day)
        < (fecha_nacimiento.month, fecha_nacimiento.day)
    ):
        edad -= 1

    # ------------------------------------------------------
    # Verificar edad mínima
    # ------------------------------------------------------

    if edad < edad_minima:
        return False

    # ------------------------------------------------------
    # Verificar edad máxima
    # ------------------------------------------------------

    if edad > edad_maxima:
        return False

    return True
# -----------------------------------------------------------------------------------
