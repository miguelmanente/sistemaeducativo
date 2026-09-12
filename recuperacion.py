# ============================================================
# recuperacion.py
# Sistema de Gestión Educativa (SGE)
#
# Responsabilidad:
#   - Crear el archivo de recuperación de la clave de datos.
#   - Proteger la clave de datos mediante una frase de recuperación.
#   - Recuperar la clave de datos utilizando dicha frase.
#   - Permitir utilizar un archivo de recuperación externo.
#
# IMPORTANTE:
#   - La frase de recuperación NUNCA se guarda.
#   - Este módulo NO administra Windows DPAPI.
#   - Este módulo NO cifra backups.
#   - Este módulo NO restaura bases de datos.
#
# ============================================================

import os
import sys
import json
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from seguridad import obtener_clave_datos


# ============================================================
# UBICACIÓN BASE
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# ARCHIVO DE RECUPERACIÓN PREDETERMINADO
# ============================================================

CARPETA_SEGURIDAD = os.path.join(BASE_DIR, "seguridad")

NOMBRE_ARCHIVO_RECUPERACION = "recuperacion_sge.json"

RUTA_RECUPERACION = os.path.join(
    CARPETA_SEGURIDAD,
    NOMBRE_ARCHIVO_RECUPERACION
)


# ============================================================
# PARÁMETROS DE SCRYPT
# ============================================================

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1

LONGITUD_SALT = 16


# ============================================================
# DERIVAR CLAVE DESDE LA FRASE DE RECUPERACIÓN
# ============================================================

def derivar_clave_recuperacion(frase_recuperacion, salt):
    """
    Deriva una clave criptográfica a partir de la frase
    de recuperación utilizando Scrypt.
    """

    if not isinstance(frase_recuperacion, str):
        raise TypeError(
            "La frase de recuperación debe ser texto."
        )

    if not frase_recuperacion.strip():
        raise ValueError(
            "La frase de recuperación no puede estar vacía."
        )

    if not isinstance(salt, bytes):
        raise TypeError(
            "El salt debe ser de tipo bytes."
        )

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P
    )

    clave = kdf.derive(
        frase_recuperacion.encode("utf-8")
    )

    return base64.urlsafe_b64encode(clave)


# ============================================================
# CREAR ARCHIVO DE RECUPERACIÓN
# ============================================================

def crear_archivo_recuperacion(
    frase_recuperacion,
    ruta_destino=None
):
    """
    Crea un archivo de recuperación para la clave de datos.

    Si no se indica una ruta:
        utiliza la ubicación predeterminada del SGE.

    Si se indica una ruta:
        guarda allí el archivo de recuperación.

    La frase de recuperación NO se guarda.
    """

    if ruta_destino is None:
        ruta_destino = RUTA_RECUPERACION

    if not isinstance(ruta_destino, str):
        raise TypeError(
            "La ruta del archivo de recuperación debe ser texto."
        )

    if not ruta_destino.strip():
        raise ValueError(
            "La ruta del archivo de recuperación no puede estar vacía."
        )

    # --------------------------------------------------------
    # Obtener la clave de datos real del SGE
    # --------------------------------------------------------

    clave_datos = obtener_clave_datos()

    if not isinstance(clave_datos, bytes):
        raise TypeError(
            "La clave de datos no es de tipo bytes."
        )

    if len(clave_datos) != 32:
        raise ValueError(
            "La clave de datos debe tener exactamente 32 bytes."
        )

    # --------------------------------------------------------
    # Crear salt aleatorio
    # --------------------------------------------------------

    salt = os.urandom(LONGITUD_SALT)

    # --------------------------------------------------------
    # Derivar clave desde la frase
    # --------------------------------------------------------

    clave_recuperacion = derivar_clave_recuperacion(
        frase_recuperacion,
        salt
    )

    # --------------------------------------------------------
    # Cifrar la clave de datos
    # --------------------------------------------------------

    fernet = Fernet(clave_recuperacion)

    datos_cifrados = fernet.encrypt(clave_datos)

    # --------------------------------------------------------
    # Construir información del archivo
    # --------------------------------------------------------

    datos_recuperacion = {
        "version": 1,
        "algoritmo": "scrypt_fernet",
        "salt": base64.b64encode(salt).decode("ascii"),
        "scrypt": {
            "n": SCRYPT_N,
            "r": SCRYPT_R,
            "p": SCRYPT_P
        },
        "clave_datos_cifrada": datos_cifrados.decode("ascii")
    }

    # --------------------------------------------------------
    # Crear carpeta de destino si corresponde
    # --------------------------------------------------------

    carpeta_destino = os.path.dirname(
        os.path.abspath(ruta_destino)
    )

    if carpeta_destino:
        os.makedirs(
            carpeta_destino,
            exist_ok=True
        )

    # --------------------------------------------------------
    # Nunca sobrescribir automáticamente
    # --------------------------------------------------------

    if os.path.exists(ruta_destino):
        raise FileExistsError(
            "Ya existe un archivo de recuperación del SGE:\n\n"
            f"{ruta_destino}\n\n"
            "No se sobrescribirá automáticamente."
        )

    # --------------------------------------------------------
    # Escritura atómica
    # --------------------------------------------------------

    ruta_temporal = ruta_destino + ".tmp"

    try:

        with open(
            ruta_temporal,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                datos_recuperacion,
                archivo,
                indent=4
            )

            archivo.flush()
            os.fsync(archivo.fileno())

        os.replace(
            ruta_temporal,
            ruta_destino
        )

    except Exception:

        try:

            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)

        except OSError:
            pass

        raise

    return ruta_destino


# ============================================================
# RECUPERAR CLAVE DE DATOS
# ============================================================

def recuperar_clave_datos(
    frase_recuperacion,
    ruta_archivo=None
):
    """
    Recupera la clave de datos utilizando:

        1. la frase de recuperación
        2. el archivo de recuperación

    Si no se indica una ruta:
        utiliza RUTA_RECUPERACION.

    Esto mantiene compatibilidad con el funcionamiento
    anterior del módulo.
    """

    if ruta_archivo is None:
        ruta_archivo = RUTA_RECUPERACION

    if not isinstance(ruta_archivo, str):
        raise TypeError(
            "La ruta del archivo de recuperación debe ser texto."
        )

    if not ruta_archivo.strip():
        raise ValueError(
            "La ruta del archivo de recuperación no puede estar vacía."
        )

    # --------------------------------------------------------
    # Verificar existencia
    # --------------------------------------------------------

    if not os.path.isfile(ruta_archivo):
        raise FileNotFoundError(
            "No existe el archivo de recuperación del SGE:\n\n"
            f"{ruta_archivo}"
        )

    # --------------------------------------------------------
    # Leer archivo
    # --------------------------------------------------------

    try:

        with open(
            ruta_archivo,
            "r",
            encoding="utf-8"
        ) as archivo:

            datos_recuperacion = json.load(archivo)

    except json.JSONDecodeError as error:

        raise ValueError(
            "El archivo de recuperación no contiene "
            "un formato JSON válido."
        ) from error

    # --------------------------------------------------------
    # Verificar versión
    # --------------------------------------------------------

    if datos_recuperacion.get("version") != 1:

        raise ValueError(
            "La versión del archivo de recuperación "
            "no es compatible."
        )

    # --------------------------------------------------------
    # Recuperar salt
    # --------------------------------------------------------

    try:

        salt = base64.b64decode(
            datos_recuperacion["salt"]
        )

    except Exception as error:

        raise ValueError(
            "El salt del archivo de recuperación "
            "no es válido."
        ) from error

    if len(salt) != LONGITUD_SALT:

        raise ValueError(
            "El salt del archivo de recuperación "
            "tiene un tamaño inválido."
        )

    # --------------------------------------------------------
    # Recuperar parámetros de Scrypt
    # --------------------------------------------------------

    parametros = datos_recuperacion.get("scrypt")

    if not isinstance(parametros, dict):

        raise ValueError(
            "Faltan los parámetros de Scrypt."
        )

    n = parametros.get("n")
    r = parametros.get("r")
    p = parametros.get("p")

    if not all(
        isinstance(valor, int)
        for valor in (n, r, p)
    ):

        raise ValueError(
            "Los parámetros de Scrypt no son válidos."
        )

    if n <= 1 or (n & (n - 1)) != 0:
        raise ValueError(
            "El parámetro N de Scrypt no es válido."
        )

    if r <= 0 or p <= 0:
        raise ValueError(
            "Los parámetros R y P de Scrypt no son válidos."
        )

    # --------------------------------------------------------
    # Validar frase
    # --------------------------------------------------------

    if not isinstance(frase_recuperacion, str):

        raise TypeError(
            "La frase de recuperación debe ser texto."
        )

    if not frase_recuperacion.strip():

        raise ValueError(
            "La frase de recuperación no puede estar vacía."
        )

    # --------------------------------------------------------
    # Derivar clave
    # --------------------------------------------------------

    kdf = Scrypt(
        salt=salt,
        length=32,
        n=n,
        r=r,
        p=p
    )

    clave_derivada = kdf.derive(
        frase_recuperacion.encode("utf-8")
    )

    clave_fernet = base64.urlsafe_b64encode(
        clave_derivada
    )

    # --------------------------------------------------------
    # Crear Fernet
    # --------------------------------------------------------

    fernet = Fernet(clave_fernet)

    # --------------------------------------------------------
    # Obtener clave de datos cifrada
    # --------------------------------------------------------

    token = datos_recuperacion.get(
        "clave_datos_cifrada"
    )

    if not token:

        raise ValueError(
            "El archivo de recuperación no contiene "
            "la clave de datos cifrada."
        )

    # --------------------------------------------------------
    # Descifrar
    # --------------------------------------------------------

    try:

        clave_datos = fernet.decrypt(
            token.encode("ascii")
        )

    except Exception as error:

        raise ValueError(
            "No fue posible recuperar la clave de datos.\n\n"
            "La frase de recuperación puede ser incorrecta "
            "o el archivo de recuperación puede estar dañado."
        ) from error

    # --------------------------------------------------------
    # Verificación final
    # --------------------------------------------------------

    if len(clave_datos) != 32:

        raise ValueError(
            "La clave recuperada no tiene exactamente "
            "32 bytes."
        )

    return clave_datos


# ============================================================
# VERIFICAR ARCHIVO DE RECUPERACIÓN
# ============================================================

def verificar_archivo_recuperacion(
    frase_recuperacion,
    ruta_archivo=None
):
    """
    Verifica que el archivo de recuperación pueda utilizarse
    para recuperar una clave de datos válida.
    """

    try:

        clave = recuperar_clave_datos(
            frase_recuperacion,
            ruta_archivo
        )

        return (
            isinstance(clave, bytes)
            and len(clave) == 32
        )

    except Exception:

        return False


# ============================================================
# PRUEBA DIRECTA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print("PRUEBA DEL MÓDULO recuperacion.py")
    print("=" * 80)

    try:

        print()
        print("Archivo de recuperación predeterminado:")
        print(RUTA_RECUPERACION)

        print()
        print("Obteniendo clave de datos...")
        clave_original = obtener_clave_datos()

        print("Clave de datos obtenida correctamente.")
        print("Bytes:", len(clave_original))

        print()
        print(
            "Ingrese la frase de recuperación "
            "para verificar el archivo existente."
        )

        frase = input("Frase de recuperación: ")

        print()
        print("Intentando recuperar la clave de datos...")

        clave_recuperada = recuperar_clave_datos(
            frase,
            RUTA_RECUPERACION
        )

        print()

        if clave_recuperada == clave_original:

            print("✅ RECUPERACIÓN EXITOSA.")
            print()
            print(
                "La clave recuperada es idéntica "
                "a la clave original."
            )
            print()
            print("Bytes:", len(clave_recuperada))

        else:

            print(
                "❌ ERROR: las claves no coinciden."
            )

        print()
        print("=" * 80)
        print("PRUEBA FINALIZADA")
        print("=" * 80)

    except Exception as error:

        print()
        print("❌ ERROR")
        print()
        print(str(error))
        print()
        print("=" * 80)


