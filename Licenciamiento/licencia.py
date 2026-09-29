
# ============================================================
#                 MÓDULO DE LICENCIAMIENTO SGE
# ============================================================

import sys
import json
import base64
from pathlib import Path
from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


# ============================================================
#                 CONFIGURACIÓN DEL SGE
# ============================================================

VERSION_SGE = "1.0"


# ============================================================
#                 UBICACIÓN DE LA APLICACIÓN
# ============================================================

def obtener_carpeta_aplicacion():
    """
    Devuelve la carpeta donde se encuentra SGE.

    Si está compilado con PyInstaller:
        devuelve la carpeta donde está SGE.exe.

    Si se ejecuta desde Python:
        devuelve la carpeta donde está licencia.py.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


# ============================================================
#                 ARCHIVO DE LICENCIA
# ============================================================

def obtener_archivo_licencia():
    """
    Devuelve la ruta de la licencia predeterminada.
    """

    return obtener_carpeta_aplicacion() / "Licencia_SGE.lic"


# ============================================================
#                 ARCHIVO DE CLAVE PÚBLICA
# ============================================================

def obtener_archivo_clave_publica():
    """
    Busca la clave pública.

    Primero:
        claves/clave_publica.pem

    Si no existe:
        clave_publica.pem
    """

    carpeta = obtener_carpeta_aplicacion()

    ruta_1 = carpeta / "claves" / "clave_publica.pem"

    if ruta_1.exists():
        return ruta_1

    ruta_2 = carpeta / "clave_publica.pem"

    return ruta_2


# ============================================================
#                 CARGAR CLAVE PÚBLICA
# ============================================================

def cargar_clave_publica():
    """
    Carga la clave pública Ed25519 utilizada
    para verificar las licencias.
    """

    ruta_clave = obtener_archivo_clave_publica()

    if not ruta_clave.exists():
        raise FileNotFoundError(
            f"No se encontró la clave pública:\n{ruta_clave}"
        )

    with open(ruta_clave, "rb") as archivo:
        clave_publica = serialization.load_pem_public_key(
            archivo.read()
        )

    if not isinstance(clave_publica, Ed25519PublicKey):
        raise ValueError(
            "La clave pública no es una clave Ed25519 válida."
        )

    return clave_publica


# ============================================================
#                 DATOS CANÓNICOS
# ============================================================

def generar_datos_canonicos(datos):
    """
    Convierte los datos de la licencia exactamente de la misma
    manera utilizada al momento de firmarlos.
    """

    return json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")


# ============================================================
#                 VALIDAR ESTRUCTURA
# ============================================================

def validar_estructura(datos_licencia):
    """
    Comprueba que estén presentes todos los campos
    necesarios de la licencia.
    """

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
        if campo not in datos_licencia:
            return False

    return True


# ============================================================
#                 VERIFICAR FIRMA DIGITAL
# ============================================================

def verificar_firma(datos_licencia, firma_base64):
    """
    Comprueba que la firma digital corresponda exactamente
    con los datos contenidos en la licencia.
    """

    try:

        clave_publica = cargar_clave_publica()

        datos_canonicos = generar_datos_canonicos(
            datos_licencia
        )

        firma = base64.b64decode(
            firma_base64
        )

        clave_publica.verify(
            firma,
            datos_canonicos
        )

        return True

    except Exception:
        return False


# ============================================================
#                 VERIFICAR VENCIMIENTO
# ============================================================

def verificar_vencimiento(fecha_vencimiento):
    """
    Comprueba si la licencia está vigente.

    None significa licencia permanente.

    Devuelve:

        True  -> vigente
        False -> vencida o inválida
    """

    if fecha_vencimiento is None:
        return True

    try:

        fecha_vencimiento = datetime.strptime(
            fecha_vencimiento,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        return False

    fecha_actual = datetime.now().date()

    return fecha_actual <= fecha_vencimiento


# ============================================================
#                 VERIFICAR VERSIÓN
# ============================================================

def verificar_version(version_autorizada):
    """
    Comprueba que la licencia corresponda a la versión
    actual de SGE.
    """

    return version_autorizada == VERSION_SGE


# ============================================================
#             ANALIZAR LICENCIA COMPLETA
# ============================================================

def analizar_licencia(ruta_licencia=None):
    """
    Analiza completamente una licencia y devuelve:

        (True, "LICENCIA_VÁLIDA")

    o:

        (False, "MOTIVO")

    Los motivos posibles son:

        LICENCIA_NO_ENCONTRADA
        ARCHIVO_INVALIDO
        ESTRUCTURA_INVALIDA
        PRODUCTO_INVALIDO
        FIRMA_INVALIDA
        VERSION_NO_COMPATIBLE
        LICENCIA_VENCIDA
        FECHA_INVALIDA
        ERROR_CLAVE_PUBLICA
        ERROR_DESCONOCIDO
    """

    try:

        # ----------------------------------------------------
        # Determinar archivo
        # ----------------------------------------------------

        if ruta_licencia is None:
            ruta_licencia = obtener_archivo_licencia()
        else:
            ruta_licencia = Path(ruta_licencia)

        # ----------------------------------------------------
        # Comprobar existencia
        # ----------------------------------------------------

        if not ruta_licencia.exists():
            return False, "LICENCIA_NO_ENCONTRADA"

        # ----------------------------------------------------
        # Leer archivo
        # ----------------------------------------------------

        try:

            with open(
                ruta_licencia,
                "r",
                encoding="utf-8"
            ) as archivo:

                licencia = json.load(archivo)

        except (json.JSONDecodeError, UnicodeDecodeError):

            return False, "ARCHIVO_INVALIDO"

        # ----------------------------------------------------
        # Estructura principal
        # ----------------------------------------------------

        if "datos" not in licencia:
            return False, "ESTRUCTURA_INVALIDA"

        if "firma" not in licencia:
            return False, "ESTRUCTURA_INVALIDA"

        datos = licencia["datos"]
        firma = licencia["firma"]

        # ----------------------------------------------------
        # Estructura de datos
        # ----------------------------------------------------

        if not isinstance(datos, dict):
            return False, "ESTRUCTURA_INVALIDA"

        if not validar_estructura(datos):
            return False, "ESTRUCTURA_INVALIDA"

        # ----------------------------------------------------
        # Producto
        # ----------------------------------------------------

        if datos["producto"] != "SGE":
            return False, "PRODUCTO_INVALIDO"

        # ----------------------------------------------------
        # Firma digital
        # ----------------------------------------------------

        try:

            firma_valida = verificar_firma(
                datos,
                firma
            )

        except FileNotFoundError:

            return False, "ERROR_CLAVE_PUBLICA"

        except Exception:

            return False, "ERROR_CLAVE_PUBLICA"

        if not firma_valida:
            return False, "FIRMA_INVALIDA"

        # ----------------------------------------------------
        # Versión
        # ----------------------------------------------------

        if not verificar_version(
            datos["version"]
        ):
            return False, "VERSION_NO_COMPATIBLE"

        # ----------------------------------------------------
        # Fecha de vencimiento
        # ----------------------------------------------------

        fecha_vencimiento = datos["fecha_vencimiento"]

        if fecha_vencimiento is not None:

            try:

                fecha = datetime.strptime(
                    fecha_vencimiento,
                    "%Y-%m-%d"
                ).date()

            except ValueError:

                return False, "FECHA_INVALIDA"

            fecha_actual = datetime.now().date()

            if fecha_actual > fecha:

                return False, "LICENCIA_VENCIDA"

        # ----------------------------------------------------
        # Todo correcto
        # ----------------------------------------------------

        return True, "LICENCIA_VALIDA"

    except Exception:

        return False, "ERROR_DESCONOCIDO"


# ============================================================
#                 VERIFICAR LICENCIA
# ============================================================

def verificar_licencia(ruta_licencia=None):
    """
    Función compatible con la versión anterior.

    Devuelve:

        True  -> licencia válida
        False -> licencia inválida
    """

    valida, motivo = analizar_licencia(
        ruta_licencia
    )

    return valida


# ============================================================
#                 OBTENER DATOS DE LICENCIA
# ============================================================

def obtener_datos_licencia(ruta_licencia=None):
    """
    Devuelve los datos de una licencia válida.

    Si la licencia no es válida:
        devuelve None.
    """

    valida, motivo = analizar_licencia(
        ruta_licencia
    )

    if not valida:
        return None

    try:

        if ruta_licencia is None:
            ruta_licencia = obtener_archivo_licencia()
        else:
            ruta_licencia = Path(ruta_licencia)

        with open(
            ruta_licencia,
            "r",
            encoding="utf-8"
        ) as archivo:

            licencia = json.load(archivo)

        return licencia["datos"]

    except Exception:

        return None


# ============================================================
#                 PRUEBA DIRECTA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("           VERIFICACIÓN DE LICENCIA SGE")
    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Archivo indicado desde PowerShell
    # --------------------------------------------------------

    if len(sys.argv) > 1:

        ruta = Path(sys.argv[1]).resolve()

    else:

        ruta = obtener_archivo_licencia()

    print("Archivo de licencia:")
    print(ruta)
    print()

    # --------------------------------------------------------
    # Analizar licencia
    # --------------------------------------------------------

    valida, motivo = analizar_licencia(ruta)

    if valida:

        datos = obtener_datos_licencia(ruta)

        print("LICENCIA VÁLIDA ✅")
        print()

        print(
            f"ID licencia       : "
            f"{datos['id_licencia']}"
        )

        print(
            f"Institución       : "
            f"{datos['institucion']}"
        )

        print(
            f"Localidad         : "
            f"{datos['localidad']}"
        )

        print(
            f"Provincia         : "
            f"{datos['provincia']}"
        )

        print(
            f"Tipo              : "
            f"{datos['tipo']}"
        )

        print(
            f"Versión           : "
            f"{datos['version']}"
        )

        print(
            f"Fecha de emisión  : "
            f"{datos['fecha_emision']}"
        )

        print(
            f"Fecha vencimiento : "
            f"{datos['fecha_vencimiento']}"
        )

    else:

        print("LICENCIA INVÁLIDA ❌")
        print()
        print(f"Motivo técnico: {motivo}")

    print()
    print("=" * 60)

