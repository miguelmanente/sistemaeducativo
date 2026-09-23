# ============================================================
#                 RECUPERACIÓN DE LA CLAVE DEL SGE
# ============================================================
#
# Este módulo permite recuperar la clave de cifrado de la
# base de datos cuando el mecanismo normal de Windows
# (DPAPI) no puede utilizarse.
#
# IMPORTANTE:
#
# - No genera una nueva clave de base de datos.
# - No guarda la clave de BD en texto plano.
# - No reemplaza la protección DPAPI.
# - Utiliza un mecanismo independiente de recuperación.
#
# Flujo:
#
# contraseña
#      ↓
# PBKDF2-HMAC-SHA256
#      ↓
# clave de recuperación
#      ↓
# AES-GCM
#      ↓
# CLAVE_BD cifrada
#
# ============================================================


# ------------------------ LIBRERÍAS --------------------------

import os
import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# ------------------------ RUTA DE RECUPERACIÓN ---------------

from seguridad_bd import obtener_ruta_recuperacion


# ============================================================
#                    CONFIGURACIÓN CRIPTOGRÁFICA
# ============================================================

ITERACIONES = 600_000

TAMANIO_SALT = 16

TAMANIO_NONCE = 12

TAMANIO_CLAVE = 32


# ============================================================
#                 DERIVAR CLAVE DE RECUPERACIÓN
# ============================================================

def derivar_clave_recuperacion(contrasena, salt):
    """
    Convierte la contraseña de recuperación en una clave
    criptográfica de 32 bytes mediante PBKDF2-HMAC-SHA256.
    """

    if not isinstance(contrasena, str):
        raise TypeError(
            "La contraseña debe ser un texto."
        )

    if not contrasena:
        raise ValueError(
            "La contraseña de recuperación "
            "no puede estar vacía."
        )

    if not isinstance(salt, bytes):
        raise TypeError(
            "El salt debe ser de tipo bytes."
        )

    if len(salt) != TAMANIO_SALT:
        raise ValueError(
            "El salt tiene un tamaño incorrecto."
        )

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=TAMANIO_CLAVE,
        salt=salt,
        iterations=ITERACIONES
    )

    return kdf.derive(
        contrasena.encode("utf-8")
    )


# ============================================================
#                  CREAR ARCHIVO DE RECUPERACIÓN
# ============================================================

def crear_recuperacion(clave_bd, contrasena):
    """
    Crea el archivo recuperacion.dat.

    El archivo contiene:

        SALT
        NONCE
        CLAVE_BD CIFRADA

    La clave de BD nunca se guarda directamente.
    """

    # --------------------------------------------------------
    # VALIDAR CLAVE
    # --------------------------------------------------------

    if not isinstance(clave_bd, bytes):
        raise TypeError(
            "La clave de BD debe ser de tipo bytes."
        )

    if len(clave_bd) != TAMANIO_CLAVE:
        raise ValueError(
            "La clave de BD debe tener 32 bytes."
        )

    # --------------------------------------------------------
    # VALIDAR CONTRASEÑA
    # --------------------------------------------------------

    if not isinstance(contrasena, str):
        raise TypeError(
            "La contraseña debe ser de tipo texto."
        )

    if len(contrasena) < 8:
        raise ValueError(
            "La contraseña de recuperación debe tener "
            "al menos 8 caracteres."
        )

    # --------------------------------------------------------
    # GENERAR SALT
    # --------------------------------------------------------

    salt = os.urandom(
        TAMANIO_SALT
    )

    # --------------------------------------------------------
    # DERIVAR CLAVE
    # --------------------------------------------------------

    clave_recuperacion = derivar_clave_recuperacion(
        contrasena,
        salt
    )

    # --------------------------------------------------------
    # GENERAR NONCE
    # --------------------------------------------------------

    nonce = os.urandom(
        TAMANIO_NONCE
    )

    # --------------------------------------------------------
    # CIFRAR CLAVE DE BD
    # --------------------------------------------------------

    aes = AESGCM(
        clave_recuperacion
    )

    clave_bd_cifrada = aes.encrypt(
        nonce,
        clave_bd,
        None
    )

    # --------------------------------------------------------
    # CONSTRUIR ARCHIVO
    # --------------------------------------------------------
    #
    # Estructura:
    #
    # [16 bytes SALT]
    # [12 bytes NONCE]
    # [32 bytes CLAVE_BD cifrada]
    # [16 bytes TAG AES-GCM]
    #
    # AES-GCM agrega automáticamente el tag.
    #

    datos = (
        salt
        + nonce
        + clave_bd_cifrada
    )

    # --------------------------------------------------------
    # OBTENER RUTA
    # --------------------------------------------------------

    ruta = obtener_ruta_recuperacion()

    carpeta = os.path.dirname(ruta)

    os.makedirs(
        carpeta,
        exist_ok=True
    )

    # --------------------------------------------------------
    # EVITAR SOBRESCRIBIR RECUPERACIÓN EXISTENTE
    # --------------------------------------------------------

    if os.path.exists(ruta):

        raise FileExistsError(
            "Ya existe un archivo de recuperación. "
            "No se sobrescribirá automáticamente."
        )

    # --------------------------------------------------------
    # GUARDAR
    # --------------------------------------------------------

    with open(
        ruta,
        "wb"
    ) as archivo:

        archivo.write(
            datos
        )

    return ruta


# ============================================================
#                  RECUPERAR CLAVE DE BD
# ============================================================

def recuperar_clave_bd(contrasena):
    """
    Recupera la clave de la base de datos utilizando
    la contraseña de recuperación.

    Este proceso NO utiliza Windows DPAPI.

    Devuelve:

        clave_bd

    Si la contraseña es incorrecta o el archivo fue
    alterado, AES-GCM producirá un error.
    """

    # --------------------------------------------------------
    # OBTENER ARCHIVO
    # --------------------------------------------------------

    ruta = obtener_ruta_recuperacion()

    if not os.path.exists(ruta):

        raise FileNotFoundError(
            "No existe el archivo de recuperación."
        )

    # --------------------------------------------------------
    # LEER ARCHIVO
    # --------------------------------------------------------

    with open(
        ruta,
        "rb"
    ) as archivo:

        datos = archivo.read()

    # --------------------------------------------------------
    # COMPROBAR TAMAÑO MÍNIMO
    # --------------------------------------------------------

    minimo = (
        TAMANIO_SALT
        + TAMANIO_NONCE
        + TAMANIO_CLAVE
        + 16
    )

    if len(datos) < minimo:

        raise ValueError(
            "El archivo de recuperación está incompleto "
            "o tiene un formato inválido."
        )

    # --------------------------------------------------------
    # EXTRAER SALT
    # --------------------------------------------------------

    posicion = 0

    salt = datos[
        posicion:
        posicion + TAMANIO_SALT
    ]

    posicion += TAMANIO_SALT

    # --------------------------------------------------------
    # EXTRAER NONCE
    # --------------------------------------------------------

    nonce = datos[
        posicion:
        posicion + TAMANIO_NONCE
    ]

    posicion += TAMANIO_NONCE

    # --------------------------------------------------------
    # EXTRAER DATOS CIFRADOS
    # --------------------------------------------------------

    clave_bd_cifrada = datos[
        posicion:
    ]

    # --------------------------------------------------------
    # DERIVAR CLAVE DE RECUPERACIÓN
    # --------------------------------------------------------

    clave_recuperacion = derivar_clave_recuperacion(
        contrasena,
        salt
    )

    # --------------------------------------------------------
    # DESCIFRAR
    # --------------------------------------------------------

    aes = AESGCM(
        clave_recuperacion
    )

    try:

        clave_bd = aes.decrypt(
            nonce,
            clave_bd_cifrada,
            None
        )

    except Exception as error:

        raise ValueError(
            "No fue posible recuperar la clave de la BD. "
            "La contraseña puede ser incorrecta o el "
            "archivo puede estar dañado."
        ) from error

    # --------------------------------------------------------
    # VALIDAR CLAVE RECUPERADA
    # --------------------------------------------------------

    if len(clave_bd) != TAMANIO_CLAVE:

        raise ValueError(
            "La clave recuperada tiene un tamaño inválido."
        )

    return clave_bd


# ============================================================
#                  PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("PRUEBA DEL MÓDULO DE RECUPERACIÓN")
    print("=" * 65)

    try:

        # ----------------------------------------------------
        # OBTENER CLAVE ACTUAL
        # ----------------------------------------------------
        #
        # Esta llamada se utiliza únicamente para preparar
        # el archivo de recuperación durante la prueba.
        #
        # El proceso recuperar_clave_bd() NO depende de ella.
        #

        print()
        print("Obteniendo clave de la BD para la prueba...")

        from seguridad_bd import obtener_clave_bd

        clave_bd = obtener_clave_bd()

        print(
            "Clave obtenida correctamente."
        )

        print(
            f"Bytes: {len(clave_bd)}"
        )

        print(
            f"Bits: {len(clave_bd) * 8}"
        )

        # ----------------------------------------------------
        # INGRESAR CONTRASEÑA
        # ----------------------------------------------------

        print()
        print(
            "Ingrese una contraseña de recuperación."
        )

        print(
            "Para esta prueba debe tener al menos "
            "8 caracteres."
        )

        contrasena = getpass.getpass(
            "Contraseña: "
        )

        confirmacion = getpass.getpass(
            "Confirmar contraseña: "
        )

        if contrasena != confirmacion:

            raise ValueError(
                "Las contraseñas no coinciden."
            )

        # ----------------------------------------------------
        # CREAR RECUPERACIÓN
        # ----------------------------------------------------

        print()
        print(
            "Creando archivo de recuperación..."
        )

        ruta = crear_recuperacion(
            clave_bd,
            contrasena
        )

        print()
        print(
            "Archivo de recuperación creado:"
        )

        print(
            ruta
        )

        # ----------------------------------------------------
        # RECUPERAR
        # ----------------------------------------------------

        print()
        print(
            "Probando recuperación..."
        )

        clave_recuperada = recuperar_clave_bd(
            contrasena
        )

        print(
            "Clave recuperada correctamente."
        )

        # ----------------------------------------------------
        # COMPARAR CLAVES
        # ----------------------------------------------------

        if clave_bd == clave_recuperada:

            print()
            print(
                "✔ La clave original y la recuperada "
                "coinciden."
            )

        else:

            print()
            print(
                "✘ ERROR: las claves no coinciden."
            )

            raise SystemExit

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        print()
        print("=" * 65)
        print(
            "PRUEBA DEL MÓDULO EXITOSA"
        )
        print("=" * 65)

        print()
        print("Se comprobó:")
        print("✔ clave BD obtenida")
        print("✔ contraseña procesada mediante PBKDF2")
        print("✔ clave BD protegida con AES-GCM")
        print("✔ archivo de recuperación creado")
        print("✔ archivo leído correctamente")
        print("✔ clave BD recuperada")
        print("✔ clave original = clave recuperada")
        print()
        print(
            "LA RECUPERACIÓN FUNCIONA CORRECTAMENTE."
        )

    except Exception as error:

        print()
        print("=" * 65)
        print("ERROR EN LA PRUEBA")
        print("=" * 65)
        print()
        print(error)
        

