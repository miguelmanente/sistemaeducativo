# ============================================================
# seguridad.py
# Sistema de Gestión Educativa (SGE)
#
# Responsabilidad:
#   - Generar la clave de datos del SGE
#   - Protegerla mediante Windows DPAPI
#   - Recuperarla cuando el SGE vuelve a ejecutarse
#   - Verificar que la clave sea válida
#
# IMPORTANTE:
#   Este módulo NO cifra backups.
#   Este módulo NO restaura bases de datos.
#   Este módulo NO maneja ventanas Tkinter.
#
#   Su única responsabilidad es administrar la CLAVE DE DATOS.
# ============================================================

import os
import sys
import secrets
import ctypes
from ctypes import wintypes


# ============================================================
# CONFIGURACIÓN
# ============================================================

NOMBRE_ARCHIVO_CLAVE = "clave_datos_sge.protegida"

# Por ahora utilizamos una carpeta "seguridad" junto al programa.
# Más adelante podremos llevarla a una ubicación específica de
# datos de aplicación de Windows.
#
# Si SGE está convertido en .exe:
#     se toma la carpeta donde está el .exe
#
# Si estamos ejecutando Python:
#     se toma la carpeta donde está este módulo.
#
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


CARPETA_SEGURIDAD = os.path.join(BASE_DIR, "seguridad")


# ============================================================
# WINDOWS DPAPI
# ============================================================

# DPAPI pertenece a Windows.
#
# Estas DLL permiten acceder a:
#
# crypt32.dll
#     CryptProtectData
#     CryptUnprotectData
#
# kernel32.dll
#     LocalFree
#
if os.name == "nt":
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
else:
    crypt32 = None
    kernel32 = None


# ============================================================
# ESTRUCTURA DATA_BLOB
# ============================================================

class DATA_BLOB(ctypes.Structure):
    """
    Estructura utilizada por Windows DPAPI.

    cbData:
        cantidad de bytes

    pbData:
        puntero a los datos
    """

    _fields_ = [
        ("cbData", wintypes.DWORD),
        (
            "pbData",
            ctypes.POINTER(ctypes.c_byte)
        )
    ]


# ============================================================
# CONFIGURACIÓN DE LAS FUNCIONES DE WINDOWS
# ============================================================

if os.name == "nt":

    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        wintypes.LPCWSTR,
        ctypes.POINTER(DATA_BLOB),
        wintypes.LPVOID,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB)
    ]

    crypt32.CryptProtectData.restype = wintypes.BOOL


    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(DATA_BLOB),
        wintypes.LPVOID,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB)
    ]

    crypt32.CryptUnprotectData.restype = wintypes.BOOL


    kernel32.LocalFree.argtypes = [
        ctypes.c_void_p
    ]

    kernel32.LocalFree.restype = ctypes.c_void_p


# ============================================================
# COMPROBAR WINDOWS
# ============================================================

def _comprobar_windows():
    """
    Verifica que el sistema operativo sea Windows.

    DPAPI utilizada por este módulo pertenece a Windows.
    """

    if os.name != "nt":
        raise RuntimeError(
            "El módulo seguridad.py requiere Windows "
            "porque utiliza Windows DPAPI."
        )


# ============================================================
# OBTENER RUTA DE LA CLAVE PROTEGIDA
# ============================================================

def obtener_ruta_clave():
    """
    Devuelve la ruta completa donde se almacena
    la clave de datos protegida.

    No crea todavía ningún archivo.
    """

    return os.path.join(
        CARPETA_SEGURIDAD,
        NOMBRE_ARCHIVO_CLAVE
    )


# ============================================================
# CONVERTIR BYTES PYTHON A DATA_BLOB
# ============================================================

def _crear_blob(datos):
    """
    Convierte bytes de Python en un DATA_BLOB
    que pueda utilizar Windows DPAPI.

    Devuelve:

        blob
        buffer

    El buffer debe mantenerse vivo mientras Windows
    esté utilizando el blob.
    """

    buffer = ctypes.create_string_buffer(datos)

    blob = DATA_BLOB(
        len(datos),
        ctypes.cast(
            buffer,
            ctypes.POINTER(ctypes.c_byte)
        )
    )

    return blob, buffer


# ============================================================
# PROTEGER DATOS CON DPAPI
# ============================================================

def proteger_clave_dpapi(clave_datos):
    """
    Protege la clave de datos utilizando Windows DPAPI.

    Recibe:
        clave_datos -> bytes

    Devuelve:
        bytes protegidos

    La clave original NO se guarda directamente en disco.
    """

    _comprobar_windows()

    if not isinstance(clave_datos, bytes):
        raise TypeError(
            "La clave de datos debe ser de tipo bytes."
        )

    if len(clave_datos) != 32:
        raise ValueError(
            "La clave de datos debe tener exactamente "
            "32 bytes."
        )

    entrada, buffer_entrada = _crear_blob(clave_datos)

    salida = DATA_BLOB()

    resultado = crypt32.CryptProtectData(
        ctypes.byref(entrada),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(salida)
    )

    if not resultado:
        raise ctypes.WinError(
            ctypes.get_last_error()
        )

    try:

        datos_protegidos = ctypes.string_at(
            salida.pbData,
            salida.cbData
        )

    finally:

        # Windows reservó memoria para la salida.
        # Debemos liberarla.
        kernel32.LocalFree(
            salida.pbData
        )

    return datos_protegidos


# ============================================================
# RECUPERAR DATOS CON DPAPI
# ============================================================

def recuperar_clave_dpapi(datos_protegidos):
    """
    Recupera la clave original utilizando Windows DPAPI.

    Recibe:
        datos_protegidos -> bytes

    Devuelve:
        clave original -> bytes
    """

    _comprobar_windows()

    if not isinstance(datos_protegidos, bytes):
        raise TypeError(
            "Los datos protegidos deben ser de tipo bytes."
        )

    if not datos_protegidos:
        raise ValueError(
            "Los datos protegidos están vacíos."
        )

    entrada, buffer_entrada = _crear_blob(
        datos_protegidos
    )

    salida = DATA_BLOB()

    resultado = crypt32.CryptUnprotectData(
        ctypes.byref(entrada),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(salida)
    )

    if not resultado:
        raise ctypes.WinError(
            ctypes.get_last_error()
        )

    try:

        clave_recuperada = ctypes.string_at(
            salida.pbData,
            salida.cbData
        )

    finally:

        # Liberamos la memoria reservada por Windows.
        kernel32.LocalFree(
            salida.pbData
        )

    return clave_recuperada


# ============================================================
# GUARDAR CLAVE PROTEGIDA
# ============================================================

def _guardar_clave_protegida(datos_protegidos):
    """
    Guarda en disco únicamente la versión protegida
    de la clave.

    Se utiliza un archivo temporal y luego os.replace()
    para evitar dejar un archivo incompleto si el proceso
    se interrumpe durante la escritura.
    """

    os.makedirs(
        CARPETA_SEGURIDAD,
        exist_ok=True
    )

    ruta = obtener_ruta_clave()

    ruta_temporal = ruta + ".tmp"

    try:

        with open(
            ruta_temporal,
            "wb"
        ) as archivo:

            archivo.write(datos_protegidos)

            archivo.flush()

            os.fsync(
                archivo.fileno()
            )

        os.replace(
            ruta_temporal,
            ruta
        )

    except Exception:

        # Si quedó un temporal incompleto,
        # intentamos eliminarlo.
        try:

            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)

        except OSError:
            pass

        raise


# ============================================================
# LEER CLAVE PROTEGIDA
# ============================================================

def _leer_clave_protegida():
    """
    Lee del disco la clave protegida.

    NO devuelve la clave original.
    Devuelve únicamente los datos protegidos
    por DPAPI.
    """

    ruta = obtener_ruta_clave()

    if not os.path.exists(ruta):
        raise FileNotFoundError(
            "No existe el archivo de protección de "
            "la clave de datos:\n\n"
            f"{ruta}"
        )

    with open(
        ruta,
        "rb"
    ) as archivo:

        datos_protegidos = archivo.read()

    if not datos_protegidos:
        raise ValueError(
            "El archivo de la clave protegida está vacío."
        )

    return datos_protegidos


# ============================================================
# GENERAR CLAVE DE DATOS
# ============================================================

def generar_clave_datos():
    """
    Genera una nueva clave de datos de 256 bits.

    IMPORTANTE:
        Esta función genera una clave NUEVA.

    No debe utilizarse para reemplazar automáticamente
    una clave existente.
    """

    return secrets.token_bytes(32)


# ============================================================
# OBTENER CLAVE DE DATOS
# ============================================================

def obtener_clave_datos():
    """
    Obtiene la clave de datos estable del SGE.

    Comportamiento:

    1. Si la clave protegida NO existe:
         - genera una nueva clave
         - la protege con DPAPI
         - la guarda
         - devuelve la clave original

    2. Si la clave protegida YA existe:
         - la lee
         - la recupera mediante DPAPI
         - verifica que tenga 32 bytes
         - devuelve la misma clave

    IMPORTANTE:
        Si existe la clave pero no puede recuperarse,
        NO se genera otra automáticamente.

        Esto es fundamental porque los backups anteriores
        dependen de la clave original.
    """

    _comprobar_windows()

    ruta = obtener_ruta_clave()

    # --------------------------------------------------------
    # PRIMERA INSTALACIÓN
    # --------------------------------------------------------

    if not os.path.exists(ruta):

        clave_datos = generar_clave_datos()

        datos_protegidos = proteger_clave_dpapi(
            clave_datos
        )

        _guardar_clave_protegida(
            datos_protegidos
        )

        return clave_datos

    # --------------------------------------------------------
    # INSTALACIÓN EXISTENTE
    # --------------------------------------------------------

    datos_protegidos = _leer_clave_protegida()

    try:

        clave_datos = recuperar_clave_dpapi(
            datos_protegidos
        )

    except Exception as error:

        raise RuntimeError(
            "No fue posible recuperar la clave de datos "
            "del SGE mediante Windows DPAPI.\n\n"
            "IMPORTANTE: no se generará una clave nueva "
            "porque eso impediría utilizar los backups "
            "cifrados anteriormente."
        ) from error

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------

    if len(clave_datos) != 32:

        raise ValueError(
            "La clave recuperada no tiene exactamente "
            "32 bytes. La protección de seguridad no es válida."
        )

    return clave_datos


# ============================================================
# VERIFICAR CLAVE DE DATOS
# ============================================================

def verificar_clave_datos():
    """
    Verifica que:

        - exista el archivo protegido
        - pueda recuperarse mediante DPAPI
        - la clave tenga 32 bytes

    Devuelve:

        True  -> todo correcto
        False -> existe algún problema

    Esta función será útil posteriormente para mostrar
    el estado de seguridad en la interfaz del SGE.
    """

    try:

        _comprobar_windows()

        ruta = obtener_ruta_clave()

        if not os.path.exists(ruta):
            return False

        clave = obtener_clave_datos()

        if len(clave) != 32:
            return False

        return True

    except Exception:

        return False


# ============================================================
# PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBA DEL MÓDULO seguridad.py")
    print("=" * 60)

    try:

        print()
        print("📁 Carpeta de seguridad:")
        print(CARPETA_SEGURIDAD)

        print()
        print("🔐 Archivo de clave protegida:")
        print(obtener_ruta_clave())

        print()
        print("🔑 Obteniendo clave de datos...")

        clave = obtener_clave_datos()

        print("✅ Clave obtenida correctamente.")

        print()
        print("Cantidad de bytes:", len(clave))
        print("Cantidad de bits:", len(clave) * 8)

        print()
        print("🛡️ Verificando clave...")

        if verificar_clave_datos():

            print("✅ VERIFICACIÓN EXITOSA.")
            print()
            print("La clave de datos del SGE:")
            print("   ✔ existe")
            print("   ✔ está protegida mediante DPAPI")
            print("   ✔ puede recuperarse")
            print("   ✔ tiene 32 bytes")
            print("   ✔ puede utilizarse para cifrado")

        else:

            print("❌ La verificación de seguridad falló.")

        print()
        print("=" * 60)
        print("PRUEBA FINALIZADA")
        print("=" * 60)

    except Exception as error:

        print()
        print("❌ ERROR")
        print()
        print(str(error))
        print()
        print("=" * 60)


