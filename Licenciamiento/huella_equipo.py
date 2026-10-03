
# =====================================================
#              HUELLA DEL EQUIPO SGE
# =====================================================

import hashlib
import platform
import subprocess


# =====================================================
#        OBTENER IDENTIFICADOR DE WINDOWS
# =====================================================

def obtener_identificador_windows():
    """
    Obtiene el identificador UUID de la computadora
    mediante Windows.

    Devuelve:
        str -> identificador del equipo
    """

    try:

        resultado = subprocess.check_output(
            [
                "wmic",
                "csproduct",
                "get",
                "uuid"
            ],
            stderr=subprocess.DEVNULL,
            text=True
        )

        lineas = [
            linea.strip()
            for linea in resultado.splitlines()
            if linea.strip()
        ]

        if len(lineas) >= 2:

            identificador = lineas[1].strip()

            if identificador:
                return identificador

    except Exception:
        pass

    return None


# =====================================================
#          OBTENER DATOS BASE DEL EQUIPO
# =====================================================

def obtener_datos_equipo():
    """
    Obtiene los datos que se utilizarán para construir
    la huella del equipo.

    Estos datos NO son todavía la huella.

    Devuelve:
        dict
    """

    datos = {

        "sistema":
            platform.system(),

        "nombre_equipo":
            platform.node(),

        "arquitectura":
            platform.machine(),

        "procesador":
            platform.processor(),

        "uuid_windows":
            obtener_identificador_windows()
    }

    return datos


# =====================================================
#             GENERAR HUELLA DEL EQUIPO
# =====================================================

def obtener_huella_equipo():
    """
    Genera una huella SHA-256 a partir de los datos
    identificativos del equipo.

    Devuelve:
        str -> huella hexadecimal de 64 caracteres
    """

    datos = obtener_datos_equipo()

    partes = []

    for clave in sorted(datos):

        valor = datos.get(clave)

        if valor is None:
            valor = ""

        valor = str(valor).strip()

        partes.append(
            f"{clave}={valor}"
        )

    cadena_base = "|".join(partes)

    huella = hashlib.sha256(
        cadena_base.encode("utf-8")
    ).hexdigest().upper()

    return huella


# =====================================================
#               MOSTRAR INFORMACIÓN
# =====================================================

def mostrar_huella():

    datos = obtener_datos_equipo()

    huella = obtener_huella_equipo()

    print()
    print("=" * 70)
    print("                 HUELLA DEL EQUIPO SGE")
    print("=" * 70)

    print()

    print(
        f"Sistema operativo : "
        f"{datos.get('sistema')}"
    )

    print(
        f"Nombre equipo     : "
        f"{datos.get('nombre_equipo')}"
    )

    print(
        f"Arquitectura      : "
        f"{datos.get('arquitectura')}"
    )

    print(
        f"Procesador        : "
        f"{datos.get('procesador')}"
    )

    print(
        f"UUID Windows      : "
        f"{datos.get('uuid_windows')}"
    )

    print()

    print("-" * 70)

    print(
        "HUELLA SHA-256:"
    )

    print()

    print(
        huella
    )

    print()

    print("=" * 70)


# =====================================================
#                    PROGRAMA
# =====================================================

if __name__ == "__main__":

    mostrar_huella()

