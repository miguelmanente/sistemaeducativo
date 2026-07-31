# =================================================================
#                   CALENDARIO ESCOLAR
# =================================================================
"""
    Genera el calendario completo de un año.

    - Carga todos los días del año.
    - Marca sábados y domingos como no hábiles.
    - Los feriados quedan inicialmente en 0.
"""

#=============== BIBLIOTECAS =====================================
from datetime import date, timedelta
from datetime import datetime
from database import conectar
from utilidades.fechas import fecha_a_bd, fecha_a_pantalla

#============================== GENERAR CALENDARIO =====================================
def generar_calendario(anio):
    conn = conectar()
    cursor = conn.cursor()

    # Elimina el calendario existente para ese año
    cursor.execute("""
        DELETE FROM calendario_escolar
        WHERE substr(fecha, 7, 4) = ?
    """, (str(anio),))

    dias_semana = [
        "Lunes",
        "Martes",
        "Miércoles",
        "Jueves",
        "Viernes",
        "Sábado",
        "Domingo"
    ]

    fecha = date(anio, 1, 1)

    while fecha.year == anio:

        dia = dias_semana[fecha.weekday()]

        # Lunes a viernes = hábil
        es_habil = 1 if fecha.weekday() < 5 else 0

        cursor.execute("""
            INSERT INTO calendario_escolar
            (
                fecha,
                dia_semana,
                es_habil,
                es_feriado,
                descripcion
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            fecha.strftime("%d/%m/%Y"),
            dia,
            es_habil,
            0,
            ""
        ))

        fecha += timedelta(days=1)

    conn.commit()
    conn.close()

    print(f"Calendario {anio} generado correctamente.")
# ------------------------------------------------------------------------------

#============================== DÍA HÁBIL =====================================
def es_dia_habil(fecha):
    """
    Devuelve True si la fecha es un día hábil.
    False en caso contrario.
    """

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT es_habil
        FROM calendario_escolar
        WHERE fecha = ?
    """, (fecha,))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return False

    return bool(resultado[0])
#-----------------------------------------------------------------------------

#============================== FERIADOS =====================================
def es_feriado(fecha):
    """
    Devuelve True si la fecha es feriado.
    """

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT es_feriado
        FROM calendario_escolar
        WHERE fecha = ?
    """, (fecha,))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return False

    return bool(resultado[0])
# ---------------------------------------------------------------------------------

#============================== CICLO LECTIVO =====================================
def obtener_ciclo_lectivo(anio):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            fecha_inicio,
            fecha_fin
        FROM ciclo_lectivo
        WHERE anio = ?
    """, (anio,))

    resultado = cursor.fetchone()

    conn.close()

    if resultado is None:
        return None

    return {
        "fecha_inicio": fecha_a_pantalla(resultado[0]),
        "fecha_fin": fecha_a_pantalla(resultado[1])
    }
#---------------------------------------------------------------------------------

# ================================================================================ 
#                   Guarda o actualiza un ciclo lectivo
# ===============================================================================

def guardar_ciclo_lectivo(anio, fecha_inicio, fecha_fin, observacion=""):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ciclo_lectivo
        WHERE anio = ?
    """, (anio,))

    fecha_inicio = fecha_a_bd(fecha_inicio)
    fecha_fin = fecha_a_bd(fecha_fin)

    existe = cursor.fetchone()[0]

    if existe:

        cursor.execute("""
            UPDATE ciclo_lectivo
            SET
                fecha_inicio = ?,
                fecha_fin = ?,
                observacion = ?
            WHERE anio = ?
        """, (
            fecha_inicio,
            fecha_fin,
            observacion,
            anio
        ))

    else:

        cursor.execute("""
            INSERT INTO ciclo_lectivo
            (
                anio,
                fecha_inicio,
                fecha_fin,
                observacion
            )

            VALUES (?, ?, ?, ?)
        """, (
            anio,
            fecha_inicio,
            fecha_fin,
            observacion
        ))

    conn.commit()
    conn.close()
# --------------------------------------------------------------------------------------

# ============================================================
# Cuenta cuántos días hábiles de un determinado día de la semana
# existen entre dos fechas.
#
# Ejemplo:
# contar_dias_semana("Miércoles",
#                    "24/02/2026",
#                    "18/12/2026")
#
# Devuelve:
#     32
# ============================================================
def contar_dias_semana(dia_semana, fecha_inicio, fecha_fin):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM calendario_escolar
        WHERE
            fecha BETWEEN ? AND ?
            AND dia_semana = ?
            AND es_habil = 1
            AND es_feriado = 0
    """, (
        fecha_inicio,
        fecha_fin,
        dia_semana
    ))

    cantidad = cursor.fetchone()[0]

    conn.close()

    return cantidad
# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass
    