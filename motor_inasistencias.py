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

from database import conectar
from datetime import datetime
from datetime import timedelta
from pprint import pprint
from calendario_escolar import (dias_habiles, dias_clase_materia, es_feriado)


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

def es_cargo(asignacion):
    return asignacion["id_materia"] is None


def es_modulo(asignacion):
    return asignacion["id_materia"] is not None

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


def recorrer_fechas(desde, hasta):

    fecha = desde

    while fecha <= hasta:

        yield fecha

        fecha += timedelta(days=1)


# ====================== INICIO DE PRUEBAS ======================
obtener_asignaciones_docente(2)

if __name__ == "__main__":

    desde = datetime.strptime("01/06/2026", "%d/%m/%Y")
    hasta = datetime.strptime("05/06/2026", "%d/%m/%Y")

    for fecha in recorrer_fechas(desde, hasta):
        print(nombre_dia(fecha))

    pprint(obtener_asignaciones_docente(2))