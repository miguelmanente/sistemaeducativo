# =====================================================
#              SEGURIDAD DE LA BASE DE DATOS
#                         SGE
# =====================================================

import os
import secrets
import ctypes
import ctypes.wintypes

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# =====================================================
#                  RUTAS DEL SGE
# =====================================================

def obtener_ruta_datos():

    """
    Devuelve la carpeta donde estarán los datos
    del SGE.

    Durante el desarrollo utilizamos una ubicación
    dentro del proyecto.

    En la versión instalada se utilizará:

        C:\ProgramData\SGE\Datos
    """

    if getattr(
        __import__("sys"),
        "frozen",
        False
    ):

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
    """

    if getattr(
        __import__("sys"),
        "frozen",
        False
    ):

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

    return os.path.join(
        obtener_ruta_seguridad(),
        "clave_bd.protegida"
    )


def obtener_ruta_recuperacion():

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

def _recuperar_dpapi(
    datos_protegidos
):

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
    """

    return secrets.token_bytes(32)


# =====================================================
#             CREAR Y GUARDAR CLAVE
# =====================================================

def crear_clave_bd():

    """
    Genera una nueva clave para la BD y la
    almacena protegida mediante Windows DPAPI.

    Devuelve la clave original en memoria.

    Esta función debe utilizarse solamente durante
    la creación inicial de la instalación.
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
#             DERIVAR CLAVE DE RECUPERACIÓN
# =====================================================

def derivar_clave_recuperacion(
    contrasena,
    salt
):

    """
    Deriva una clave criptográfica a partir
    de una contraseña de recuperación.

    PBKDF2-SHA256 se utiliza para evitar que
    la contraseña sea utilizada directamente
    como clave AES.
    """

    if not contrasena:

        raise ValueError(
            "La contraseña de recuperación "
            "no puede estar vacía."
        )

    if not salt:

        raise ValueError(
            "El salt no puede estar vacío."
        )

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000
    )

    return kdf.derive(
        contrasena.encode("utf-8")
    )


# =====================================================
#           CREAR ARCHIVO DE RECUPERACIÓN
# =====================================================

def crear_recuperacion(
    clave_bd,
    contrasena
):

    """
    Crea el archivo de recuperación de la
    clave de la base de datos.

    El archivo NO contiene la clave de la BD
    en texto plano.

    Contiene:

        SALT
        +
        NONCE
        +
        CLAVE DE BD CIFRADA
    """

    if len(clave_bd) != 32:

        raise ValueError(
            "La clave de BD debe tener "
            "256 bits."
        )

    if not contrasena:

        raise ValueError(
            "La contraseña de recuperación "
            "no puede estar vacía."
        )

    ruta_seguridad = (
        obtener_ruta_seguridad()
    )

    os.makedirs(
        ruta_seguridad,
        exist_ok=True
    )

    ruta_recuperacion = (
        obtener_ruta_recuperacion()
    )

    if os.path.exists(
        ruta_recuperacion
    ):

        raise FileExistsError(
            "Ya existe un archivo "
            "de recuperación."
        )

    salt = secrets.token_bytes(
        16
    )

    clave_recuperacion = (
        derivar_clave_recuperacion(
            contrasena,
            salt
        )
    )

    nonce = secrets.token_bytes(
        12
    )

    aes = AESGCM(
        clave_recuperacion
    )

    clave_cifrada = aes.encrypt(
        nonce,
        clave_bd,
        None
    )

    with open(
        ruta_recuperacion,
        "wb"
    ) as archivo:

        archivo.write(
            salt
        )

        archivo.write(
            nonce
        )

        archivo.write(
            clave_cifrada
        )


# =====================================================
#           RECUPERAR CLAVE DE LA BD
# =====================================================

def recuperar_clave_bd(
    contrasena
):

    """
    Recupera la clave de la BD utilizando
    el archivo de recuperación y la contraseña
    correspondiente.
    """

    ruta_recuperacion = (
        obtener_ruta_recuperacion()
    )

    if not os.path.exists(
        ruta_recuperacion
    ):

        raise FileNotFoundError(
            "No existe el archivo "
            "de recuperación."
        )

    with open(
        ruta_recuperacion,
        "rb"
    ) as archivo:

        contenido = archivo.read()

    if len(contenido) < 29:

        raise RuntimeError(
            "El archivo de recuperación "
            "está incompleto o dañado."
        )

    salt = contenido[
        0:16
    ]

    nonce = contenido[
        16:28
    ]

    clave_cifrada = contenido[
        28:
    ]

    clave_recuperacion = (
        derivar_clave_recuperacion(
            contrasena,
            salt
        )
    )

    aes = AESGCM(
        clave_recuperacion
    )

    try:

        clave_bd = aes.decrypt(
            nonce,
            clave_cifrada,
            None
        )

    except Exception as error:

        raise ValueError(
            "No fue posible recuperar "
            "la clave de la BD. "
            "La contraseña puede ser "
            "incorrecta o el archivo "
            "puede estar dañado."
        ) from error

    if len(clave_bd) != 32:

        raise RuntimeError(
            "La clave recuperada "
            "no tiene un tamaño válido."
        )

    return clave_bd


# =====================================================
#                 FIN DEL MÓDULO
# =====================================================