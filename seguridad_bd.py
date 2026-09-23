# =====================================================
#             SEGURIDAD DE LA BASE DE DATOS
#                         SGE
# =====================================================

import os
import sys
import secrets
import ctypes
import ctypes.wintypes


# =====================================================
#                  RUTAS DEL SGE
# =====================================================

def obtener_ruta_datos():
    """
    Devuelve la carpeta donde estarán los datos
    del SGE.

    Durante el desarrollo se utiliza una ubicación
    dentro del proyecto.

    En la versión instalada se utilizará:

        C:\\ProgramData\\SGE\\Datos
    """

    if getattr(sys, "frozen", False):

        base = os.environ.get(
            "PROGRAMDATA",
            os.path.expanduser("~")
        )

        return os.path.join(
            base,
            "SGE",
            "Datos"
        )

    else:

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

        return os.path.join(
            base,
            "Datos"
        )


def obtener_ruta_seguridad():
    """
    Devuelve la carpeta donde se almacenan
    los elementos de seguridad del SGE.

    Durante el desarrollo:

        Proyecto\\Seguridad

    En la versión instalada:

        C:\\ProgramData\\SGE\\Seguridad
    """

    if getattr(sys, "frozen", False):

        base = os.environ.get(
            "PROGRAMDATA",
            os.path.expanduser("~")
        )

        return os.path.join(
            base,
            "SGE",
            "Seguridad"
        )

    else:

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

        return os.path.join(
            base,
            "Seguridad"
        )


def obtener_ruta_clave():
    """
    Devuelve la ruta donde se almacena
    la clave de la base de datos protegida
    mediante Windows DPAPI.
    """

    return os.path.join(
        obtener_ruta_seguridad(),
        "clave_bd.protegida"
    )


def obtener_ruta_recuperacion():
    """
    Devuelve la ruta donde se almacena
    el archivo de recuperación.

    La gestión criptográfica del archivo
    corresponde al módulo recuperacion.py.
    """

    return os.path.join(
        obtener_ruta_seguridad(),
        "recuperacion.dat"
    )


# =====================================================
#                  WINDOWS DATA BLOB
# =====================================================

class DATA_BLOB(ctypes.Structure):

    _fields_ = [
        (
            "cbData",
            ctypes.wintypes.DWORD
        ),
        (
            "pbData",
            ctypes.POINTER(
                ctypes.c_byte
            )
        )
    ]


# =====================================================
#                  PROTEGER CON DPAPI
# =====================================================

def _proteger_dpapi(dato):
    """
    Protege datos utilizando Windows DPAPI.

    La protección queda vinculada al contexto
    de Windows de esta instalación.
    """

    buffer = ctypes.create_string_buffer(
        dato
    )

    entrada = DATA_BLOB(
        len(dato),
        ctypes.cast(
            buffer,
            ctypes.POINTER(
                ctypes.c_byte
            )
        )
    )

    salida = DATA_BLOB()

    resultado = (
        ctypes.windll.crypt32.CryptProtectData(
            ctypes.byref(entrada),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(salida)
        )
    )

    if not resultado:

        raise RuntimeError(
            "Windows no pudo proteger "
            "la clave de la base de datos."
        )

    datos_protegidos = ctypes.string_at(
        salida.pbData,
        salida.cbData
    )

    ctypes.windll.kernel32.LocalFree(
        salida.pbData
    )

    return datos_protegidos


# =====================================================
#                  RECUPERAR CON DPAPI
# =====================================================

def _recuperar_dpapi(datos_protegidos):
    """
    Recupera datos protegidos mediante
    Windows DPAPI.
    """

    buffer = ctypes.create_string_buffer(
        datos_protegidos
    )

    entrada = DATA_BLOB(
        len(datos_protegidos),
        ctypes.cast(
            buffer,
            ctypes.POINTER(
                ctypes.c_byte
            )
        )
    )

    salida = DATA_BLOB()

    resultado = (
        ctypes.windll.crypt32.CryptUnprotectData(
            ctypes.byref(entrada),
            None,
            None,
            None,
            None,
            0,
            ctypes.byref(salida)
        )
    )

    if not resultado:

        raise RuntimeError(
            "Windows no pudo recuperar "
            "la clave de la base de datos."
        )

    dato_original = ctypes.string_at(
        salida.pbData,
        salida.cbData
    )

    ctypes.windll.kernel32.LocalFree(
        salida.pbData
    )

    return dato_original


# =====================================================
#              GENERAR CLAVE DE LA BD
# =====================================================

def generar_clave_bd():
    """
    Genera una clave criptográfica aleatoria
    de 256 bits.

    Esta clave será utilizada posteriormente
    por SQLCipher para cifrar la base de datos.
    """

    return secrets.token_bytes(32)


# =====================================================
#              CREAR Y GUARDAR CLAVE
# =====================================================

def crear_clave_bd():
    """
    Genera una nueva clave para la BD y la
    almacena protegida mediante Windows DPAPI.

    Devuelve la clave original en memoria.

    Esta función debe utilizarse solamente durante
    la creación inicial de una instalación.

    Si ya existe una clave, no genera otra.
    """

    ruta_seguridad = (
        obtener_ruta_seguridad()
    )

    os.makedirs(
        ruta_seguridad,
        exist_ok=True
    )

    ruta_clave = (
        obtener_ruta_clave()
    )

    if os.path.exists(ruta_clave):

        raise FileExistsError(
            "Ya existe una clave de base "
            "de datos para esta instalación."
        )

    clave = generar_clave_bd()

    clave_protegida = _proteger_dpapi(
        clave
    )

    with open(
        ruta_clave,
        "wb"
    ) as archivo:

        archivo.write(
            clave_protegida
        )

    return clave


# =====================================================
#              OBTENER CLAVE DE LA BD
# =====================================================

def obtener_clave_bd():
    """
    Recupera la clave de la base de datos
    mediante Windows DPAPI.

    Si la clave no existe, genera un error.

    No crea automáticamente una clave nueva,
    porque eso podría provocar la pérdida de
    acceso a una BD existente.

    La recuperación de emergencia NO se realiza
    desde este módulo.

    Para recuperación se utiliza:

        recuperacion.py
    """

    ruta_clave = (
        obtener_ruta_clave()
    )

    if not os.path.exists(
        ruta_clave
    ):

        raise FileNotFoundError(
            "No existe la clave protegida "
            "de la base de datos."
        )

    with open(
        ruta_clave,
        "rb"
    ) as archivo:

        clave_protegida = (
            archivo.read()
        )

    if not clave_protegida:

        raise RuntimeError(
            "El archivo de clave está vacío."
        )

    clave = _recuperar_dpapi(
        clave_protegida
    )

    if len(clave) != 32:

        raise RuntimeError(
            "La clave recuperada no tiene "
            "el tamaño esperado."
        )

    return clave


# =====================================================
#                     FIN DEL MÓDULO
# =====================================================