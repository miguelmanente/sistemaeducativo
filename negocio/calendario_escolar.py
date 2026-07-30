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
from database import conectar

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
print(es_dia_habil("02/03/2026"))
print(es_feriado("09/07/2026"))
if __name__ == "__main__":
    generar_calendario(2026)
    