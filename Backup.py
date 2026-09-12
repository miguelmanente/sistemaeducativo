
# ========================================================================================
#                         MÓDULO PARA BACKUP DE BASE DE DATOS
#                                  SISTEMA SGE
# ========================================================================================
#
# Responsabilidad:
#   - Crear una copia consistente de la base SQLite.
#   - Obtener la clave de datos desde seguridad.py.
#   - Cifrar el backup mediante Fernet.
#   - Guardar cada backup con fecha y hora.
#   - Evitar sobrescribir backups existentes.
#
# IMPORTANTE:
#   Este módulo NO:
#   - genera claves.
#   - administra Windows DPAPI.
#   - administra la clave de datos.
#   - restaura bases de datos.
#   - maneja ventanas Tkinter.
#
#   La administración de la clave pertenece a seguridad.py.
#   La restauración pertenece a restauracion_nueva.py.
#
# ========================================================================================

import os
import sys
import sqlite3
import base64
from datetime import datetime

from cryptography.fernet import Fernet

from seguridad import obtener_clave_datos


# ========================================================================================
#                                  RUTAS DEL SGE
# ========================================================================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


RUTA_BASE_DATOS = os.path.join(
    BASE_DIR,
    "bdescuela.db"
)

CARPETA_BACKUPS = os.path.join(
    BASE_DIR,
    "backups"
)


# ========================================================================================
#                            OBTENER CLAVE PARA FERNET
# ========================================================================================

def obtener_clave_fernet():

    clave_datos = obtener_clave_datos()

    if not isinstance(clave_datos, bytes):
        raise TypeError(
            "La clave de datos recuperada no es de tipo bytes."
        )

    if len(clave_datos) != 32:
        raise ValueError(
            "La clave de datos debe tener exactamente 32 bytes."
        )

    clave_fernet = base64.urlsafe_b64encode(
        clave_datos
    )

    return clave_fernet


# ========================================================================================
#                         CREAR COPIA CONSISTENTE DE SQLITE
# ========================================================================================

def crear_copia_sqlite(ruta_origen, ruta_temporal):

    if not os.path.isfile(ruta_origen):
        raise FileNotFoundError(
            "No existe la base de datos del SGE:\n\n"
            f"{ruta_origen}"
        )

    conexion_origen = sqlite3.connect(
        ruta_origen
    )

    conexion_destino = sqlite3.connect(
        ruta_temporal
    )

    try:

        conexion_origen.backup(
            conexion_destino
        )

        conexion_destino.commit()

    finally:

        conexion_destino.close()
        conexion_origen.close()


# ========================================================================================
#                         GENERAR NOMBRE SIN COLISIONES
# ========================================================================================

def generar_nombre_backup():

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

    if not os.path.exists(ruta_backup):
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

        if not os.path.exists(ruta_backup):
            return ruta_backup

        contador += 1


# ========================================================================================
#                              CIFRAR LA COPIA
# ========================================================================================

def cifrar_backup(
    ruta_copia_sqlite,
    ruta_backup
):

    if not os.path.isfile(
        ruta_copia_sqlite
    ):
        raise FileNotFoundError(
            "No existe la copia SQLite que se desea cifrar:\n\n"
            f"{ruta_copia_sqlite}"
        )

    # ------------------------------------------------------------------------------------
    # Protección adicional:
    # nunca sobrescribir un backup existente.
    # ------------------------------------------------------------------------------------

    if os.path.exists(
        ruta_backup
    ):
        raise FileExistsError(
            "El archivo de backup ya existe y no será sobrescrito:\n\n"
            f"{ruta_backup}"
        )

    clave_fernet = obtener_clave_fernet()

    fernet = Fernet(
        clave_fernet
    )

    with open(
        ruta_copia_sqlite,
        "rb"
    ) as archivo:

        datos = archivo.read()

    if not datos:

        raise ValueError(
            "La copia SQLite está vacía."
        )

    datos_cifrados = fernet.encrypt(
        datos
    )

    ruta_temporal = ruta_backup + ".tmp"

    try:

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

        # -------------------------------------------------------------------------------
        # Verificar nuevamente que el backup definitivo no apareció mientras se
        # estaba creando el archivo temporal.
        # -------------------------------------------------------------------------------

        if os.path.exists(
            ruta_backup
        ):
            raise FileExistsError(
                "El archivo de backup apareció durante la creación "
                "y no será sobrescrito:\n\n"
                f"{ruta_backup}"
            )

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

    ruta_copia_temporal = None

    try:

        # -------------------------------------------------------------------------------
        # Crear carpeta de backups
        # -------------------------------------------------------------------------------

        os.makedirs(
            CARPETA_BACKUPS,
            exist_ok=True
        )

        # -------------------------------------------------------------------------------
        # Nombre temporal para la copia SQLite
        # -------------------------------------------------------------------------------

        ruta_copia_temporal = os.path.join(
            CARPETA_BACKUPS,
            "sge_backup_temporal.db"
        )

        # -------------------------------------------------------------------------------
        # Si quedó una copia temporal de una ejecución anterior, eliminarla
        # -------------------------------------------------------------------------------

        if os.path.exists(
            ruta_copia_temporal
        ):

            os.remove(
                ruta_copia_temporal
            )

        # -------------------------------------------------------------------------------
        # Crear copia consistente de SQLite
        # -------------------------------------------------------------------------------

        crear_copia_sqlite(
            RUTA_BASE_DATOS,
            ruta_copia_temporal
        )

        # -------------------------------------------------------------------------------
        # Generar nombre disponible
        # -------------------------------------------------------------------------------

        ruta_backup = generar_nombre_backup()

        # -------------------------------------------------------------------------------
        # Cifrar la copia
        # -------------------------------------------------------------------------------

        cifrar_backup(
            ruta_copia_temporal,
            ruta_backup
        )

        # -------------------------------------------------------------------------------
        # Eliminar la copia SQLite temporal sin cifrar
        # -------------------------------------------------------------------------------

        if os.path.exists(
            ruta_copia_temporal
        ):

            os.remove(
                ruta_copia_temporal
            )

        # -------------------------------------------------------------------------------
        # Información del backup
        # -------------------------------------------------------------------------------

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

        # -------------------------------------------------------------------------------
        # Limpieza de copia temporal si ocurrió algún error
        # -------------------------------------------------------------------------------

        if (
            ruta_copia_temporal
            and os.path.exists(ruta_copia_temporal)
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
    print("PRUEBA DEL MÓDULO backup.py")
    print("=" * 80)

    try:

        print()
        print("Base de datos del SGE:")
        print(RUTA_BASE_DATOS)

        print()
        print("Carpeta de backups:")
        print(CARPETA_BACKUPS)

        print()
        print("Obteniendo clave de datos...")

        clave = obtener_clave_datos()

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





