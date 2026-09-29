# ============================================================
#              GENERADOR DE LICENCIAS SGE
# ============================================================

import json
import base64
import uuid
import os
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# ============================================================
#                    RUTAS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_SOLICITUD = os.path.join(
    BASE_DIR,
    "Solicitud_SGE.dat"
)

ARCHIVO_LICENCIA = os.path.join(
    BASE_DIR,
    "Licencia_SGE.lic"
)

ARCHIVO_CLAVE_PRIVADA = os.path.join(
    BASE_DIR,
    "claves",
    "clave_privada.pem"
)


# ============================================================
#              CARGAR SOLICITUD DE LICENCIA
# ============================================================

def cargar_solicitud():

    if not os.path.exists(ARCHIVO_SOLICITUD):

        print()
        print("ERROR: No se encontró el archivo")
        print("Solicitud_SGE.dat")
        print()
        print("Primero debe generarse una solicitud.")
        return None

    try:

        with open(
            ARCHIVO_SOLICITUD,
            "r",
            encoding="utf-8"
        ) as archivo:

            solicitud = json.load(archivo)

        return solicitud

    except Exception as e:

        print()
        print("ERROR AL LEER LA SOLICITUD")
        print(e)
        return None


# ============================================================
#              CARGAR CLAVE PRIVADA
# ============================================================

def cargar_clave_privada():

    if not os.path.exists(ARCHIVO_CLAVE_PRIVADA):

        print()
        print("ERROR: No se encontró la clave privada.")
        print()
        print("Ruta:")
        print(ARCHIVO_CLAVE_PRIVADA)

        return None

    try:

        with open(
            ARCHIVO_CLAVE_PRIVADA,
            "rb"
        ) as archivo:

            clave_privada = serialization.load_pem_private_key(
                archivo.read(),
                password=None
            )

        return clave_privada

    except Exception as e:

        print()
        print("ERROR AL CARGAR LA CLAVE PRIVADA")
        print(e)

        return None


# ============================================================
#              GENERAR ID DE LICENCIA
# ============================================================

def generar_id_licencia():

    identificador = uuid.uuid4().hex[:8].upper()

    año = datetime.now().year

    return f"SGE-{año}-{identificador}"


# ============================================================
#              CALCULAR VENCIMIENTO
# ============================================================

def calcular_vencimiento(
    tipo,
    fecha_emision
):

    if tipo == "permanente":

        return None

    if tipo == "anual":

        fecha = fecha_emision + timedelta(days=365)

        return fecha.strftime("%Y-%m-%d")

    if tipo == "prueba":

        while True:

            try:

                dias = int(
                    input(
                        "Cantidad de días de prueba: "
                    )
                )

                if dias <= 0:

                    print(
                        "La cantidad de días debe ser mayor que 0."
                    )
                    continue

                fecha = fecha_emision + timedelta(
                    days=dias
                )

                return fecha.strftime("%Y-%m-%d")

            except ValueError:

                print(
                    "Ingrese un número entero válido."
                )


# ============================================================
#              GENERAR LICENCIA
# ============================================================

def generar_licencia():

    print()
    print("=" * 60)
    print("              GENERADOR DE LICENCIAS SGE")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Cargar solicitud
    # --------------------------------------------------------

    solicitud = cargar_solicitud()

    if solicitud is None:

        return

    # --------------------------------------------------------
    # Mostrar datos de la solicitud
    # --------------------------------------------------------

    print("DATOS DE LA SOLICITUD")
    print("-" * 60)

    print(
        f"Institución : {solicitud.get('institucion', '')}"
    )

    print(
        f"Localidad   : {solicitud.get('localidad', '')}"
    )

    print(
        f"Provincia   : {solicitud.get('provincia', '')}"
    )

    print(
        f"ID solicitud: {solicitud.get('id_solicitud', '')}"
    )

    print(
        f"Fecha       : {solicitud.get('fecha_solicitud', '')}"
    )

    print("-" * 60)
    print()

    # --------------------------------------------------------
    # Confirmar emisión
    # --------------------------------------------------------

    confirmar = input(
        "¿Desea generar una licencia para esta solicitud? (S/N): "
    ).strip().upper()

    if confirmar != "S":

        print()
        print("Operación cancelada.")
        return

    # --------------------------------------------------------
    # Tipo de licencia
    # --------------------------------------------------------

    print()
    print("TIPO DE LICENCIA")
    print()
    print("1 - Permanente")
    print("2 - Anual")
    print("3 - Prueba")

    while True:

        opcion = input(
            "Seleccione una opción: "
        ).strip()

        if opcion == "1":

            tipo = "permanente"
            break

        elif opcion == "2":

            tipo = "anual"
            break

        elif opcion == "3":

            tipo = "prueba"
            break

        else:

            print(
                "Opción inválida."
            )

    # --------------------------------------------------------
    # Versión autorizada
    # --------------------------------------------------------

    print()

    version = input(
        "Versión autorizada de SGE: "
    ).strip()

    if not version:

        print()
        print("ERROR: Debe indicar una versión.")
        return

    # --------------------------------------------------------
    # Fechas
    # --------------------------------------------------------

    fecha_emision = datetime.now()

    fecha_vencimiento = calcular_vencimiento(
        tipo,
        fecha_emision
    )

    # --------------------------------------------------------
    # ID de licencia
    # --------------------------------------------------------

    id_licencia = generar_id_licencia()

    # --------------------------------------------------------
    # Construcción de los datos de licencia
    # --------------------------------------------------------

    datos_licencia = {

        "producto": "SGE",

        "id_licencia": id_licencia,

        "id_solicitud": solicitud.get(
            "id_solicitud"
        ),

        "institucion": solicitud.get(
            "institucion"
        ),

        "localidad": solicitud.get(
            "localidad"
        ),

        "provincia": solicitud.get(
            "provincia"
        ),

        "tipo": tipo,

        "version": version,

        "fecha_emision": fecha_emision.strftime(
            "%Y-%m-%d"
        ),

        "fecha_vencimiento": fecha_vencimiento
    }

    # ========================================================
    #             PREPARAR DATOS PARA FIRMAR
    # ========================================================

    contenido = json.dumps(
        datos_licencia,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    # ========================================================
    #             CARGAR CLAVE PRIVADA
    # ========================================================

    clave_privada = cargar_clave_privada()

    if clave_privada is None:

        return

    # ========================================================
    #                  FIRMAR LICENCIA
    # ========================================================

    try:

        firma = clave_privada.sign(
            contenido
        )

    except Exception as e:

        print()
        print("ERROR AL FIRMAR LA LICENCIA")
        print(e)

        return

    # ========================================================
    #             CODIFICAR FIRMA EN BASE64
    # ========================================================

    firma_base64 = base64.b64encode(
        firma
    ).decode("utf-8")

    # ========================================================
    #             ESTRUCTURA FINAL DE LICENCIA
    # ========================================================

    licencia_final = {

        "datos": datos_licencia,

        "firma": firma_base64
    }

    # ========================================================
    #                  GUARDAR LICENCIA
    # ========================================================

    try:

        with open(
            ARCHIVO_LICENCIA,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                licencia_final,
                archivo,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print()
        print("ERROR AL GUARDAR LA LICENCIA")
        print(e)

        return

    # ========================================================
    #                    RESULTADO
    # ========================================================

    print()
    print("=" * 60)
    print("           LICENCIA GENERADA CORRECTAMENTE")
    print("=" * 60)
    print()

    print(
        f"ID licencia       : {id_licencia}"
    )

    print(
        f"ID solicitud      : {datos_licencia['id_solicitud']}"
    )

    print(
        f"Institución       : {datos_licencia['institucion']}"
    )

    print(
        f"Localidad         : {datos_licencia['localidad']}"
    )

    print(
        f"Provincia         : {datos_licencia['provincia']}"
    )

    print(
        f"Tipo              : {datos_licencia['tipo']}"
    )

    print(
        f"Versión           : {datos_licencia['version']}"
    )

    print(
        f"Fecha de emisión  : {datos_licencia['fecha_emision']}"
    )

    if datos_licencia["fecha_vencimiento"]:

        print(
            f"Fecha vencimiento : "
            f"{datos_licencia['fecha_vencimiento']}"
        )

    else:

        print(
            "Fecha vencimiento : Sin vencimiento"
        )

    print()
    print(
        f"Archivo generado: {ARCHIVO_LICENCIA}"
    )

    print()
    print("=" * 60)


# ============================================================
#                       PROGRAMA
# ============================================================

if __name__ == "__main__":

    generar_licencia()