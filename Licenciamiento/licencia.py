
# =====================================================
#              MÓDULO DE LICENCIAMIENTO SGE
# =====================================================

import sys
import json
import base64

from pathlib import Path
from datetime import datetime

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


# =====================================================
#          OBTENER MÓDULO DE HUELLA DEL EQUIPO
# =====================================================

try:

    from .huella_equipo import obtener_huella_equipo

except ImportError:

    from huella_equipo import obtener_huella_equipo


# =====================================================
#              CONFIGURACIÓN DEL SGE
# =====================================================

VERSION_SGE = "1.0"


# =====================================================
#          OBTENER CARPETA DEL SGE
# =====================================================

def obtener_carpeta_sge():

    """
    Devuelve la carpeta principal del SGE.
    """

    # ---------------------------------------------
    # SGE COMPILADO
    # ---------------------------------------------

    if getattr(sys, "frozen", False):

        return Path(
            sys.executable
        ).resolve().parent


    # ---------------------------------------------
    # SGE EN DESARROLLO
    # ---------------------------------------------

    return Path(
        __file__
    ).resolve().parent.parent


# =====================================================
#       OBTENER CARPETA DE LICENCIAMIENTO
# =====================================================

def obtener_carpeta_licenciamiento():

    # ---------------------------------------------
    # DESARROLLO
    # ---------------------------------------------

    if not getattr(sys, "frozen", False):

        return (
            Path(__file__).resolve().parent
        )


    # ---------------------------------------------
    # COMPILADO
    # ---------------------------------------------

    return (
        Path(sys.executable).resolve().parent
    )


# =====================================================
#              ARCHIVO DE LICENCIA
# =====================================================

def obtener_archivo_licencia():

    carpeta = obtener_carpeta_licenciamiento()

    return (
        carpeta / "Licencia_SGE.lic"
    )


# =====================================================
#              ARCHIVO DE CLAVE PÚBLICA
# =====================================================

def obtener_archivo_clave_publica():

    # ---------------------------------------------
    # SGE EN DESARROLLO
    # ---------------------------------------------

    if not getattr(sys, "frozen", False):

        ruta = (
            Path(__file__).resolve().parent
            / "claves"
            / "clave_publica.pem"
        )

        return (
            ruta
            if ruta.exists()
            else None
        )


    # ---------------------------------------------
    # SGE COMPILADO
    # ---------------------------------------------

    carpeta_exe = (
        Path(sys.executable).resolve().parent
    )

    # -------------------------------------------------
    # POSIBLE UBICACIÓN 1
    #
    # PyInstaller --onedir normalmente coloca los
    # archivos adicionales dentro de:
    #
    # SGE\
    # ├── SGE.exe
    # └── _internal\
    #     └── claves\
    #         └── clave_publica.pem
    # -------------------------------------------------

    ruta_interna = (
        Path(sys._MEIPASS)
        / "claves"
        / "clave_publica.pem"
    )

    if ruta_interna.exists():

        return ruta_interna


    # -------------------------------------------------
    # POSIBLE UBICACIÓN 2
    #
    # Permite una distribución donde la carpeta
    # claves queda junto al ejecutable:
    #
    # SGE\
    # ├── SGE.exe
    # └── claves\
    #     └── clave_publica.pem
    # -------------------------------------------------

    ruta_junto_exe = (
        carpeta_exe
        / "claves"
        / "clave_publica.pem"
    )

    if ruta_junto_exe.exists():

        return ruta_junto_exe


    # -------------------------------------------------
    # POSIBLE UBICACIÓN 3
    #
    # Algunos esquemas de distribución pueden dejar
    # los archivos internos directamente bajo la
    # carpeta _internal del ejecutable.
    # -------------------------------------------------

    ruta_internal_exe = (
        carpeta_exe
        / "_internal"
        / "claves"
        / "clave_publica.pem"
    )

    if ruta_internal_exe.exists():

        return ruta_internal_exe


    # ---------------------------------------------
    # No encontrada
    # ---------------------------------------------

    return None


# =====================================================
#              CARGAR CLAVE PÚBLICA
# =====================================================

def cargar_clave_publica():

    ruta = obtener_archivo_clave_publica()

    if ruta is None:

        raise FileNotFoundError(
            "No se encontró la clave pública de SGE."
        )

    with open(
        ruta,
        "rb"
    ) as archivo:

        clave_publica = (
            serialization.load_pem_public_key(
                archivo.read()
            )
        )

    if not isinstance(
        clave_publica,
        Ed25519PublicKey
    ):

        raise ValueError(
            "La clave pública no es Ed25519."
        )

    return clave_publica


# =====================================================
#          GENERAR DATOS CANÓNICOS
# =====================================================

def generar_datos_canonicos(datos):

    return json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")


# =====================================================
#          VALIDAR ESTRUCTURA
# =====================================================

def validar_estructura(licencia):

    if not isinstance(
        licencia,
        dict
    ):

        return False

    if "datos" not in licencia:

        return False

    if "firma" not in licencia:

        return False

    datos = licencia["datos"]

    if not isinstance(
        datos,
        dict
    ):

        return False

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
        "fecha_vencimiento",
        "huella_equipo"
    ]

    for campo in campos_obligatorios:

        if campo not in datos:

            return False

    return True


# =====================================================
#              VERIFICAR FIRMA
# =====================================================

def verificar_firma(licencia):

    try:

        clave_publica = (
            cargar_clave_publica()
        )

        datos = licencia["datos"]

        firma_base64 = (
            licencia["firma"]
        )

        firma = base64.b64decode(
            firma_base64,
            validate=True
        )

        datos_canonicos = (
            generar_datos_canonicos(
                datos
            )
        )

        clave_publica.verify(
            firma,
            datos_canonicos
        )

        return True

    except Exception:

        return False


# =====================================================
#          VALIDAR HUELLA DEL EQUIPO
# =====================================================

def validar_huella_formato(huella):

    if not isinstance(
        huella,
        str
    ):

        return False

    huella = huella.strip()

    if len(huella) != 64:

        return False

    try:

        int(
            huella,
            16
        )

    except ValueError:

        return False

    return True


# =====================================================
#       VERIFICAR HUELLA DEL EQUIPO
# =====================================================

def verificar_huella_equipo(datos):

    huella_licencia = datos.get(
        "huella_equipo"
    )

    # ---------------------------------------------
    # La licencia no contiene huella
    # ---------------------------------------------

    if huella_licencia is None:

        return (
            False,
            "HUELLA_NO_ENCONTRADA"
        )


    # ---------------------------------------------
    # Validar formato
    # ---------------------------------------------

    if not validar_huella_formato(
        huella_licencia
    ):

        return (
            False,
            "HUELLA_INVALIDA"
        )


    # ---------------------------------------------
    # Obtener huella actual
    # ---------------------------------------------

    try:

        huella_actual = (
            obtener_huella_equipo()
        )

    except Exception:

        return (
            False,
            "ERROR_HUELLA_EQUIPO"
        )


    # ---------------------------------------------
    # Comparar huellas
    # ---------------------------------------------

    if (
        huella_actual.upper()
        != huella_licencia.upper()
    ):

        return (
            False,
            "EQUIPO_NO_AUTORIZADO"
        )


    # ---------------------------------------------
    # Equipo autorizado
    # ---------------------------------------------

    return (
        True,
        "EQUIPO_AUTORIZADO"
    )


# =====================================================
#            VERIFICAR VENCIMIENTO
# =====================================================

def verificar_vencimiento(datos):

    fecha_vencimiento = (
        datos.get(
            "fecha_vencimiento"
        )
    )

    # ---------------------------------------------
    # Licencia permanente
    # ---------------------------------------------

    if fecha_vencimiento is None:

        return True


    # ---------------------------------------------
    # Convertir fecha
    # ---------------------------------------------

    try:

        fecha = datetime.strptime(
            fecha_vencimiento,
            "%Y-%m-%d"
        ).date()

    except (
        TypeError,
        ValueError
    ):

        return None


    # ---------------------------------------------
    # Comparar con fecha actual
    # ---------------------------------------------

    fecha_actual = (
        datetime.now().date()
    )

    if fecha_actual > fecha:

        return False

    return True


# =====================================================
#              VERIFICAR VERSIÓN
# =====================================================

def verificar_version(datos):

    return (
        datos.get("version")
        == VERSION_SGE
    )


# =====================================================
#          ANALIZAR LICENCIA COMPLETA
# =====================================================

def analizar_licencia(
    ruta_licencia=None
):

    # ---------------------------------------------
    # Determinar licencia
    # ---------------------------------------------

    if ruta_licencia is None:

        ruta = (
            obtener_archivo_licencia()
        )

    else:

        ruta = Path(
            ruta_licencia
        )


    # ---------------------------------------------
    # Verificar existencia
    # ---------------------------------------------

    if not ruta.exists():

        return (
            False,
            "LICENCIA_NO_ENCONTRADA"
        )


    # ---------------------------------------------
    # Leer archivo
    # ---------------------------------------------

    try:

        with open(
            ruta,
            "r",
            encoding="utf-8"
        ) as archivo:

            licencia = json.load(
                archivo
            )

    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError
    ):

        return (
            False,
            "ARCHIVO_INVALIDO"
        )


    # ---------------------------------------------
    # Validar estructura
    # ---------------------------------------------

    if not validar_estructura(
        licencia
    ):

        return (
            False,
            "ESTRUCTURA_INVALIDA"
        )


    datos = licencia["datos"]


    # ---------------------------------------------
    # Verificar producto
    # ---------------------------------------------

    if datos.get(
        "producto"
    ) != "SGE":

        return (
            False,
            "PRODUCTO_INVALIDO"
        )


    # ---------------------------------------------
    # Verificar clave pública
    # ---------------------------------------------

    try:

        clave_publica = (
            cargar_clave_publica()
        )

    except Exception:

        return (
            False,
            "ERROR_CLAVE_PUBLICA"
        )


    # ---------------------------------------------
    # Verificar firma
    # ---------------------------------------------

    try:

        firma_base64 = (
            licencia["firma"]
        )

        firma = base64.b64decode(
            firma_base64,
            validate=True
        )

        datos_canonicos = (
            generar_datos_canonicos(
                datos
            )
        )

        clave_publica.verify(
            firma,
            datos_canonicos
        )

    except Exception:

        return (
            False,
            "FIRMA_INVALIDA"
        )


    # =================================================
    # VERIFICAR HUELLA DEL EQUIPO
    #
    # La firma ya fue comprobada.
    # Por lo tanto, ahora podemos confiar en la huella
    # que contiene la licencia.
    # =================================================

    equipo_autorizado, motivo_huella = (
        verificar_huella_equipo(
            datos
        )
    )

    if not equipo_autorizado:

        return (
            False,
            motivo_huella
        )


    # ---------------------------------------------
    # Verificar versión
    # ---------------------------------------------

    if not verificar_version(
        datos
    ):

        return (
            False,
            "VERSION_NO_COMPATIBLE"
        )


    # ---------------------------------------------
    # Verificar vencimiento
    # ---------------------------------------------

    resultado_vencimiento = (
        verificar_vencimiento(
            datos
        )
    )

    if resultado_vencimiento is None:

        return (
            False,
            "FECHA_INVALIDA"
        )

    if resultado_vencimiento is False:

        return (
            False,
            "LICENCIA_VENCIDA"
        )


    # ---------------------------------------------
    # Todo correcto
    # ---------------------------------------------

    return (
        True,
        "LICENCIA_VALIDA"
    )


# =====================================================
#              VERIFICAR LICENCIA
# =====================================================

def verificar_licencia(
    ruta_licencia=None
):

    valida, motivo = (
        analizar_licencia(
            ruta_licencia
        )
    )

    return valida


# =====================================================
#          OBTENER DATOS DE LICENCIA
# =====================================================

def obtener_datos_licencia(
    ruta_licencia=None
):

    valida, motivo = (
        analizar_licencia(
            ruta_licencia
        )
    )

    if not valida:

        return None


    if ruta_licencia is None:

        ruta = (
            obtener_archivo_licencia()
        )

    else:

        ruta = Path(
            ruta_licencia
        )


    try:

        with open(
            ruta,
            "r",
            encoding="utf-8"
        ) as archivo:

            licencia = json.load(
                archivo
            )

        return licencia.get(
            "datos"
        )

    except Exception:

        return None


# =====================================================
#                    PRUEBA DIRECTA
# =====================================================

if __name__ == "__main__":

    if len(sys.argv) > 1:

        ruta_prueba = Path(
            sys.argv[1]
        )

    else:

        ruta_prueba = (
            obtener_archivo_licencia()
        )


    valida, motivo = (
        analizar_licencia(
            ruta_prueba
        )
    )


    print()
    print(
        "=============================================="
    )
    print(
        "          VERIFICACIÓN DE LICENCIA SGE"
    )
    print(
        "=============================================="
    )
    print()

    print(
        f"Archivo de licencia:\n"
        f"{ruta_prueba}"
    )

    print()


    if valida:

        datos = (
            obtener_datos_licencia(
                ruta_prueba
            )
        )

        print(
            "LICENCIA VÁLIDA ✅"
        )

        print()

        if datos:

            print(
                f"ID licencia       : "
                f"{datos.get('id_licencia')}"
            )

            print(
                f"Institución       : "
                f"{datos.get('institucion')}"
            )

            print(
                f"Localidad         : "
                f"{datos.get('localidad')}"
            )

            print(
                f"Provincia         : "
                f"{datos.get('provincia')}"
            )

            print(
                f"Tipo              : "
                f"{datos.get('tipo')}"
            )

            print(
                f"Versión           : "
                f"{datos.get('version')}"
            )

            print(
                f"Fecha de emisión  : "
                f"{datos.get('fecha_emision')}"
            )

            print(
                f"Fecha vencimiento : "
                f"{datos.get('fecha_vencimiento')}"
            )

            print(
                f"Huella del equipo : "
                f"{datos.get('huella_equipo')}"
            )

    else:

        print(
            "LICENCIA INVÁLIDA ❌"
        )

        print()

        print(
            f"Motivo técnico: {motivo}"
        )

    print()
