
# ============================================================
# restauracion_nueva.py
# Sistema de Gestión Educativa (SGE)
#
# Responsabilidad:
#   - Recuperar un backup cifrado.
#   - Obtener la clave de datos normalmente desde seguridad.py.
#   - Permitir recuperar la clave desde recuperacion.py
#     en caso de desastre.
#   - Descifrar el backup mediante Fernet.
#   - Crear una nueva base de datos SQLite.
#   - Verificar la integridad de la base recuperada.
#
# IMPORTANTE:
#   Este módulo NO:
#   - genera claves.
#   - administra Windows DPAPI.
#   - crea archivos de recuperación.
#   - maneja ventanas Tkinter.
#
#   La administración de la clave pertenece a seguridad.py.
#   La recuperación de emergencia pertenece a recuperacion.py.
#
# ============================================================

import os
import sys
import base64
import sqlite3

from cryptography.fernet import Fernet

from seguridad import obtener_clave_datos


# ============================================================
# UBICACIÓN BASE
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# CONVERTIR CLAVE DE DATOS A CLAVE FERNET
# ============================================================

def convertir_clave_fernet(clave_datos):
    """
    Convierte la clave de datos de 32 bytes a la representación
    Base64 URL-safe requerida por Fernet.
    """

    if not isinstance(clave_datos, bytes):
        raise TypeError(
            "La clave de datos debe ser de tipo bytes."
        )

    if len(clave_datos) != 32:
        raise ValueError(
            "La clave de datos debe tener exactamente 32 bytes."
        )

    return base64.urlsafe_b64encode(clave_datos)


# ============================================================
# OBTENER CLAVE FERNET MEDIANTE EL SISTEMA NORMAL
# ============================================================

def obtener_clave_fernet():
    """
    Obtiene la clave de datos mediante seguridad.py
    y la convierte al formato utilizado por Fernet.

    Este es el camino normal de funcionamiento.
    """

    clave_datos = obtener_clave_datos()

    return convertir_clave_fernet(clave_datos)


# ============================================================
# DESCIFRAR BACKUP
# ============================================================

def descifrar_backup(
    ruta_backup,
    ruta_base_datos,
    clave_datos=None
):
    """
    Descifra un backup .enc y genera una base SQLite.

    Si clave_datos es None:
        obtiene la clave mediante seguridad.py.

    Si clave_datos contiene una clave:
        utiliza directamente esa clave.

    Esta segunda posibilidad permite realizar una
    recuperación de emergencia sin depender de DPAPI.
    """

    # --------------------------------------------------------
    # Verificar backup
    # --------------------------------------------------------

    if not os.path.isfile(ruta_backup):
        raise FileNotFoundError(
            "No existe el backup indicado:\n\n"
            f"{ruta_backup}"
        )

    # --------------------------------------------------------
    # Obtener clave
    # --------------------------------------------------------

    if clave_datos is None:

        clave_fernet = obtener_clave_fernet()

    else:

        clave_fernet = convertir_clave_fernet(
            clave_datos
        )

    # --------------------------------------------------------
    # Crear Fernet
    # --------------------------------------------------------

    fernet = Fernet(clave_fernet)

    # --------------------------------------------------------
    # Leer backup cifrado
    # --------------------------------------------------------

    with open(
        ruta_backup,
        "rb"
    ) as archivo:

        datos_cifrados = archivo.read()

    if not datos_cifrados:
        raise ValueError(
            "El archivo de backup está vacío."
        )

    # --------------------------------------------------------
    # Descifrar
    # --------------------------------------------------------

    datos_recuperados = fernet.decrypt(
        datos_cifrados
    )

    if not datos_recuperados:
        raise ValueError(
            "El backup fue descifrado pero "
            "no contiene datos."
        )

    # --------------------------------------------------------
    # Preparar carpeta destino
    # --------------------------------------------------------

    carpeta_destino = os.path.dirname(
        os.path.abspath(ruta_base_datos)
    )

    if carpeta_destino:

        os.makedirs(
            carpeta_destino,
            exist_ok=True
        )

    # --------------------------------------------------------
    # Crear archivo temporal
    # --------------------------------------------------------

    ruta_temporal = ruta_base_datos + ".tmp"

    try:

        with open(
            ruta_temporal,
            "wb"
        ) as archivo:

            archivo.write(
                datos_recuperados
            )

            archivo.flush()
            os.fsync(archivo.fileno())

        # ----------------------------------------------------
        # Reemplazo atómico
        # ----------------------------------------------------

        os.replace(
            ruta_temporal,
            ruta_base_datos
        )

    except Exception:

        try:

            if os.path.exists(ruta_temporal):
                os.remove(ruta_temporal)

        except OSError:
            pass

        raise

    return ruta_base_datos


# ============================================================
# VERIFICAR INTEGRIDAD DE SQLITE
# ============================================================

def verificar_base_sqlite(ruta_base_datos):
    """
    Comprueba que la base recuperada sea una SQLite válida
    y que haya superado la prueba de integridad.
    """

    if not os.path.isfile(ruta_base_datos):

        raise FileNotFoundError(
            "No existe la base recuperada."
        )

    conexion = sqlite3.connect(
        ruta_base_datos
    )

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
                "La base SQLite no superó "
                "la prueba de integridad:\n"
                f"{resultado[0]}"
            )

    finally:

        conexion.close()

    return True


# ============================================================
# COMPARAR ARCHIVOS
# ============================================================

def comparar_archivos(
    ruta_archivo_1,
    ruta_archivo_2
):
    """
    Compara dos archivos byte por byte.
    """

    if not os.path.isfile(ruta_archivo_1):

        raise FileNotFoundError(
            f"No existe:\n{ruta_archivo_1}"
        )

    if not os.path.isfile(ruta_archivo_2):

        raise FileNotFoundError(
            f"No existe:\n{ruta_archivo_2}"
        )

    with open(
        ruta_archivo_1,
        "rb"
    ) as archivo:

        datos_1 = archivo.read()

    with open(
        ruta_archivo_2,
        "rb"
    ) as archivo:

        datos_2 = archivo.read()

    return datos_1 == datos_2


# ============================================================
# RECUPERACIÓN DE EMERGENCIA
# ============================================================

def recuperar_desde_emergencia(
    ruta_archivo_recuperacion,
    frase_recuperacion,
    ruta_backup,
    ruta_base_datos
):
    """
    Realiza una recuperación completa utilizando:

        - archivo de recuperación externo
        - frase de recuperación
        - backup cifrado

    No depende de la clave protegida mediante DPAPI.

    Flujo:

        archivo + frase
              ↓
        recuperacion.py
              ↓
        clave de datos
              ↓
        descifrar backup
              ↓
        base SQLite
              ↓
        verificar integridad
    """

    # --------------------------------------------------------
    # Importación local para mantener separadas
    # las responsabilidades de los módulos.
    # --------------------------------------------------------

    from recuperacion import recuperar_clave_datos

    # --------------------------------------------------------
    # Recuperar clave de datos
    # --------------------------------------------------------

    clave_datos = recuperar_clave_datos(
        frase_recuperacion,
        ruta_archivo_recuperacion
    )

    # --------------------------------------------------------
    # Descifrar backup
    # --------------------------------------------------------

    ruta_recuperada = descifrar_backup(
        ruta_backup,
        ruta_base_datos,
        clave_datos
    )

    # --------------------------------------------------------
    # Verificar SQLite
    # --------------------------------------------------------

    verificar_base_sqlite(
        ruta_recuperada
    )

    return ruta_recuperada


# ============================================================
# PRUEBA DIRECTA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("PRUEBA DEL MÓDULO restauracion_nueva.py")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # Rutas de laboratorio
        # ----------------------------------------------------

        ruta_bd_original = os.path.join(
            BASE_DIR,
            "bdescuela_prueba.db"
        )

        carpeta_backups = os.path.join(
            BASE_DIR,
            "backups_prueba"
        )

        # ----------------------------------------------------
        # Buscar backups cifrados
        # ----------------------------------------------------

        if not os.path.isdir(carpeta_backups):

            raise FileNotFoundError(
                "No existe la carpeta backups_prueba."
            )

        archivos_backup = [
            archivo
            for archivo in os.listdir(
                carpeta_backups
            )
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

        ruta_bd_recuperada = os.path.join(
            BASE_DIR,
            "bdescuela_recuperada.db"
        )

        # ----------------------------------------------------
        # Mostrar información
        # ----------------------------------------------------

        print()
        print("📦 Backup seleccionado:")
        print(ruta_backup)

        print()
        print("📁 Base original:")
        print(ruta_bd_original)

        print()
        print("📁 Base que será recuperada:")
        print(ruta_bd_recuperada)

        # ----------------------------------------------------
        # Obtener clave mediante seguridad.py
        # ----------------------------------------------------

        print()
        print(
            "🔑 Obteniendo clave de datos "
            "desde seguridad.py..."
        )

        clave = obtener_clave_datos()

        print(
            "✅ Clave obtenida correctamente."
        )

        print()
        print(
            "Cantidad de bytes:",
            len(clave)
        )

        print(
            "Cantidad de bits:",
            len(clave) * 8
        )

        # ----------------------------------------------------
        # Descifrar
        # ----------------------------------------------------

        print()
        print("🔓 Descifrando backup...")

        descifrar_backup(
            ruta_backup,
            ruta_bd_recuperada,
            clave
        )

        print(
            "✅ Backup descifrado correctamente."
        )

        # ----------------------------------------------------
        # Verificar SQLite
        # ----------------------------------------------------

        print()
        print(
            "🧪 Verificando integridad de SQLite..."
        )

        verificar_base_sqlite(
            ruta_bd_recuperada
        )

        print(
            "✅ La base recuperada es una SQLite válida."
        )

        # ----------------------------------------------------
        # Comparar
        # ----------------------------------------------------

        print()
        print(
            "🔍 Comparando base original "
            "y base recuperada..."
        )

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
        print(
            "📊 Tamaño base original:"
        )

        print(
            tamaño_original,
            "bytes"
        )

        print()
        print(
            "📊 Tamaño base recuperada:"
        )

        print(
            tamaño_recuperado,
            "bytes"
        )

        print()

        if son_iguales:

            print(
                "🎉 ¡COMPARACIÓN EXITOSA!"
            )

            print()
            print(
                "La base recuperada es exactamente "
                "igual a la base original."
            )

            print()
            print("✔ misma clave")
            print("✔ backup descifrado")
            print("✔ integridad Fernet verificada")
            print("✔ SQLite válida")
            print("✔ archivos idénticos")

        else:

            print(
                "❌ LAS BASES SON DIFERENTES."
            )

        print()
        print("=" * 70)
        print("PRUEBA FINALIZADA")
        print("=" * 70)

    except Exception as error:

        print()
        print("❌ ERROR")
        print()
        print(str(error))
        print()
        print("=" * 70)

