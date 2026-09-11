# ============================================================
# restauracion_nueva.py
# Sistema de Gestión Educativa (SGE)
#
# Responsabilidad:
#   - Recuperar un backup cifrado
#   - Obtener la clave de datos desde seguridad.py
#   - Descifrar el backup mediante Fernet
#   - Crear una nueva base de datos SQLite
#
# IMPORTANTE:
#   Este módulo NO:
#   - genera claves
#   - administra DPAPI
#   - modifica la base de datos original
#   - maneja ventanas Tkinter
#
#   La administración de la clave pertenece a seguridad.py
# ============================================================

import os
import sys
import base64
import sqlite3

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
# OBTENER CLAVE PARA FERNET
# ============================================================

def obtener_clave_fernet():
    """
    Obtiene la clave de datos desde seguridad.py
    y la convierte al formato requerido por Fernet.
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

    return base64.urlsafe_b64encode(clave_datos)


# ============================================================
# DESCIFRAR BACKUP
# ============================================================

def descifrar_backup(ruta_backup, ruta_base_datos):
    """
    Descifra un backup Fernet y crea una nueva base SQLite.

    La base original no es modificada.
    """

    if not os.path.isfile(ruta_backup):
        raise FileNotFoundError(
            "No existe el backup indicado:\n\n"
            f"{ruta_backup}"
        )

    # --------------------------------------------------------
    # Obtener la misma clave utilizada para cifrar
    # --------------------------------------------------------

    clave_fernet = obtener_clave_fernet()

    fernet = Fernet(clave_fernet)

    # --------------------------------------------------------
    # Leer backup cifrado
    # --------------------------------------------------------

    with open(ruta_backup, "rb") as archivo:
        datos_cifrados = archivo.read()

    if not datos_cifrados:
        raise ValueError(
            "El archivo de backup está vacío."
        )

    # --------------------------------------------------------
    # Descifrar
    #
    # Fernet también verifica automáticamente la integridad.
    # Si el backup fue alterado o está dañado, se producirá
    # una excepción y NO se creará la base recuperada.
    # --------------------------------------------------------

    datos_recuperados = fernet.decrypt(datos_cifrados)

    if not datos_recuperados:
        raise ValueError(
            "El backup fue descifrado pero no contiene datos."
        )

    # --------------------------------------------------------
    # Crear carpeta destino
    # --------------------------------------------------------

    carpeta_destino = os.path.dirname(ruta_base_datos)

    if carpeta_destino:
        os.makedirs(carpeta_destino, exist_ok=True)

    # --------------------------------------------------------
    # Guardar temporalmente
    # --------------------------------------------------------

    ruta_temporal = ruta_base_datos + ".tmp"

    try:

        with open(ruta_temporal, "wb") as archivo:

            archivo.write(datos_recuperados)

            archivo.flush()

            os.fsync(archivo.fileno())

        # ----------------------------------------------------
        # Reemplazo atómico
        # ----------------------------------------------------

        os.replace(ruta_temporal, ruta_base_datos)

    except Exception:

        try:
            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)
        except OSError:
            pass

        raise

    return ruta_base_datos


# ============================================================
# VERIFICAR BASE SQLITE
# ============================================================

def verificar_base_sqlite(ruta_base_datos):
    """
    Comprueba que el archivo recuperado sea realmente
    una base SQLite válida.
    """

    if not os.path.isfile(ruta_base_datos):
        raise FileNotFoundError(
            "No existe la base recuperada."
        )

    conexion = sqlite3.connect(ruta_base_datos)

    try:

        resultado = conexion.execute(
            "PRAGMA integrity_check;"
        ).fetchone()

        if not resultado:
            raise RuntimeError(
                "SQLite no devolvió resultado de integridad."
            )

        if resultado[0] != "ok":
            raise RuntimeError(
                "La base SQLite no superó la prueba de integridad:\n"
                f"{resultado[0]}"
            )

    finally:

        conexion.close()

    return True


# ============================================================
# COMPARAR ARCHIVOS
# ============================================================

def comparar_archivos(ruta_archivo_1, ruta_archivo_2):
    """
    Compara byte por byte dos archivos.
    """

    if not os.path.isfile(ruta_archivo_1):
        raise FileNotFoundError(
            f"No existe:\n{ruta_archivo_1}"
        )

    if not os.path.isfile(ruta_archivo_2):
        raise FileNotFoundError(
            f"No existe:\n{ruta_archivo_2}"
        )

    with open(ruta_archivo_1, "rb") as archivo:
        datos_1 = archivo.read()

    with open(ruta_archivo_2, "rb") as archivo:
        datos_2 = archivo.read()

    return datos_1 == datos_2


# ============================================================
# PRUEBA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBA DEL MÓDULO restauracion_nueva.py")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # BASE ORIGINAL DE LABORATORIO
        # ----------------------------------------------------

        ruta_bd_original = os.path.join(
            BASE_DIR,
            "bdescuela_prueba.db"
        )

        # ----------------------------------------------------
        # CARPETA DE BACKUPS
        # ----------------------------------------------------

        carpeta_backups = os.path.join(
            BASE_DIR,
            "backups_prueba"
        )

        # ----------------------------------------------------
        # Buscar el backup más reciente
        # ----------------------------------------------------

        archivos_backup = [
            archivo
            for archivo in os.listdir(carpeta_backups)
            if archivo.endswith(".enc")
        ]

        if not archivos_backup:
            raise FileNotFoundError(
                "No se encontró ningún backup .enc "
                "en la carpeta backups_prueba."
            )

        archivos_backup.sort()

        nombre_backup = archivos_backup[-1]

        ruta_backup = os.path.join(
            carpeta_backups,
            nombre_backup
        )

        # ----------------------------------------------------
        # BASE RECUPERADA
        # ----------------------------------------------------

        ruta_bd_recuperada = os.path.join(
            BASE_DIR,
            "bdescuela_recuperada.db"
        )

        print()
        print("📦 Backup seleccionado:")
        print(ruta_backup)

        print()
        print("📁 Base original de laboratorio:")
        print(ruta_bd_original)

        print()
        print("📁 Base que será recuperada:")
        print(ruta_bd_recuperada)

        # ----------------------------------------------------
        # Obtener clave
        # ----------------------------------------------------

        print()
        print("🔑 Obteniendo clave de datos desde seguridad.py...")

        clave = obtener_clave_datos()

        print("✅ Clave obtenida correctamente.")

        print()
        print("Cantidad de bytes:", len(clave))
        print("Cantidad de bits:", len(clave) * 8)

        # ----------------------------------------------------
        # Descifrar
        # ----------------------------------------------------

        print()
        print("🔓 Descifrando backup...")

        descifrar_backup(
            ruta_backup,
            ruta_bd_recuperada
        )

        print("✅ Backup descifrado correctamente.")

        # ----------------------------------------------------
        # Verificar SQLite
        # ----------------------------------------------------

        print()
        print("🧪 Verificando integridad de SQLite...")

        verificar_base_sqlite(
            ruta_bd_recuperada
        )

        print("✅ La base recuperada es una SQLite válida.")

        # ----------------------------------------------------
        # Comparar archivos
        # ----------------------------------------------------

        print()
        print("🔍 Comparando base original y base recuperada...")

        son_iguales = comparar_archivos(
            ruta_bd_original,
            ruta_bd_recuperada
        )

        tamaño_original = os.path.getsize(
            ruta_bd_original
        )

        tamaño_recuperado = os.path.getsize(
            ruta_bd_recuperada
        )

        print()
        print("📊 Tamaño base original:")
        print(tamaño_original, "bytes")

        print()
        print("📊 Tamaño base recuperada:")
        print(tamaño_recuperado, "bytes")

        print()

        if son_iguales:

            print("🎉 ¡COMPARACIÓN EXITOSA!")
            print()
            print(
                "La base recuperada es exactamente igual "
                "a la base original."
            )
            print()
            print("✔ misma clave")
            print("✔ backup descifrado")
            print("✔ integridad Fernet verificada")
            print("✔ SQLite válida")
            print("✔ archivos idénticos")

        else:

            print("❌ LAS BASES SON DIFERENTES.")

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
