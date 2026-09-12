# ============================================================
# prueba_recuperacion_nueva.py
# Sistema de Gestión Educativa (SGE)
#
# LABORATORIO:
#   Recuperación ante desastre sin utilizar Windows DPAPI
#
# OBJETIVO:
#   Simular una nueva instalación del SGE en una computadora
#   donde ya no existe la protección DPAPI de la instalación
#   anterior.
#
#   La recuperación utilizará únicamente:
#
#       1. Backup cifrado
#       2. Archivo de recuperación
#       3. Clave de recuperación
#
# RESULTADO ESPERADO:
#
#   RECUPERACION_SGE_NUEVA
#              │
#              ↓
#       recuperar clave de datos
#              │
#              ↓
#        descifrar backup
#              │
#              ↓
#      NUEVA_INSTALACION_SGE
#              │
#              ↓
#        bdescuela.db
#
# IMPORTANTE:
#   Este laboratorio NO utiliza:
#
#       - seguridad.py
#       - Windows DPAPI
#       - bdescuela.db original
#       - clave_datos_sge.protegida
#
#   Tampoco modifica el backup original.
# ============================================================

import os
import sys
import base64
import sqlite3

from cryptography.fernet import Fernet, InvalidToken


# ------------------------------------------------------------
# UBICACIÓN BASE
# ------------------------------------------------------------

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# CARPETAS DEL LABORATORIO
# ------------------------------------------------------------

CARPETA_RECUPERACION = os.path.join(
    BASE_DIR,
    "RECUPERACION_SGE_NUEVA"
)

CARPETA_NUEVA_INSTALACION = os.path.join(
    BASE_DIR,
    "NUEVA_INSTALACION_SGE"
)


# ------------------------------------------------------------
# ARCHIVOS DE RECUPERACIÓN
# ------------------------------------------------------------

NOMBRE_BACKUP = "backup_sge_20260911_175705.enc"

NOMBRE_ARCHIVO_RECUPERACION = (
    "clave_datos_sge.recuperacion"
)

NOMBRE_CLAVE_RECUPERACION = (
    "clave_recuperacion_sge.key"
)


# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------

RUTA_BACKUP = os.path.join(
    CARPETA_RECUPERACION,
    NOMBRE_BACKUP
)

RUTA_ARCHIVO_RECUPERACION = os.path.join(
    CARPETA_RECUPERACION,
    NOMBRE_ARCHIVO_RECUPERACION
)

RUTA_CLAVE_RECUPERACION = os.path.join(
    CARPETA_RECUPERACION,
    NOMBRE_CLAVE_RECUPERACION
)

RUTA_NUEVA_BASE = os.path.join(
    CARPETA_NUEVA_INSTALACION,
    "bdescuela.db"
)


# ------------------------------------------------------------
# VERIFICAR ARCHIVOS
# ------------------------------------------------------------

def verificar_archivos_recuperacion():

    archivos = [
        RUTA_BACKUP,
        RUTA_ARCHIVO_RECUPERACION,
        RUTA_CLAVE_RECUPERACION
    ]

    for ruta in archivos:

        if not os.path.isfile(ruta):

            raise FileNotFoundError(
                "No se encontró el archivo necesario "
                "para la recuperación:\n\n"
                f"{ruta}"
            )


# ------------------------------------------------------------
# RECUPERAR CLAVE DE DATOS
# ------------------------------------------------------------

def recuperar_clave_datos():

    with open(
        RUTA_CLAVE_RECUPERACION,
        "rb"
    ) as archivo:

        clave_recuperacion = archivo.read()

    if not clave_recuperacion:

        raise ValueError(
            "La clave de recuperación está vacía."
        )

    with open(
        RUTA_ARCHIVO_RECUPERACION,
        "rb"
    ) as archivo:

        datos_protegidos = archivo.read()

    if not datos_protegidos:

        raise ValueError(
            "El archivo de recuperación está vacío."
        )

    fernet_recuperacion = Fernet(
        clave_recuperacion
    )

    try:

        clave_datos = (
            fernet_recuperacion.decrypt(
                datos_protegidos
            )
        )

    except InvalidToken as error:

        raise RuntimeError(
            "No fue posible recuperar la clave de datos.\n\n"
            "El paquete de recuperación puede estar "
            "dañado o no corresponde con la clave."
        ) from error

    if len(clave_datos) != 32:

        raise ValueError(
            "La clave de datos recuperada no tiene "
            "exactamente 32 bytes."
        )

    return clave_datos


# ------------------------------------------------------------
# CREAR CLAVE FERNET PARA EL BACKUP
# ------------------------------------------------------------

def crear_clave_fernet(clave_datos):

    if not isinstance(
        clave_datos,
        bytes
    ):

        raise TypeError(
            "La clave de datos debe ser bytes."
        )

    if len(clave_datos) != 32:

        raise ValueError(
            "La clave de datos debe tener "
            "exactamente 32 bytes."
        )

    return base64.urlsafe_b64encode(
        clave_datos
    )


# ------------------------------------------------------------
# DESCIFRAR BACKUP
# ------------------------------------------------------------

def descifrar_backup(
    clave_datos
):

    clave_fernet = crear_clave_fernet(
        clave_datos
    )

    fernet = Fernet(
        clave_fernet
    )

    with open(
        RUTA_BACKUP,
        "rb"
    ) as archivo:

        datos_cifrados = archivo.read()

    if not datos_cifrados:

        raise ValueError(
            "El backup cifrado está vacío."
        )

    try:

        datos_recuperados = (
            fernet.decrypt(
                datos_cifrados
            )
        )

    except InvalidToken as error:

        raise RuntimeError(
            "El backup no pudo ser descifrado.\n\n"
            "El backup puede estar dañado, alterado "
            "o no corresponder con la clave de datos."
        ) from error

    if not datos_recuperados:

        raise ValueError(
            "El backup fue descifrado pero "
            "no contiene datos."
        )

    os.makedirs(
        CARPETA_NUEVA_INSTALACION,
        exist_ok=True
    )

    ruta_temporal = (
        RUTA_NUEVA_BASE + ".tmp"
    )

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

        os.replace(
            ruta_temporal,
            RUTA_NUEVA_BASE
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

    return RUTA_NUEVA_BASE


# ------------------------------------------------------------
# VERIFICAR SQLITE
# ------------------------------------------------------------

def verificar_sqlite():

    if not os.path.isfile(
        RUTA_NUEVA_BASE
    ):

        raise FileNotFoundError(
            "No se creó la base de datos "
            "de la nueva instalación."
        )

    conexion = sqlite3.connect(
        RUTA_NUEVA_BASE
    )

    try:

        resultado = conexion.execute(
            "PRAGMA integrity_check;"
        ).fetchone()

        if not resultado:

            raise RuntimeError(
                "SQLite no devolvió resultado "
                "de integridad."
            )

        if resultado[0] != "ok":

            raise RuntimeError(
                "La base recuperada no superó "
                "la prueba de integridad:\n"
                f"{resultado[0]}"
            )

    finally:

        conexion.close()

    return True


# ------------------------------------------------------------
# OBTENER TABLAS
# ------------------------------------------------------------

def obtener_tablas():

    conexion = sqlite3.connect(
        RUTA_NUEVA_BASE
    )

    try:

        filas = conexion.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name;
            """
        ).fetchall()

    finally:

        conexion.close()

    return [
        fila[0]
        for fila in filas
    ]


# ------------------------------------------------------------
# TABLAS ESPERADAS DEL SGE
# ------------------------------------------------------------

TABLAS_ESPERADAS = [
    "usuarios",
    "profesores",
    "materias",
    "asignacion",
    "inasistencia",
    "calendario_escolar",
    "ciclo_lectivo",
    "dias_no_laborables"
]


# ------------------------------------------------------------
# VERIFICAR TABLAS DEL SGE
# ------------------------------------------------------------

def verificar_tablas():

    tablas = obtener_tablas()

    faltantes = [
        tabla
        for tabla in TABLAS_ESPERADAS
        if tabla not in tablas
    ]

    if faltantes:

        raise RuntimeError(
            "Faltan tablas esperadas del SGE:\n\n"
            + "\n".join(faltantes)
        )

    return tablas


# ------------------------------------------------------------
# PRUEBA PRINCIPAL
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("RECUPERACIÓN DEL SGE SIN DPAPI")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # 1. Preparar nueva instalación
        # ----------------------------------------------------

        print()
        print("🖥️ SIMULANDO NUEVA INSTALACIÓN DEL SGE")

        os.makedirs(
            CARPETA_NUEVA_INSTALACION,
            exist_ok=True
        )

        # Si existe una base de una prueba anterior,
        # la eliminamos para comenzar desde cero.

        if os.path.exists(
            RUTA_NUEVA_BASE
        ):

            os.remove(
                RUTA_NUEVA_BASE
            )

        print()
        print(
            "📁 Nueva instalación:"
        )

        print(
            CARPETA_NUEVA_INSTALACION
        )

        # ----------------------------------------------------
        # 2. Verificar paquete
        # ----------------------------------------------------

        print()
        print(
            "📦 VERIFICANDO PAQUETE DE RECUPERACIÓN..."
        )

        verificar_archivos_recuperacion()

        print()
        print(
            "✅ Backup cifrado encontrado."
        )

        print(
            "✅ Archivo de recuperación encontrado."
        )

        print(
            "✅ Clave de recuperación encontrada."
        )

        # ----------------------------------------------------
        # 3. Recuperar clave sin DPAPI
        # ----------------------------------------------------

        print()
        print(
            "🔑 Recuperando clave de datos..."
        )

        print(
            "   Método utilizado:"
        )

        print(
            "   📦 Paquete de recuperación"
        )

        print(
            "   ❌ No se utiliza DPAPI"
        )

        clave_datos = recuperar_clave_datos()

        print()
        print(
            "✅ Clave de datos recuperada."
        )

        print()
        print(
            "Cantidad de bytes:",
            len(clave_datos)
        )

        print(
            "Cantidad de bits:",
            len(clave_datos) * 8
        )

        # ----------------------------------------------------
        # 4. Descifrar backup
        # ----------------------------------------------------

        print()
        print(
            "🔓 Descifrando backup..."
        )

        descifrar_backup(
            clave_datos
        )

        print()
        print(
            "✅ Backup descifrado correctamente."
        )

        # ----------------------------------------------------
        # 5. Verificar SQLite
        # ----------------------------------------------------

        print()
        print(
            "🧪 Verificando integridad de SQLite..."
        )

        verificar_sqlite()

        print()
        print(
            "✅ La base recuperada es una SQLite válida."
        )

        # ----------------------------------------------------
        # 6. Verificar tablas
        # ----------------------------------------------------

        print()
        print(
            "🔍 Verificando estructura del SGE..."
        )

        tablas = verificar_tablas()

        print()

        print(
            "Tablas encontradas:"
        )

        for tabla in tablas:

            print(
                "   ✔",
                tabla
            )

        # ----------------------------------------------------
        # 7. Verificar base creada
        # ----------------------------------------------------

        tamaño = os.path.getsize(
            RUTA_NUEVA_BASE
        )

        print()
        print(
            "📊 Tamaño de la base recuperada:"
        )

        print(
            tamaño,
            "bytes"
        )

        # ----------------------------------------------------
        # RESULTADO FINAL
        # ----------------------------------------------------

        print()
        print(
            "🎉 RECUPERACIÓN EXITOSA."
        )

        print()
        print(
            "La nueva instalación del SGE "
            "pudo reconstruir la base de datos."
        )

        print()
        print(
            "La recuperación utilizó únicamente:"
        )

        print(
            "   🔐 paquete de recuperación"
        )

        print(
            "   📦 backup cifrado"
        )

        print()
        print(
            "No fue necesaria:"
        )

        print(
            "   ❌ la base de datos original"
        )

        print(
            "   ❌ la protección DPAPI anterior"
        )

        print(
            "   ❌ la instalación anterior"
        )

        print()
        print("=" * 60)
        print(
            "LABORATORIO FINALIZADO"
        )
        print("=" * 60)

    except Exception as error:

        print()
        print(
            "❌ ERROR DURANTE LA RECUPERACIÓN"
        )

        print()
        print(
            str(error)
        )

        print()
        print("=" * 60)

