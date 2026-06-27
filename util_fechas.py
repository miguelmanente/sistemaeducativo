from datetime import datetime, timedelta
from database import conectar


# =====================================================
# Devuelve los días que trabaja el docente
# =====================================================
def obtener_dias_trabajo(id_docente):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT dia
        FROM asignacion
        WHERE id_docente = ?
        AND activo = 1
    """, (id_docente,))

    datos = cursor.fetchall()

    conn.close()

    dias = set()

    for (dia,) in datos:

        if dia == "Lunes a Viernes":

            dias.update([
                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes"
            ])

        else:
            dias.add(dia)

    return dias