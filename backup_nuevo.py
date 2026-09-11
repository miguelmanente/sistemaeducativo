
# ============================================================
# backup.py
# Sistema de Gestión Educativa (SGE)
#
# Responsabilidad:
#   - Crear backups cifrados de la base de datos
#   - Obtener la clave desde seguridad.py
#   - Utilizar Fernet para cifrar el backup
#
# IMPORTANTE:
#   Este módulo NO:
#   - genera claves
#   - administra DPAPI
#   - administra la clave de datos
#   - restaura bases de datos
#   - maneja ventanas Tkinter
#
#   La administración de la clave pertenece a seguridad.py
# ============================================================

import os
import sys
import base64
from datetime import datetime

from cryptography.fernet import Fernet

from seguridad import obtener_clave_datos


# ============================================================
# UBICACIÓN BASE DEL SGE
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# RUTAS
# ============================================================

CARPETA_BACKUPS = os.path.join(BASE_DIR, "backups")


# ============================================================
# OBTENER CLAVE PARA FERNET
# ============================================================

def obtener_clave_fernet():
    """
    Obtiene la clave de datos desde seguridad.py
    y la convierte al formato requerido por Fernet.

    seguridad.py trabaja con:
        32 bytes

    Fernet necesita:
        clave codificada en Base64 URL-safe
    """

    clave_datos = obtener_clave_datos()

    if not isinstance(clave_datos, bytes):
        raise TypeError(
            "La clave de datos recuperada no es de tipo bytes."
        )

    if len(clave_datos) != 32:
        raise ValueError(
            "La clave de datos debe tener exactamente 32 bytes."
        )

    clave_fernet = base64.urlsafe_b64encode(clave_datos)

    return clave_fernet


# ============================================================
# CIFRAR UNA BASE DE DATOS
# ============================================================

def cifrar_base_datos(ruta_base_datos, ruta_backup):
    """
    Lee una base de datos SQLite, la cifra y guarda
    el resultado en un archivo de backup.

    No modifica la base de datos original.
    """

    if not os.path.isfile(ruta_base_datos):
        raise FileNotFoundError(
            "No existe la base de datos indicada:\n\n"
            f"{ruta_base_datos}"
        )

    # --------------------------------------------------------
    # Obtener clave de datos
    # --------------------------------------------------------

    clave_fernet = obtener_clave_fernet()

    # --------------------------------------------------------
    # Crear objeto Fernet
    # --------------------------------------------------------

    fernet = Fernet(clave_fernet)

    # --------------------------------------------------------
    # Leer la base de datos
    # --------------------------------------------------------

    with open(ruta_base_datos, "rb") as archivo:
        datos = archivo.read()

    if not datos:
        raise ValueError(
            "La base de datos está vacía."
        )

    # --------------------------------------------------------
    # Cifrar
    # --------------------------------------------------------

    datos_cifrados = fernet.encrypt(datos)

    # --------------------------------------------------------
    # Crear carpeta destino
    # --------------------------------------------------------

    carpeta_destino = os.path.dirname(ruta_backup)

    if carpeta_destino:
        os.makedirs(carpeta_destino, exist_ok=True)

    # --------------------------------------------------------
    # Guardar de forma segura
    # --------------------------------------------------------

    ruta_temporal = ruta_backup + ".tmp"

    try:

        with open(ruta_temporal, "wb") as archivo:

            archivo.write(datos_cifrados)

            archivo.flush()

            os.fsync(archivo.fileno())

        os.replace(ruta_temporal, ruta_backup)

    except Exception:

        try:
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
        except OSError:
            pass

        raise

    return ruta_backup


# ============================================================
# CREAR BACKUP
# ============================================================

def crear_backup(ruta_base_datos, carpeta_destino=None):
    """
    Crea un backup cifrado de la base de datos indicada.

    El nombre del archivo incluye fecha y hora para evitar
    sobrescribir automáticamente backups anteriores.
    """

    if carpeta_destino is None:
        carpeta_destino = CARPETA_BACKUPS

    os.makedirs(carpeta_destino, exist_ok=True)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    nombre_backup = (
        f"backup_sge_{fecha}.enc"
    )

    ruta_backup = os.path.join(
        carpeta_destino,
        nombre_backup
    )

    return cifrar_base_datos(
        ruta_base_datos,
        ruta_backup
    )


# ============================================================
# PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBA DEL MÓDULO backup.py")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # IMPORTANTE:
        # Usamos una COPIA de laboratorio.
        # NO usamos bdescuela.db
        # ----------------------------------------------------

        ruta_bd_prueba = os.path.join(
            BASE_DIR,
            "bdescuela_prueba.db"
        )

        carpeta_prueba = os.path.join(
            BASE_DIR,
            "backups_prueba"
        )

        print()
        print("📁 Base de datos de prueba:")
        print(ruta_bd_prueba)

        print()
        print("📁 Carpeta de backups:")
        print(carpeta_prueba)

        print()
        print("🔑 Obteniendo clave de datos desde seguridad.py...")

        clave = obtener_clave_datos()

        print("✅ Clave obtenida correctamente.")

        print()
        print("Cantidad de bytes:", len(clave))
        print("Cantidad de bits:", len(clave) * 8)

        print()
        print("🔐 Creando backup cifrado...")

        ruta_backup = crear_backup(
            ruta_bd_prueba,
            carpeta_prueba
        )

        print()
        print("✅ BACKUP CIFRADO CREADO.")

        print()
        print("📦 Archivo:")
        print(ruta_backup)

        print()

        tamaño_original = os.path.getsize(
            ruta_bd_prueba
        )

        tamaño_backup = os.path.getsize(
            ruta_backup
        )

        print("📊 Tamaño de la base original:")
        print(tamaño_original, "bytes")

        print()
        print("📊 Tamaño del backup cifrado:")
        print(tamaño_backup, "bytes")

        print()
        print("🛡️ La base de datos original NO fue modificada.")

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
