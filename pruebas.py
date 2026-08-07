from database import conectar
def es_dia_no_laborable(fecha, anio):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM dias_no_laborables
        WHERE anio = ?
        AND fecha = ?
        LIMIT 1
    """, (anio, fecha))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None


print(es_dia_no_laborable("25/03/2026", 2026))