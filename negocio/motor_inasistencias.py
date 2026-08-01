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
from datetime import datetime, timedelta
from negocio.calendario_escolar import (es_dia_habil, es_feriado)
# -------------------------------------------------------------

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


# ====================== INICIO DE PRUEBAS ======================

if __name__ == "__main__":
    asignaciones = obtener_asignaciones_docente(2)

    for asignacion in asignaciones:

        if es_cargo(asignacion):

            dias = analizar_cargo(
                asignacion,
                "02/03/2026",
                "06/03/2026"
            )

            print(asignacion["cargo"])
            print("Días afectados:", dias)