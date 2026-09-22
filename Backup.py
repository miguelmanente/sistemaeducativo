# ========================================================================================
#                         MÓDULO PARA BACKUP DE BASE DE DATOS
#                                  SISTEMA SGE
# ========================================================================================
#
# Responsabilidad:
#   - Crear una copia consistente de la base SQLCipher.
#   - Obtener la clave de la BD desde seguridad_bd.py.
#   - Mantener la base de datos cifrada mediante SQLCipher.
#   - Aplicar una segunda capa de cifrado Fernet al archivo de backup.
#   - Guardar cada backup con fecha y hora.
#   - Evitar sobrescribir backups existentes.
#
# IMPORTANTE:
#   Este módulo NO:
#   - genera claves.
#   - administra Windows DPAPI.
#   - crea claves de recuperación.
#   - restaura bases de datos.
#   - maneja ventanas Tkinter.
#
#   La administración de la clave pertenece a seguridad_bd.py.
#   La restauración pertenece a restauracion_nueva.py.
#
# ========================================================================================


# ========================================================================================
#                                  LIBRERÍAS
# ========================================================================================

import os
import base64
from datetime import datetime

from sqlcipher3 import dbapi2 as sqlite3

from cryptography.fernet import Fernet

from seguridad_bd import (
    obtener_clave_bd,
    obtener_ruta_datos
)


# ========================================================================================
#                                  RUTAS DEL SGE
# ========================================================================================

# ----------------------------------------------------------------------------------------
# La base de datos se encuentra dentro de:
#
#   C:\ProgramData\SGE\Datos\bdescuela.db
#
# durante la versión instalada.
#
# En desarrollo, seguridad_bd.py utiliza:
#
#   Proyecto\Datos\bdescuela.db
#
# ----------------------------------------------------------------------------------------

RUTA_DATOS = obtener_ruta_datos()

RUTA_BASE_DATOS = os.path.join(
    RUTA_DATOS,
    "bdescuela.db"
)


# ----------------------------------------------------------------------------------------
# La carpeta Backups se encuentra al mismo nivel que Datos:
#
#   C:\ProgramData\SGE\
#       ├── Datos
#       ├── Seguridad
#       └── Backups
#
# ----------------------------------------------------------------------------------------

RUTA_BASE_SGE = os.path.dirname(
    RUTA_DATOS
)

CARPETA_BACKUPS = os.path.join(
    RUTA_BASE_SGE,
    "Backups"
)


# ========================================================================================
#                       CONFIGURAR CLAVE DE SQLCIPHER
# ========================================================================================

def configurar_clave_sqlcipher(
    conexion,
    clave_bd
):
    """
    Configura la clave de cifrado SQLCipher
    para una conexión.

    La clave original es de 32 bytes.

    SQLCipher acepta la clave en formato hexadecimal
    mediante:

        PRAGMA key = "x'...'"

    """

    if not isinstance(
        clave_bd,
        bytes
    ):
        raise TypeError(
            "La clave de la base de datos debe "
            "ser de tipo bytes."
        )

    if len(clave_bd) != 32:
        raise ValueError(
            "La clave de la base de datos debe "
            "tener exactamente 32 bytes."
        )

    clave_hex = clave_bd.hex()

    conexion.execute(
        f'PRAGMA key = "x\'{clave_hex}\'"'
    )


# ========================================================================================
#                         OBTENER CLAVE PARA FERNET
# ========================================================================================

def obtener_clave_fernet():
    """
    Obtiene la clave de la base de datos y la
    convierte al formato requerido por Fernet.

    IMPORTANTE:

    La misma clave criptográfica de 32 bytes
    utilizada para SQLCipher se utiliza aquí
    únicamente para proteger el archivo de backup
    con una segunda capa Fernet.

    La clave nunca se guarda en texto plano.
    """

    clave_bd = obtener_clave_bd()

    if not isinstance(
        clave_bd,
        bytes
    ):
        raise TypeError(
            "La clave de la base de datos recuperada "
            "no es de tipo bytes."
        )

    if len(clave_bd) != 32:
        raise ValueError(
            "La clave de la base de datos debe "
            "tener exactamente 32 bytes."
        )

    clave_fernet = base64.urlsafe_b64encode(
        clave_bd
    )

    return clave_fernet


# ========================================================================================
#                 CREAR COPIA CONSISTENTE DE LA BASE SQLCIPHER
# ========================================================================================

def crear_copia_sqlcipher(
    ruta_origen,
    ruta_temporal,
    clave_bd
):
    """
    Crea una copia consistente de una base SQLCipher.

    Tanto la base de origen como la copia temporal
    se abren utilizando la clave de la base de datos.

    La copia temporal continúa siendo una base
    SQLCipher cifrada.

    No se genera una copia SQLite en texto plano.
    """

    if not os.path.isfile(
        ruta_origen
    ):
        raise FileNotFoundError(
            "No existe la base de datos del SGE:\n\n"
            f"{ruta_origen}"
        )

    # ------------------------------------------------------------------------------------
    # La copia temporal no debe existir previamente.
    # ------------------------------------------------------------------------------------

    if os.path.exists(
        ruta_temporal
    ):
        raise FileExistsError(
            "La copia temporal ya existe:\n\n"
            f"{ruta_temporal}"
        )

    conexion_origen = None
    conexion_destino = None

    try:

        # --------------------------------------------------------------------------------
        # Abrir base de origen utilizando SQLCipher.
        # --------------------------------------------------------------------------------

        conexion_origen = sqlite3.connect(
            ruta_origen
        )

        configurar_clave_sqlcipher(
            conexion_origen,
            clave_bd
        )

        # --------------------------------------------------------------------------------
        # Verificar que la base de origen pueda abrirse correctamente.
        # --------------------------------------------------------------------------------

        conexion_origen.execute(
            "SELECT count(*) FROM sqlite_master"
        ).fetchone()

        # --------------------------------------------------------------------------------
        # Crear conexión destino.
        # --------------------------------------------------------------------------------

        conexion_destino = sqlite3.connect(
            ruta_temporal
        )

        # --------------------------------------------------------------------------------
        # Configurar la misma clave antes de realizar
        # la operación de backup.
        # --------------------------------------------------------------------------------

        configurar_clave_sqlcipher(
            conexion_destino,
            clave_bd
        )

        # --------------------------------------------------------------------------------
        # Realizar copia consistente mediante el mecanismo
        # de backup de SQLite/SQLCipher.
        # --------------------------------------------------------------------------------

        conexion_origen.backup(
            conexion_destino
        )

        conexion_destino.commit()

    finally:

        if conexion_destino is not None:

            conexion_destino.close()

        if conexion_origen is not None:

            conexion_origen.close()


# ========================================================================================
#                         GENERAR NOMBRE SIN COLISIONES
# ========================================================================================

def generar_nombre_backup():
    """
    Genera un nombre de backup basado en fecha y hora.

    Ejemplo:

        backup_sge_20260922_173015.enc

    Si ya existe un archivo con ese nombre,
    agrega un contador.
    """

    fecha = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    nombre_base = (
        f"backup_sge_{fecha}"
    )

    ruta_backup = os.path.join(
        CARPETA_BACKUPS,
        nombre_base + ".enc"
    )

    if not os.path.exists(
        ruta_backup
    ):
        return ruta_backup

    contador = 1

    while True:

        nombre_backup = (
            f"{nombre_base}_{contador:02d}.enc"
        )

        ruta_backup = os.path.join(
            CARPETA_BACKUPS,
            nombre_backup
        )

        if not os.path.exists(
            ruta_backup
        ):
            return ruta_backup

        contador += 1


# ========================================================================================
#                              CIFRAR LA COPIA
# ========================================================================================

def cifrar_backup(
    ruta_copia_sqlcipher,
    ruta_backup
):
    """
    Aplica una segunda capa de cifrado Fernet
    sobre la copia SQLCipher.

    El archivo original ya está cifrado mediante
    SQLCipher.

    Fernet agrega una capa adicional para proteger
    el archivo de backup almacenado externamente.
    """

    if not os.path.isfile(
        ruta_copia_sqlcipher
    ):
        raise FileNotFoundError(
            "No existe la copia SQLCipher que "
            "se desea cifrar:\n\n"
            f"{ruta_copia_sqlcipher}"
        )

    # ------------------------------------------------------------------------------------
    # Nunca sobrescribir un backup existente.
    # ------------------------------------------------------------------------------------

    if os.path.exists(
        ruta_backup
    ):
        raise FileExistsError(
            "El archivo de backup ya existe "
            "y no será sobrescrito:\n\n"
            f"{ruta_backup}"
        )

    clave_fernet = obtener_clave_fernet()

    fernet = Fernet(
        clave_fernet
    )

    with open(
        ruta_copia_sqlcipher,
        "rb"
    ) as archivo:

        datos = archivo.read()

    if not datos:

        raise ValueError(
            "La copia SQLCipher está vacía."
        )

    datos_cifrados = fernet.encrypt(
        datos
    )

    ruta_temporal = (
        ruta_backup + ".tmp"
    )

    try:

        # --------------------------------------------------------------------------------
        # Crear archivo temporal de forma exclusiva.
        # --------------------------------------------------------------------------------

        with open(
            ruta_temporal,
            "xb"
        ) as archivo:

            archivo.write(
                datos_cifrados
            )

            archivo.flush()

            os.fsync(
                archivo.fileno()
            )

        # --------------------------------------------------------------------------------
        # Verificar nuevamente que el destino definitivo
        # no haya aparecido durante la operación.
        # --------------------------------------------------------------------------------

        if os.path.exists(
            ruta_backup
        ):
            raise FileExistsError(
                "El archivo de backup apareció durante "
                "la creación y no será sobrescrito:\n\n"
                f"{ruta_backup}"
            )

        # --------------------------------------------------------------------------------
        # Reemplazo atómico.
        # --------------------------------------------------------------------------------

        os.replace(
            ruta_temporal,
            ruta_backup
        )

    except Exception:

        try:

            if os.path.exists(
                ruta_temporal
            ):
                os.remove(
                    ruta_temporal
                )

        except OSError:
            pass

        raise


# ========================================================================================
#                              CREAR BACKUP
# ========================================================================================

def crear_backup():
    """
    Crea un backup completo y cifrado de la base
    de datos del SGE.

    Proceso:

        1. Recuperar clave BD.
        2. Crear copia consistente mediante SQLCipher.
        3. Mantener esa copia cifrada.
        4. Aplicar Fernet.
        5. Guardar archivo .enc.
        6. Eliminar copia temporal.
    """

    ruta_copia_temporal = None

    try:

        # --------------------------------------------------------------------------------
        # Crear carpeta de backups.
        # --------------------------------------------------------------------------------

        os.makedirs(
            CARPETA_BACKUPS,
            exist_ok=True
        )

        # --------------------------------------------------------------------------------
        # Obtener la clave de la BD.
        #
        # IMPORTANTE:
        # obtener_clave_bd() NO genera una clave nueva.
        # --------------------------------------------------------------------------------

        clave_bd = obtener_clave_bd()

        if not isinstance(
            clave_bd,
            bytes
        ):
            raise TypeError(
                "La clave de la base de datos "
                "no es válida."
            )

        if len(clave_bd) != 32:
            raise ValueError(
                "La clave de la base de datos "
                "debe tener 32 bytes."
            )

        # --------------------------------------------------------------------------------
        # Nombre temporal.
        # --------------------------------------------------------------------------------

        ruta_copia_temporal = os.path.join(
            CARPETA_BACKUPS,
            "sge_backup_temporal.db"
        )

        # --------------------------------------------------------------------------------
        # Eliminar temporal anterior si hubiera quedado
        # de una ejecución interrumpida.
        # --------------------------------------------------------------------------------

        if os.path.exists(
            ruta_copia_temporal
        ):

            os.remove(
                ruta_copia_temporal
            )

        # --------------------------------------------------------------------------------
        # Crear copia consistente SQLCipher.
        # --------------------------------------------------------------------------------

        crear_copia_sqlcipher(
            RUTA_BASE_DATOS,
            ruta_copia_temporal,
            clave_bd
        )

        # --------------------------------------------------------------------------------
        # Generar nombre definitivo.
        # --------------------------------------------------------------------------------

        ruta_backup = generar_nombre_backup()

        # --------------------------------------------------------------------------------
        # Aplicar segunda capa de cifrado Fernet.
        # --------------------------------------------------------------------------------

        cifrar_backup(
            ruta_copia_temporal,
            ruta_backup
        )

        # --------------------------------------------------------------------------------
        # Eliminar copia temporal SQLCipher.
        # --------------------------------------------------------------------------------

        if os.path.exists(
            ruta_copia_temporal
        ):

            os.remove(
                ruta_copia_temporal
            )

        ruta_copia_temporal = None

        # --------------------------------------------------------------------------------
        # Obtener tamaño final.
        # --------------------------------------------------------------------------------

        tamaño_backup = os.path.getsize(
            ruta_backup
        )

        print(
            "Backup cifrado creado correctamente:"
        )

        print(
            ruta_backup
        )

        print(
            f"Tamaño del backup: {tamaño_backup} bytes"
        )

        return ruta_backup

    except Exception as error:

        # --------------------------------------------------------------------------------
        # Limpieza de copia temporal ante cualquier error.
        # --------------------------------------------------------------------------------

        if (
            ruta_copia_temporal
            and os.path.exists(
                ruta_copia_temporal
            )
        ):

            try:

                os.remove(
                    ruta_copia_temporal
                )

            except OSError:
                pass

        print(
            "Error backup:",
            error
        )

        raise


# ========================================================================================
#                                      PRUEBA
# ========================================================================================

if __name__ == "__main__":

    print("=" * 80)
    print("PRUEBA DEL MÓDULO Backup.py")
    print("=" * 80)

    try:

        print()
        print("Base de datos del SGE:")
        print(
            RUTA_BASE_DATOS
        )

        print()
        print("Carpeta de backups:")
        print(
            CARPETA_BACKUPS
        )

        print()
        print("Obteniendo clave de la base de datos...")

        clave = obtener_clave_bd()

        print(
            "Clave obtenida correctamente."
        )

        print(
            "Bytes:",
            len(clave)
        )

        print(
            "Bits:",
            len(clave) * 8
        )

        print()
        print(
            "Creando backup cifrado..."
        )

        ruta_backup = crear_backup()

        print()
        print(
            "BACKUP CIFRADO CREADO CORRECTAMENTE."
        )

        print()
        print(
            "Archivo:"
        )

        print(
            ruta_backup
        )

        print()
        print("=" * 80)
        print("PRUEBA FINALIZADA")
        print("=" * 80)

    except Exception as error:

        print()
        print("ERROR")
        print()
        print(
            str(error)
        )

        print()
        print("=" * 80)





