# ================ CONVERTIR FORMATOS DE FECHAS =============
# Funciones para convertir fechas entre la base de datos
# (YYYY-MM-DD) y la pantalla (DD/MM/AAAA)
# ============================================================

from datetime import datetime


# ========================= FORMATO YYYY-MM-DD =========================
def fecha_a_bd(fecha):
    """
    Convierte:
        24/02/2026
    a:
        2026-02-24
    """

    if not fecha:
        return ""

    return datetime.strptime(
        fecha,
        "%d/%m/%Y"
    ).strftime("%Y-%m-%d")
# ------------------------------------------------------------------------------

# ========================= FORMATO DD/MM/AAAA =================================
def fecha_a_pantalla(fecha):
    """
    Convierte:
        2026-02-24
    a:
        24/02/2026
    """

    if not fecha:
        return ""

    return datetime.strptime(
        fecha,
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")
# ------------------------------------------------------------------------------

if __name__ == "__main__":

    print(fecha_a_bd("24/02/2026"))

    print(fecha_a_pantalla("2026-02-24"))