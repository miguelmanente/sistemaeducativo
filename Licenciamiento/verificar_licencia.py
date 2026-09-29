# ============================================================
#              VERIFICADOR DE LICENCIAS SGE
# ============================================================

import json
import base64
import os
import sys
from datetime import datetime

from cryptography.hazmat.primitives import serialization


# ============================================================
#                    CONFIGURACIÓN
# ============================================================

VERSION_SGE = "1.0"


# ============================================================
#                    RUTAS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_CLAVE_PUBLICA = os.path.join(
    BASE_DIR,
    "claves",
    "clave_publica.pem"
)

ARCHIVO_LICENCIA_POR_DEFECTO = os.path.join(
    BASE_DIR,
    "Licencia_SGE.lic"
)


# ============================================================
#              OBTENER ARCHIVO DE LICENCIA
# ============================================================

def obtener_archivo_licencia():

    if len(sys.argv) > 1:

        return os.path.abspath(sys.argv[1])

    return ARCHIVO_LICENCIA_POR_DEFECTO


# ============================================================
#              CARGAR CLAVE PÚBLICA
# ============================================================

def cargar_clave_publica():

    if not os.path.exists(ARCHIVO_CLAVE_PUBLICA):

        print()
        print("ERROR: No se encontró la clave pública.")
        print()
        print("Ruta:")
        print(ARCHIVO_CLAVE_PUBLICA)

        return None

    try:

        with open(
            ARCHIVO_CLAVE_PUBLICA,
            "rb"
        ) as archivo:

            clave_publica = serialization.load_pem_public_key(
                archivo.read()
            )

        return clave_publica

    except Exception as e:

        print()
        print("ERROR AL CARGAR LA CLAVE PÚBLICA")
        print(e)

        return None


# ============================================================
#              CARGAR ARCHIVO DE LICENCIA
# ============================================================

def cargar_licencia(ruta_licencia):

    if not os.path.exists(ruta_licencia):

        print()
        print("ERROR: No se encontró el archivo de licencia.")
        print()
        print("Ruta:")
        print(ruta_licencia)

        return None

    try:

        with open(
            ruta_licencia,
            "r",
            encoding="utf-8"
        ) as archivo:

            licencia = json.load(archivo)

        return licencia

    except json.JSONDecodeError:

        print()
        print("ERROR: El archivo de licencia no contiene")
        print("un JSON válido.")

        return None

    except Exception as e:

        print()
        print("ERROR AL LEER LA LICENCIA")
        print(e)

        return None


# ============================================================
#              VERIFICAR ESTRUCTURA
# ============================================================

def verificar_estructura(licencia):

    if not isinstance(licencia, dict):

        return False

    if "datos" not in licencia:

        return False

    if "firma" not in licencia:

        return False

    if not isinstance(licencia["datos"], dict):

        return False

    datos = licencia["datos"]

    campos_obligatorios = [

        "producto",
        "id_licencia",
        "id_solicitud",
        "institucion",
        "localidad",
        "provincia",
        "tipo",
        "version",
        "fecha_emision",
        "fecha_vencimiento"

    ]

    for campo in campos_obligatorios:

        if campo not in datos:

            print()
            print(
                f"ERROR: Falta el campo '{campo}' "
                f"en la licencia."
            )

            return False

    return True


# ============================================================
#              VERIFICAR FIRMA DIGITAL
# ============================================================

def verificar_firma(
    licencia,
    clave_publica
):

    datos = licencia["datos"]

    firma_base64 = licencia["firma"]

    try:

        firma = base64.b64decode(
            firma_base64
        )

    except Exception:

        print()
        print("ERROR: La firma digital no tiene")
        print("un formato Base64 válido.")

        return False

    contenido = json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    try:

        clave_publica.verify(
            firma,
            contenido
        )

        return True

    except Exception:

        return False


# ============================================================
#              VERIFICAR PRODUCTO
# ============================================================

def verificar_producto(datos):

    if datos["producto"] != "SGE":

        print()
        print("LICENCIA INVÁLIDA ❌")
        print()
        print(
            "La licencia no corresponde al producto SGE."
        )

        return False

    return True


# ============================================================
#              VERIFICAR VERSIÓN
# ============================================================

def verificar_version(datos):

    version_licencia = str(
        datos["version"]
    )

    if version_licencia != VERSION_SGE:

        print()
        print("LICENCIA NO COMPATIBLE ❌")
        print()

        print(
            f"Versión del SGE      : {VERSION_SGE}"
        )

        print(
            f"Versión autorizada   : {version_licencia}"
        )

        print()

        print(
            "La licencia no autoriza "
            "esta versión del SGE."
        )

        return False

    return True


# ============================================================
#              VERIFICAR FECHA DE VENCIMIENTO
# ============================================================

def verificar_vencimiento(datos):

    fecha_vencimiento = datos.get(
        "fecha_vencimiento"
    )

    # --------------------------------------------------------
    # Licencia permanente
    # --------------------------------------------------------

    if fecha_vencimiento is None:

        return True

    # --------------------------------------------------------
    # Convertir fecha
    # --------------------------------------------------------

    try:

        vencimiento = datetime.strptime(
            fecha_vencimiento,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        print()
        print("ERROR: La fecha de vencimiento")
        print("no tiene un formato válido.")

        return False

    # --------------------------------------------------------
    # Comparar con fecha actual
    # --------------------------------------------------------

    fecha_actual = datetime.now().date()

    if fecha_actual > vencimiento:

        print()
        print("LICENCIA VENCIDA ❌")
        print()

        print(
            f"Fecha actual     : "
            f"{fecha_actual.strftime('%Y-%m-%d')}"
        )

        print(
            f"Fecha vencimiento: "
            f"{vencimiento.strftime('%Y-%m-%d')}"
        )

        return False

    return True


# ============================================================
#              MOSTRAR INFORMACIÓN
# ============================================================

def mostrar_licencia(datos):

    print()
    print("=" * 60)
    print("                LICENCIA SGE")
    print("=" * 60)
    print()

    print(
        f"Producto          : {datos['producto']}"
    )

    print(
        f"ID licencia       : {datos['id_licencia']}"
    )

    print(
        f"ID solicitud      : {datos['id_solicitud']}"
    )

    print(
        f"Institución       : {datos['institucion']}"
    )

    print(
        f"Localidad         : {datos['localidad']}"
    )

    print(
        f"Provincia         : {datos['provincia']}"
    )

    print(
        f"Tipo              : {datos['tipo']}"
    )

    print(
        f"Versión           : {datos['version']}"
    )

    print(
        f"Fecha de emisión  : {datos['fecha_emision']}"
    )

    if datos["fecha_vencimiento"] is None:

        print(
            "Fecha vencimiento : Sin vencimiento"
        )

    else:

        print(
            f"Fecha vencimiento : "
            f"{datos['fecha_vencimiento']}"
        )

    print()


# ============================================================
#                  VERIFICAR LICENCIA
# ============================================================

def verificar_licencia():

    print()
    print("=" * 60)
    print("              VERIFICADOR DE LICENCIAS SGE")
    print("=" * 60)

    # --------------------------------------------------------
    # Obtener archivo
    # --------------------------------------------------------

    ruta_licencia = obtener_archivo_licencia()

    print()
    print(
        f"Archivo: {ruta_licencia}"
    )

    # --------------------------------------------------------
    # Cargar licencia
    # --------------------------------------------------------

    licencia = cargar_licencia(
        ruta_licencia
    )

    if licencia is None:

        return False

    # --------------------------------------------------------
    # Verificar estructura
    # --------------------------------------------------------

    if not verificar_estructura(
        licencia
    ):

        print()
        print("LICENCIA INVÁLIDA ❌")
        print()
        print(
            "La estructura de la licencia "
            "no es válida."
        )

        return False

    datos = licencia["datos"]

    # --------------------------------------------------------
    # Verificar producto
    # --------------------------------------------------------

    if not verificar_producto(
        datos
    ):

        return False

    # --------------------------------------------------------
    # Cargar clave pública
    # --------------------------------------------------------

    clave_publica = cargar_clave_publica()

    if clave_publica is None:

        return False

    # --------------------------------------------------------
    # Verificar firma
    # --------------------------------------------------------

    if not verificar_firma(
        licencia,
        clave_publica
    ):

        print()
        print("LICENCIA INVÁLIDA ❌")
        print()
        print(
            "La firma digital NO corresponde "
            "con los datos de la licencia."
        )

        print()
        print(
            "La licencia pudo haber sido modificada "
            "o no fue emitida por el generador autorizado."
        )

        return False

    # --------------------------------------------------------
    # Verificar versión
    # --------------------------------------------------------

    if not verificar_version(
        datos
    ):

        return False

    # --------------------------------------------------------
    # Verificar vencimiento
    # --------------------------------------------------------

    if not verificar_vencimiento(
        datos
    ):

        return False

    # --------------------------------------------------------
    # Mostrar licencia
    # --------------------------------------------------------

    mostrar_licencia(
        datos
    )

    # --------------------------------------------------------
    # Resultado final
    # --------------------------------------------------------

    print("=" * 60)
    print("              LICENCIA VÁLIDA ✅")
    print("=" * 60)
    print()

    return True


# ============================================================
#                       PROGRAMA
# ============================================================

if __name__ == "__main__":

    verificar_licencia()