# ============================================================
# SISTEMA DE GESTIÓN ESCOLAR (SGE)
# Motor de cálculo de inasistencias
#
# Este módulo contiene exclusivamente la lógica de negocio
# para analizar el impacto de las licencias sobre cargos
# y módulos de los docentes.
#
# No contiene código de interfaz gráfica (Tkinter).
# ============================================================

# ============================================================
# IMPORTACIONES
# ============================================================
from database import conectar
import sqlite3
from datetime import datetime, timedelta
from negocio.calendario_escolar import (es_dia_habil, es_feriado)
# -------------------------------------------------------------

# ======================= Asignaciones activas del docente
def obtener_asignaciones_docente(id_docente):
    """
    Devuelve todas las asignaciones activas de un docente.
    Incluye el nombre de la materia cuando corresponda.
    """

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.id_asignacion,
            a.id_docente,
            a.id_materia,
            m.nombre AS materia,
            a.cargo,
            a.curso,
            a.dia,
            a.modulos,
            a.turno,
            a.hentrada,
            a.hsalida,
            a.situacion_revista,
            a.activo,
            a.fecha_cese,
            a.toma_pos
        FROM asignacion a
        LEFT JOIN materias m
            ON a.id_materia = m.id_materia
        WHERE a.id_docente = ?
        AND a.activo = 1
        ORDER BY
            a.turno,
            a.dia
    """, (id_docente,))

    columnas = [col[0] for col in cursor.description]

    datos = [
        dict(zip(columnas, fila))
        for fila in cursor.fetchall()
    ]

    conn.close()

    for fila in datos:
        fila["modulos"] = int(fila["modulos"])

    return datos
# --------------------------------------------------------------------------------

# ============================================================
# Obtiene una inasistencia por su ID
# ============================================================

def obtener_inasistencia(id_inasistencia):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            id_docente,
            fecha_desde,
            fecha_hasta,
            motivo,
            observacion
        FROM inasistencia
        WHERE id = ?
    """, (id_inasistencia,))

    fila = cursor.fetchone()

    conn.close()

    if fila is None:
        return None

    columnas = [
        "id",
        "id_docente",
        "fecha_desde",
        "fecha_hasta",
        "motivo",
        "observacion"
    ]

    return dict(zip(columnas, fila))
# -------------------------------------------------------------------------------

# ========================= Averigua si es un cargo  ============================
def es_cargo(asignacion):
    return asignacion["id_materia"] is None
# -------------------------------------------------------------------------------

# ========================== Averigua si es un módulo ===========================
def es_modulo(asignacion):
    return asignacion["id_materia"] is not None
# -------------------------------------------------------------------------------

def separar_asignaciones(asignaciones):
    """
    Separa las asignaciones en cargos y módulos.
    """

    cargos = []
    modulos = []

    for asignacion in asignaciones:

        if es_cargo(asignacion):
            cargos.append(asignacion)
        else:
            modulos.append(asignacion)

    return cargos, modulos
# ============================================================
# Analiza una asignación de CARGO
# Devuelve la cantidad de días hábiles afectados
# ============================================================

def analizar_cargo(asignacion, fecha_desde, fecha_hasta):

    desde = datetime.strptime(fecha_desde, "%d/%m/%Y")
    hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y")

    dias = 0

    for fecha in recorrer_fechas(desde, hasta):

        fecha_str = fecha.strftime("%d/%m/%Y")

        # Si no es un día hábil, no cuenta
        if not es_dia_habil(fecha_str):
            continue

        dias += 1

    return dias
# ============================================================

# ============================================================
def nombre_dia(fecha):
    dias = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }

    return dias[fecha.weekday()]
# -----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
def recorrer_fechas(desde, hasta):

    fecha = desde

    while fecha <= hasta:

        yield fecha

        fecha += timedelta(days=1)
# --------------------------------------------------------------------------------

# ============================================================
# Devuelve una lista con todos los días hábiles
# comprendidos entre dos fechas.
# ============================================================

def dias_habiles_entre(fecha_desde, fecha_hasta):

    desde = datetime.strptime(fecha_desde, "%d/%m/%Y")
    hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y")

    dias = []

    for fecha in recorrer_fechas(desde, hasta):

        fecha_str = fecha.strftime("%d/%m/%Y")

        if es_dia_habil(fecha_str):

            dias.append(fecha_str)

    return dias
# ---------------------------------------------------------------------------------

# |==================== Analiza asignación ========================================
def analizar_asignacion(asignacion, fecha_desde, fecha_hasta):
    """
    Analiza una única asignación (cargo o módulo) y devuelve
    cuántos días o módulos fueron afectados.
    """

    desde = datetime.strptime(fecha_desde, "%d/%m/%Y")
    hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y")

    total = 0

    for fecha in recorrer_fechas(desde, hasta):

        # Si el día no es hábil no cuenta
        if not es_dia_habil(fecha.strftime("%d/%m/%Y")):
            continue

        # -------------------------------
        # CARGOS
        # -------------------------------
        if es_cargo(asignacion):

            if fecha.weekday() <= 4:       # lunes a viernes
                total += 1

        # -------------------------------
        # MÓDULOS
        # -------------------------------
        else:

            if nombre_dia(fecha) == asignacion["dia"]:

                total += int(asignacion["modulos"])

    return total
# ----------------------------------------------------------------------------

# =============================================================================
#          Calcula la cantidad de días perdidos de un cargo
# =============================================================================
def calcular_dias_cargo(cargo, fecha_desde, fecha_hasta):

    dias = dias_habiles_entre(fecha_desde, fecha_hasta)

    return len(dias)
# ------------------------------------------------------------------------------

# ==============================================================================
#                 Calcula la cantidad de módulos perdidos
# ==============================================================================
def calcular_modulos(modulo, fecha_desde, fecha_hasta):

    dias = dias_habiles_entre(fecha_desde, fecha_hasta)

    total = 0

    for fecha in dias:

        fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

        if nombre_dia(fecha_dt) == modulo["dia"]:

            total += int(modulo["modulos"])

    return total
# ---------------------------------------------------------------------------------------

# ========================= Analiza inasistencias de un docente =========================
def analizar_inasistencia(id_inasistencia):

    inasistencia = obtener_inasistencia(id_inasistencia)

    id_docente = inasistencia["id_docente"]
    fecha_desde = inasistencia["fecha_desde"]
    fecha_hasta = inasistencia["fecha_hasta"]
    motivo = inasistencia["motivo"]

    # Obtener las asignaciones del docente
    asignaciones = obtener_asignaciones_docente(id_docente)

    # Separarlas en cargos y módulos
    cargos, modulos = separar_asignaciones(asignaciones)

    resultado = {
        "id_inasistencia": id_inasistencia,
        "id_docente": id_docente,
        "motivo": motivo,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "cargos": [],
        "modulos": []
    }

    # Analizar cargos
    for cargo in cargos:

        dias = calcular_dias_cargo(
            cargo,
            fecha_desde,
            fecha_hasta
        )

        resultado["cargos"].append({
            "cargo": cargo["cargo"],
            "dias": dias,
            "motivo": motivo
        })

    # Analizar módulos
    for modulo in modulos:

        cantidad = calcular_modulos(
            modulo,
            fecha_desde,
            fecha_hasta
        )

        resultado["modulos"].append({
            "materia": modulo["materia"],
            "curso": modulo["curso"],
            "modulos": cantidad,
            "motivo": motivo
        })

    return resultado
# ------------------------------------------------------------------------------

# ==============================================================================
#               Calcula los módulos totales del ciclo lectivo
# ==============================================================================
def calcular_modulos_ciclo_lectivo(modulo):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fecha_inicio, fecha_fin
        FROM ciclo_lectivo
        LIMIT 1
    """)

    ciclo = cursor.fetchone()

    conn.close()

    if ciclo is None:
        return 0

    fecha_inicio = ciclo[0]
    fecha_fin = ciclo[1]

    dias = dias_habiles_entre(fecha_inicio, fecha_fin)

    cantidad_clases = 0

    for fecha in dias:

        fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")

        if nombre_dia(fecha_dt) == modulo["dia"]:
            cantidad_clases += 1

 
    return cantidad_clases * int(modulo["modulos"])
# -----------------------------------------------------------------------------

# ============================================================
# Calcula los días hábiles del ciclo lectivo
# ============================================================
def calcular_dias_ciclo_lectivo():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fecha_inicio, fecha_fin
        FROM ciclo_lectivo
        LIMIT 1
    """)

    ciclo = cursor.fetchone()

    conn.close()

    if ciclo is None:
        return 0

    fecha_inicio = ciclo[0]
    fecha_fin = ciclo[1]

    dias = dias_habiles_entre(fecha_inicio, fecha_fin)

    return len(dias)
# ------------------------------------------------------------------------------

# ============================================================
# Devuelve todas las inasistencias de un docente en un año
# ============================================================

def obtener_inasistencias_docente(id_docente, anio):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            id_docente,
            fecha_desde,
            fecha_hasta,
            motivo,
            observacion
        FROM inasistencia
        WHERE id_docente = ?
    """, (id_docente,))

    filas = cursor.fetchall()

    conn.close()

    resultado = []

    for fila in filas:

        # Obtener el año de la fecha de inicio
        anio_inasistencia = datetime.strptime(
            fila["fecha_desde"],
            "%d/%m/%Y"
        ).year

        if anio_inasistencia == anio:
            resultado.append(dict(fila))

    return resultado
#-----------------------------------------------------------------------

# ============================================================
# RESUMEN ANUAL DEL DOCENTE
# ============================================================
def resumen_docente(id_docente, anio):

    # --------------------------------------------------------
    # Asignaciones del docente
    # --------------------------------------------------------

    asignaciones = obtener_asignaciones_docente(id_docente)

    cargos, modulos = separar_asignaciones(asignaciones)

    # --------------------------------------------------------
    # Inasistencias del año
    # --------------------------------------------------------

    inasistencias = obtener_inasistencias_docente(
        id_docente,
        anio
    )

    resumen = {
        "id_docente": id_docente,
        "anio": anio,
        "cargos": [],
        "modulos": []
    }

    # ========================================================
    # CARGOS
    # ========================================================

    for cargo in cargos:

        dias_perdidos = 0

        for licencia in inasistencias:

            dias_perdidos += calcular_dias_cargo(
                cargo,
                licencia["fecha_desde"],
                licencia["fecha_hasta"]
            )

        dias_ciclo = calcular_dias_ciclo_lectivo()

        resumen["cargos"].append({

            "cargo": cargo["cargo"],

            "dias_ciclo": dias_ciclo,

            "dias_perdidos": dias_perdidos,

            "dias_trabajados": dias_ciclo - dias_perdidos

        })

    # ========================================================
    # MODULOS
    # ========================================================

    for modulo in modulos:

        modulos_perdidos = 0

        for licencia in inasistencias:

            modulos_perdidos += calcular_modulos(

                modulo,

                licencia["fecha_desde"],

                licencia["fecha_hasta"]

            )

        modulos_ciclo = calcular_modulos_ciclo_lectivo(modulo)

        resumen["modulos"].append({

            "materia": modulo["materia"],

            "curso": modulo["curso"],

            "modulos_ciclo": modulos_ciclo,

            "modulos_perdidos": modulos_perdidos,

            "modulos_trabajados": modulos_ciclo - modulos_perdidos

        })

    return resumen
# ---------------------------------------------------------------------------




# ====================== INICIO DE PRUEBAS ======================
if __name__ == "__main__":
    pass