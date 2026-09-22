# ============================================================
# restauracion_nueva.py
# Sistema de Gestión Educativa (SGE)
#
# Responsabilidad:
#   - Recuperar un backup cifrado del SGE.
#   - Obtener la clave de la BD desde seguridad_bd.py.
#   - Descifrar la capa Fernet del backup.
#   - Trabajar con bases SQLCipher.
#   - Verificar la integridad de la base recuperada.
#   - Verificar que la estructura de la BD sea válida.
#   - Reemplazar la BD actual solamente después de verificarla.
#
# IMPORTANTE:
#   Este módulo NO:
#   - genera claves.
#   - administra Windows DPAPI.
#   - crea archivos de recuperación.
#   - maneja ventanas Tkinter.
#
#   La administración de la clave pertenece a:
#       seguridad_bd.py
#
#   La recuperación de emergencia de la clave pertenece a:
#       recuperacion.py
#
# ============================================================


import os
import sys
import base64
import shutil

from sqlcipher3 import dbapi2 as sqlite3

from cryptography.fernet import Fernet

from seguridad_bd import (
    obtener_clave_bd,
    obtener_ruta_datos,
)


# ============================================================
# UBICACIÓN BASE
# ============================================================

if getattr(sys, "frozen", False):

    BASE_DIR = os.path.dirname(
        sys.executable
    )

else:

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


# ============================================================
# RUTAS
# ============================================================

RUTA_DATOS = obtener_ruta_datos()

RUTA_BASE_DATOS = os.path.join(
    RUTA_DATOS,
    "bdescuela.db"
)

CARPETA_BACKUPS = os.path.join(
    BASE_DIR,
    "Backups"
)


# ============================================================
# CONVERTIR CLAVE DE BD A CLAVE FERNET
# ============================================================

def convertir_clave_fernet(clave_bd):
    """
    Convierte la clave de la base de datos de 32 bytes
    a la representación Base64 URL-safe requerida por Fernet.
    """

    if not isinstance(clave_bd, bytes):

        raise TypeError(
            "La clave de la base de datos debe ser de tipo bytes."
        )

    if len(clave_bd) != 32:

        raise ValueError(
            "La clave de la base de datos debe tener "
            "exactamente 32 bytes."
        )

    return base64.urlsafe_b64encode(
        clave_bd
    )


# ============================================================
# OBTENER CLAVE FERNET
# ============================================================

def obtener_clave_fernet():
    """
    Obtiene la clave de la BD mediante seguridad_bd.py
    y la convierte al formato utilizado por Fernet.

    Este es el camino normal de funcionamiento.
    """

    clave_bd = obtener_clave_bd()

    return convertir_clave_fernet(
        clave_bd
    )


# ============================================================
# CONFIGURAR CLAVE SQLCIPHER
# ============================================================

def configurar_clave_sqlcipher(
    conexion,
    clave_bd
):
    """
    Configura la clave de 256 bits utilizada por SQLCipher.

    La clave se transforma a hexadecimal para evitar problemas
    con caracteres especiales dentro de PRAGMA key.
    """

    if not isinstance(clave_bd, bytes):

        raise TypeError(
            "La clave de la BD debe ser de tipo bytes."
        )

    if len(clave_bd) != 32:

        raise ValueError(
            "La clave de la BD debe tener exactamente 32 bytes."
        )

    clave_hex = clave_bd.hex()

    conexion.execute(
        f"PRAGMA key = \"x'{clave_hex}'\""
    )


# ============================================================
# DESCIFRAR BACKUP A ARCHIVO TEMPORAL
# ============================================================

def descifrar_backup_temporal(
    ruta_backup,
    ruta_temporal,
    clave_bd=None
):
    """
    Descifra la capa Fernet del backup.

    IMPORTANTE:

    El resultado NO es una SQLite normal.

    El resultado es el archivo SQLCipher que estaba dentro
    del backup.

    La función solamente genera el archivo temporal.
    Todavía NO reemplaza la base actual.

    Si clave_bd es None:
        obtiene la clave mediante seguridad_bd.py.

    Si clave_bd contiene una clave:
        utiliza directamente esa clave.
    """

    # --------------------------------------------------------
    # Verificar backup
    # --------------------------------------------------------

    if not os.path.isfile(ruta_backup):

        raise FileNotFoundError(
            "No existe el backup indicado:\n\n"
            f"{ruta_backup}"
        )

    tamaño_backup = os.path.getsize(
        ruta_backup
    )

    if tamaño_backup == 0:

        raise ValueError(
            "El archivo de backup está vacío."
        )

    # --------------------------------------------------------
    # Obtener clave
    # --------------------------------------------------------

    if clave_bd is None:

        clave_fernet = obtener_clave_fernet()

    else:

        clave_fernet = convertir_clave_fernet(
            clave_bd
        )

    # --------------------------------------------------------
    # Crear Fernet
    # --------------------------------------------------------

    fernet = Fernet(
        clave_fernet
    )

    # --------------------------------------------------------
    # Leer backup
    # --------------------------------------------------------

    with open(
        ruta_backup,
        "rb"
    ) as archivo:

        datos_cifrados = archivo.read()

    if not datos_cifrados:

        raise ValueError(
            "El archivo de backup no contiene datos."
        )

    # --------------------------------------------------------
    # Descifrar capa Fernet
    # --------------------------------------------------------

    try:

        datos_recuperados = fernet.decrypt(
            datos_cifrados
        )

    except Exception as error:

        raise RuntimeError(
            "No fue posible descifrar el backup. "
            "La clave puede ser incorrecta o el archivo "
            "puede estar dañado."
        ) from error

    if not datos_recuperados:

        raise ValueError(
            "El backup fue descifrado pero "
            "no contiene datos."
        )

    # --------------------------------------------------------
    # Preparar carpeta
    # --------------------------------------------------------

    carpeta_destino = os.path.dirname(
        os.path.abspath(
            ruta_temporal
        )
    )

    os.makedirs(
        carpeta_destino,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Escribir temporalmente
    # --------------------------------------------------------

    try:

        with open(
            ruta_temporal,
            "wb"
        ) as archivo:

            archivo.write(
                datos_recuperados
            )

            archivo.flush()

            os.fsync(
                archivo.fileno()
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

    return ruta_temporal


# ============================================================
# VERIFICAR BASE SQLCIPHER
# ============================================================

def verificar_base_sqlcipher(
    ruta_base_datos,
    clave_bd
):
    """
    Verifica que una base recuperada:

        1. exista.
        2. pueda abrirse con SQLCipher.
        3. acepte la clave correcta.
        4. supere PRAGMA integrity_check.
        5. contenga las tablas fundamentales del SGE.

    La función NO modifica la base.
    """

    if not os.path.isfile(
        ruta_base_datos
    ):

        raise FileNotFoundError(
            "No existe la base que se desea verificar:\n"
            f"{ruta_base_datos}"
        )

    conexion = None

    try:

        # ----------------------------------------------------
        # Abrir con SQLCipher
        # ----------------------------------------------------

        conexion = sqlite3.connect(
            ruta_base_datos
        )

        configurar_clave_sqlcipher(
            conexion,
            clave_bd
        )

        # ----------------------------------------------------
        # Intentar acceder a SQLite
        # ----------------------------------------------------

        conexion.execute(
            "SELECT count(*) FROM sqlite_master"
        ).fetchone()

        # ----------------------------------------------------
        # Integridad
        # ----------------------------------------------------

        resultado = conexion.execute(
            "PRAGMA integrity_check;"
        ).fetchone()

        if not resultado:

            raise RuntimeError(
                "SQLCipher no devolvió resultado "
                "de la prueba de integridad."
            )

        if resultado[0] != "ok":

            raise RuntimeError(
                "La base recuperada no superó "
                "la prueba de integridad:\n"
                f"{resultado[0]}"
            )

        # ----------------------------------------------------
        # Tablas fundamentales
        # ----------------------------------------------------

        tablas = conexion.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        ).fetchall()

        nombres_tablas = {
            fila[0]
            for fila in tablas
        }

        tablas_requeridas = {
            "usuarios",
            "profesores",
            "materias",
            "asignacion",
            "inasistencia",
            "calendario_escolar",
            "ciclo_lectivo",
            "dias_no_laborables",
        }

        faltantes = (
            tablas_requeridas
            - nombres_tablas
        )

        if faltantes:

            raise RuntimeError(
                "La base recuperada no contiene "
                "todas las tablas necesarias del SGE.\n"
                "Faltan:\n"
                + "\n".join(
                    sorted(faltantes)
                )
            )

        return True

    finally:

        if conexion is not None:

            conexion.close()


# ============================================================
# VERIFICAR ARCHIVO SQLCIPHER SIN MODIFICARLO
# ============================================================

def verificar_archivo_recuperado(
    ruta_base_datos,
    clave_bd
):
    """
    Función pública para verificar una base SQLCipher
    antes de utilizarla como base oficial del SGE.
    """

    verificar_base_sqlcipher(
        ruta_base_datos,
        clave_bd
    )

    return True


# ============================================================
# RESTAURAR BACKUP
# ============================================================

def restaurar_backup(
    ruta_backup,
    ruta_base_datos=None,
    clave_bd=None
):
    """
    Realiza una restauración segura.

    Flujo:

        backup .enc
             ↓
        descifrado Fernet
             ↓
        archivo SQLCipher temporal
             ↓
        verificación SQLCipher
             ↓
        integrity_check
             ↓
        verificación estructura SGE
             ↓
        reemplazo de la base actual
             ↓
        nueva base activa

    IMPORTANTE:

    La base actual NO se reemplaza hasta que
    la base recuperada haya superado todas
    las verificaciones.
    """

    # --------------------------------------------------------
    # Ruta de la base
    # --------------------------------------------------------

    if ruta_base_datos is None:

        ruta_base_datos = RUTA_BASE_DATOS

    # --------------------------------------------------------
    # Obtener clave
    # --------------------------------------------------------

    if clave_bd is None:

        clave_bd = obtener_clave_bd()

    # --------------------------------------------------------
    # Validar clave
    # --------------------------------------------------------

    if not isinstance(clave_bd, bytes):

        raise TypeError(
            "La clave de la BD debe ser de tipo bytes."
        )

    if len(clave_bd) != 32:

        raise ValueError(
            "La clave de la BD debe tener exactamente 32 bytes."
        )

    # --------------------------------------------------------
    # Crear carpeta
    # --------------------------------------------------------

    carpeta_base = os.path.dirname(
        os.path.abspath(
            ruta_base_datos
        )
    )

    os.makedirs(
        carpeta_base,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Archivo temporal
    # --------------------------------------------------------

    ruta_temporal = (
        ruta_base_datos
        + ".restauracion.tmp"
    )

    # --------------------------------------------------------
    # Copia de seguridad de la BD actual
    # --------------------------------------------------------

    ruta_respaldo_actual = (
        ruta_base_datos
        + ".antes_restauracion"
    )

    try:

        # ----------------------------------------------------
        # 1. Descifrar backup
        # ----------------------------------------------------

        descifrar_backup_temporal(
            ruta_backup,
            ruta_temporal,
            clave_bd
        )

        # ----------------------------------------------------
        # 2. Verificar SQLCipher
        # ----------------------------------------------------

        verificar_base_sqlcipher(
            ruta_temporal,
            clave_bd
        )

        # ----------------------------------------------------
        # 3. Respaldar la BD actual
        # ----------------------------------------------------

        if os.path.exists(
            ruta_base_datos
        ):

            if os.path.exists(
                ruta_respaldo_actual
            ):

                os.remove(
                    ruta_respaldo_actual
                )

            shutil.copy2(
                ruta_base_datos,
                ruta_respaldo_actual
            )

        # ----------------------------------------------------
        # 4. Reemplazar la BD
        # ----------------------------------------------------

        os.replace(
            ruta_temporal,
            ruta_base_datos
        )

        # ----------------------------------------------------
        # 5. Verificación final
        # ----------------------------------------------------

        try:

            verificar_base_sqlcipher(
                ruta_base_datos,
                clave_bd
            )

        except Exception:

            # -----------------------------------------------
            # Si algo falla después del reemplazo,
            # intentar recuperar la base anterior.
            # -----------------------------------------------

            if os.path.exists(
                ruta_respaldo_actual
            ):

                try:

                    if os.path.exists(
                        ruta_base_datos
                    ):

                        os.remove(
                            ruta_base_datos
                        )

                    os.replace(
                        ruta_respaldo_actual,
                        ruta_base_datos
                    )

                except Exception:
                    pass

            raise

        return ruta_base_datos

    except Exception:

        # ----------------------------------------------------
        # Limpiar temporal
        # ----------------------------------------------------

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


# ============================================================
# COMPARAR ARCHIVOS
# ============================================================

def comparar_archivos(
    ruta_archivo_1,
    ruta_archivo_2
):
    """
    Compara dos archivos byte por byte.

    Esta función se conserva como herramienta de prueba.

    IMPORTANTE:

    Dos bases SQLCipher válidas pueden contener exactamente
    los mismos datos sin necesariamente tener que ser
    byte por byte idénticas después de una operación de
    backup/restauración.

    Por eso esta función NO se utiliza para decidir si una
    restauración es válida.
    """

    if not os.path.isfile(
        ruta_archivo_1
    ):

        raise FileNotFoundError(
            f"No existe:\n{ruta_archivo_1}"
        )

    if not os.path.isfile(
        ruta_archivo_2
    ):

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
    ruta_base_datos=None
):
    """
    Realiza una recuperación completa utilizando:

        - archivo de recuperación externo
        - frase de recuperación
        - backup cifrado

    IMPORTANTE:

    La recuperación de emergencia debe devolver la clave
    de la BD de 32 bytes.

    El módulo recuperacion.py será el responsable de
    obtener esa clave.

    Flujo:

        archivo + frase
              ↓
        recuperacion.py
              ↓
        clave_bd
              ↓
        backup Fernet
              ↓
        base SQLCipher
              ↓
        verificación
              ↓
        restauración segura
    """

    # --------------------------------------------------------
    # Importación local
    # --------------------------------------------------------

    try:

        from recuperacion import (
            recuperar_clave_bd
        )

    except ImportError as error:

        raise RuntimeError(
            "El módulo recuperacion.py todavía no está "
            "adaptado a la nueva arquitectura de seguridad."
        ) from error

    # --------------------------------------------------------
    # Recuperar clave BD
    # --------------------------------------------------------

    clave_bd = recuperar_clave_bd(
        frase_recuperacion,
        ruta_archivo_recuperacion
    )

    # --------------------------------------------------------
    # Restaurar
    # --------------------------------------------------------

    return restaurar_backup(
        ruta_backup,
        ruta_base_datos,
        clave_bd
    )


# ============================================================
# INFORMACIÓN DE RUTAS
# ============================================================

def obtener_rutas_restauracion():
    """
    Devuelve las rutas principales utilizadas por
    el sistema de restauración.
    """

    return {
        "datos": RUTA_DATOS,
        "base_datos": RUTA_BASE_DATOS,
        "backups": CARPETA_BACKUPS,
    }


# ============================================================
# PRUEBA DIRECTA DEL MÓDULO
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print("PRUEBA DEL MÓDULO restauracion_nueva.py")
    print("=" * 80)

    try:

        # ----------------------------------------------------
        # Mostrar rutas
        # ----------------------------------------------------

        print()
        print("Base de datos del SGE:")
        print(RUTA_BASE_DATOS)

        print()
        print("Carpeta de backups:")
        print(CARPETA_BACKUPS)

        # ----------------------------------------------------
        # Buscar backups
        # ----------------------------------------------------

        if not os.path.isdir(
            CARPETA_BACKUPS
        ):

            raise FileNotFoundError(
                "No existe la carpeta Backups."
            )

        archivos_backup = [
            archivo
            for archivo in os.listdir(
                CARPETA_BACKUPS
            )
            if archivo.lower().endswith(
                ".enc"
            )
        ]

        if not archivos_backup:

            raise FileNotFoundError(
                "No se encontró ningún backup .enc."
            )

        archivos_backup.sort()

        nombre_backup = (
            archivos_backup[-1]
        )

        ruta_backup = os.path.join(
            CARPETA_BACKUPS,
            nombre_backup
        )

        # ----------------------------------------------------
        # Archivo de prueba
        # ----------------------------------------------------

        ruta_prueba = os.path.join(
            RUTA_DATOS,
            "bdescuela_restauracion_prueba.db"
        )

        # ----------------------------------------------------
        # Mostrar backup
        # ----------------------------------------------------

        print()
        print("Backup seleccionado:")
        print(ruta_backup)

        print()
        print("Base que se utilizará para la prueba:")
        print(ruta_prueba)

        # ----------------------------------------------------
        # Obtener clave
        # ----------------------------------------------------

        print()
        print("Obteniendo clave de la BD...")

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

        # ----------------------------------------------------
        # Descifrar a archivo temporal de prueba
        # ----------------------------------------------------

        ruta_temporal = (
            ruta_prueba
            + ".tmp"
        )

        print()
        print("Descifrando backup...")

        descifrar_backup_temporal(
            ruta_backup,
            ruta_temporal,
            clave
        )

        print(
            "Backup descifrado correctamente."
        )

        # ----------------------------------------------------
        # Verificar SQLCipher
        # ----------------------------------------------------

        print()
        print(
            "Verificando base recuperada..."
        )

        verificar_base_sqlcipher(
            ruta_temporal,
            clave
        )

        print(
            "La base recuperada superó "
            "la verificación SQLCipher."
        )

        # ----------------------------------------------------
        # Reemplazar archivo de prueba
        # ----------------------------------------------------

        if os.path.exists(
            ruta_prueba
        ):

            os.remove(
                ruta_prueba
            )

        os.replace(
            ruta_temporal,
            ruta_prueba
        )

        # ----------------------------------------------------
        # Mostrar tablas
        # ----------------------------------------------------

        conexion = sqlite3.connect(
            ruta_prueba
        )

        try:

            configurar_clave_sqlcipher(
                conexion,
                clave
            )

            tablas = conexion.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                ORDER BY name
                """
            ).fetchall()

            print()
            print("Tablas recuperadas:")

            for tabla in tablas:

                print(
                    " -",
                    tabla[0]
                )

        finally:

            conexion.close()

        # ----------------------------------------------------
        # Resultado
        # ----------------------------------------------------

        print()
        print("=" * 80)
        print("PRUEBA FINALIZADA CORRECTAMENTE")
        print("=" * 80)

        print()
        print("Se comprobó:")

        print("✔ backup encontrado")
        print("✔ clave de BD obtenida")
        print("✔ backup Fernet descifrado")
        print("✔ archivo SQLCipher generado")
        print("✔ clave SQLCipher aceptada")
        print("✔ integrity_check correcto")
        print("✔ estructura del SGE recuperada")
        print("✔ base restaurada en archivo de prueba")

        print()
        print("Archivo de prueba:")
        print(ruta_prueba)

    except Exception as error:

        print()
        print("=" * 80)
        print("ERROR DURANTE LA PRUEBA")
        print("=" * 80)

        print()
        print(str(error))

        print()
        print("La base oficial del SGE NO fue modificada.")

        print()
        print("=" * 80)
        

