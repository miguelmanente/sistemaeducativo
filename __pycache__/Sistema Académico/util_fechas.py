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

from datetime import datetime, timedelta

def calcular_dias_trabajados(id_docente, fecha_desde, fecha_hasta):

    dias_trabajo = obtener_dias_trabajo(id_docente)

    fecha_ini = datetime.strptime(fecha_desde, "%d/%m/%Y")
    fecha_fin = datetime.strptime(fecha_hasta, "%d/%m/%Y")

    dias_semana = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo"
    }

    contador = 0
    actual = fecha_ini

    while actual <= fecha_fin:

        nombre_dia = dias_semana[actual.weekday()]

        if nombre_dia in dias_trabajo:
            contador += 1

        actual += timedelta(days=1)

    return contador