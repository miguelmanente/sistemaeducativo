# =====================================================
#            MÓDULO CREACIÓN DE TABLAS DE LA BD
# =====================================================

# ------------------------ LIBRERÍAS -------------------

from sqlcipher3 import dbapi2 as sqlite3
import hashlib
import os
import shutil

import seguridad_bd


# =====================================================
#              OBTENER RUTA DE LA BASE
# =====================================================

def obtener_ruta_bd():

    ruta_datos = (
        seguridad_bd.obtener_ruta_datos()
    )

    os.makedirs(
        ruta_datos,
        exist_ok=True
    )

    return os.path.join(
        ruta_datos,
        "bdescuela.db"
    )


# =====================================================
#          OBTENER RUTA DE LA BASE ANTIGUA
# =====================================================

def obtener_ruta_bd_antigua():

    if getattr(
        __import__("sys"),
        "frozen",
        False
    ):

        base_dir = os.path.dirname(
            __import__("sys").executable
        )

    else:

        base_dir = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_dir,
        "bdescuela.db"
    )


# =====================================================
#       CONFIGURAR CLAVE DE SQLCIPHER
# =====================================================

def configurar_clave_sqlcipher(
    conexion,
    clave
):

    if not isinstance(
        clave,
        bytes
    ):
        raise TypeError(
            "La clave de la base de datos "
            "debe ser de tipo bytes."
        )

    if len(clave) != 32:
        raise ValueError(
            "La clave de la base de datos "
            "debe tener exactamente 32 bytes."
        )

    clave_sql = clave.hex()

    conexion.execute(
        f'PRAGMA key = "x\'{clave_sql}\'"'
    )


# =====================================================
#       VERIFICAR BASE SQLCIPHER
# =====================================================

def verificar_bd_sqlcipher(
    ruta_bd,
    clave
):

    if not os.path.isfile(
        ruta_bd
    ):
        return False

    conexion = None

    try:

        conexion = sqlite3.connect(
            ruta_bd
        )

        configurar_clave_sqlcipher(
            conexion,
            clave
        )

        conexion.execute(
            "SELECT count(*) FROM sqlite_master"
        ).fetchone()

        return True

    except Exception:

        return False

    finally:

        if conexion is not None:

            conexion.close()


# =====================================================
#       VERIFICAR BASE SQLITE NORMAL
# =====================================================

def verificar_bd_sqlite_normal(
    ruta_bd
):

    if not os.path.isfile(
        ruta_bd
    ):
        return False

    # -------------------------------------------------
    # Importamos sqlite3 estándar únicamente para
    # comprobar si la base antigua es una SQLite
    # normal.
    # -------------------------------------------------

    import sqlite3 as sqlite_normal

    conexion = None

    try:

        conexion = sqlite_normal.connect(
            ruta_bd
        )

        conexion.execute(
            "SELECT count(*) FROM sqlite_master"
        ).fetchone()

        return True

    except Exception:

        return False

    finally:

        if conexion is not None:

            conexion.close()


# =====================================================
#       MIGRAR BASE ANTIGUA
# =====================================================

def migrar_base_antigua():

    """
    Migra la base antigua ubicada junto al programa
    hacia:

        Datos\bdescuela.db

    Se contemplan dos situaciones:

    1. La base antigua ya está cifrada con SQLCipher.
       En ese caso se copia conservando su contenido.

    2. La base antigua todavía es SQLite normal.
       En ese caso se importa y se crea una nueva
       base SQLCipher.

    La base antigua nunca se elimina automáticamente.
    """

    ruta_nueva = obtener_ruta_bd()

    ruta_antigua = obtener_ruta_bd_antigua()

    # -------------------------------------------------
    # Si no existe la base antigua, no hay nada
    # que migrar.
    # -------------------------------------------------

    if not os.path.isfile(
        ruta_antigua
    ):

        return False

    # -------------------------------------------------
    # Si la base nueva ya existe, no hacemos nada.
    # -------------------------------------------------

    if os.path.isfile(
        ruta_nueva
    ):

        return False

    print()
    print(
        "================================================="
    )
    print(
        "MIGRACIÓN DE LA BASE DE DATOS"
    )
    print(
        "================================================="
    )

    print()
    print(
        "Base antigua detectada:"
    )

    print(
        ruta_antigua
    )

    print()
    print(
        "Nueva ubicación:"
    )

    print(
        ruta_nueva
    )

    # -------------------------------------------------
    # Obtener la clave de la instalación.
    #
    # Si la base antigua ya era SQLCipher, esta será
    # la clave con la que fue creada.
    #
    # Si era SQLite normal, se crea una nueva clave
    # porque ahora será necesario cifrarla.
    # -------------------------------------------------

    try:

        clave = seguridad_bd.obtener_clave_bd()

        print()
        print(
            "Clave de BD existente encontrada."
        )

    except FileNotFoundError:

        print()
        print(
            "No existe una clave de BD protegida."
        )

        print(
            "La base antigua será migrada a una "
            "nueva base SQLCipher."
        )

        clave = seguridad_bd.crear_clave_bd()

        print(
            "Nueva clave de BD creada correctamente."
        )

    # =================================================
    # INTENTO 1:
    # LA BASE ANTIGUA YA ES SQLCIPHER
    # =================================================

    if verificar_bd_sqlcipher(
        ruta_antigua,
        clave
    ):

        print()
        print(
            "La base antigua ya está cifrada "
            "mediante SQLCipher."
        )

        # -------------------------------------------------
        # Copiamos el archivo directamente.
        #
        # Esto conserva el cifrado existente.
        # -------------------------------------------------

        shutil.copy2(
            ruta_antigua,
            ruta_nueva
        )

        print()
        print(
            "Base SQLCipher trasladada correctamente."
        )

        return True

    # =================================================
    # INTENTO 2:
    # LA BASE ANTIGUA ES SQLITE NORMAL
    # =================================================

    if verificar_bd_sqlite_normal(
        ruta_antigua
    ):

        print()
        print(
            "La base antigua es SQLite normal."
        )

        print(
            "Se realizará una migración hacia SQLCipher."
        )

        migrar_sqlite_normal_a_sqlcipher(
            ruta_antigua,
            ruta_nueva,
            clave
        )

        print()
        print(
            "Migración a SQLCipher completada."
        )

        return True

    # =================================================
    # BASE NO RECONOCIDA
    # =================================================

    raise RuntimeError(
        "La base de datos antigua existe pero "
        "no pudo ser reconocida como SQLite normal "
        "ni como SQLCipher compatible con la clave "
        "de esta instalación."
    )


# =====================================================
# MIGRAR SQLITE NORMAL A SQLCIPHER
# =====================================================

def migrar_sqlite_normal_a_sqlcipher(
    ruta_origen,
    ruta_destino,
    clave
):

    """
    Convierte una base SQLite normal en una nueva
    base SQLCipher.

    La base original permanece intacta.
    """

    import sqlite3 as sqlite_normal

    conexion_origen = None
    conexion_destino = None

    try:

        # -------------------------------------------------
        # Abrir base SQLite normal.
        # -------------------------------------------------

        conexion_origen = sqlite_normal.connect(
            ruta_origen
        )

        # -------------------------------------------------
        # Verificar que realmente pueda leerse.
        # -------------------------------------------------

        conexion_origen.execute(
            "SELECT count(*) FROM sqlite_master"
        ).fetchone()

        # -------------------------------------------------
        # Crear nueva base SQLCipher.
        # -------------------------------------------------

        conexion_destino = sqlite3.connect(
            ruta_destino
        )

        configurar_clave_sqlcipher(
            conexion_destino,
            clave
        )

        # -------------------------------------------------
        # Obtener la estructura completa de la base.
        # -------------------------------------------------

        objetos = conexion_origen.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE sql IS NOT NULL
            AND name NOT LIKE 'sqlite_%'
            ORDER BY
                CASE type
                    WHEN 'table' THEN 1
                    WHEN 'index' THEN 2
                    WHEN 'trigger' THEN 3
                    WHEN 'view' THEN 4
                    ELSE 5
                END,
                name
            """
        ).fetchall()

        # -------------------------------------------------
        # Crear primero tablas.
        # -------------------------------------------------

        for tipo, nombre, sql in objetos:

            if tipo == "table":

                conexion_destino.execute(
                    sql
                )

        # -------------------------------------------------
        # Copiar los datos de las tablas.
        # -------------------------------------------------

        tablas = conexion_origen.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        for fila in tablas:

            nombre_tabla = fila[0]

            columnas = conexion_origen.execute(
                f"""
                PRAGMA table_info(
                    "{nombre_tabla}"
                )
                """
            ).fetchall()

            nombres_columnas = [
                columna[1]
                for columna in columnas
            ]

            if not nombres_columnas:
                continue

            columnas_sql = ", ".join(
                f'"{columna}"'
                for columna in nombres_columnas
            )

            marcadores = ", ".join(
                "?"
                for _ in nombres_columnas
            )

            registros = conexion_origen.execute(
                f"""
                SELECT {columnas_sql}
                FROM "{nombre_tabla}"
                """
            ).fetchall()

            if registros:

                conexion_destino.executemany(
                    f"""
                    INSERT INTO "{nombre_tabla}"
                    ({columnas_sql})
                    VALUES ({marcadores})
                    """,
                    registros
                )

        # -------------------------------------------------
        # Crear índices, triggers y vistas.
        # -------------------------------------------------

        for tipo, nombre, sql in objetos:

            if tipo in (
                "index",
                "trigger",
                "view"
            ):

                try:

                    conexion_destino.execute(
                        sql
                    )

                except Exception as error:

                    print(
                        f"Advertencia al crear "
                        f"{tipo} '{nombre}': "
                        f"{error}"
                    )

        # -------------------------------------------------
        # Confirmar migración.
        # -------------------------------------------------

        conexion_destino.commit()

        # -------------------------------------------------
        # Verificación básica.
        # -------------------------------------------------

        resultado = conexion_destino.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        if not resultado:

            raise RuntimeError(
                "No se pudo verificar la integridad "
                "de la base migrada."
            )

        if resultado[0] != "ok":

            raise RuntimeError(
                "La base migrada no superó "
                "la comprobación de integridad."
            )

    except Exception:

        # -------------------------------------------------
        # Si la migración falla, eliminar solamente
        # la nueva base incompleta.
        #
        # La base original permanece intacta.
        # -------------------------------------------------

        if conexion_destino is not None:

            try:

                conexion_destino.close()

            except Exception:
                pass

            conexion_destino = None

        if os.path.exists(
            ruta_destino
        ):

            try:

                os.remove(
                    ruta_destino
                )

            except OSError:
                pass

        raise

    finally:

        if conexion_origen is not None:

            conexion_origen.close()

        if conexion_destino is not None:

            conexion_destino.close()


# =====================================================
#              CONEXIÓN A LA BASE DE DATOS
# =====================================================

def conectar():

    DATABASE = obtener_ruta_bd()

    # -------------------------------------------------
    # Intentar primero migrar una base antigua.
    #
    # Esto se ejecuta únicamente si existe una base
    # antigua y todavía no existe la nueva.
    # -------------------------------------------------

    if not os.path.exists(
        DATABASE
    ):

        migrar_base_antigua()

    # -------------------------------------------------
    # Si después de la migración sigue sin existir,
    # estamos ante una instalación completamente nueva.
    # -------------------------------------------------

    if not os.path.exists(
        DATABASE
    ):

        print(
            "--> Base de datos nueva."
        )

        print(
            "--> Generando clave segura de la BD..."
        )

        try:

            clave = seguridad_bd.obtener_clave_bd()

        except FileNotFoundError:

            clave = seguridad_bd.crear_clave_bd()

    else:

        # -------------------------------------------------
        # La BD ya existe.
        #
        # Siempre recuperamos la clave protegida.
        #
        # NUNCA generamos una clave nueva para una BD
        # existente.
        # -------------------------------------------------

        clave = seguridad_bd.obtener_clave_bd()

    # =================================================
    #        CONEXIÓN MEDIANTE SQLCIPHER
    # =================================================

    conn = sqlite3.connect(
        DATABASE
    )

    # -------------------------------------------------
    # Configurar clave.
    # -------------------------------------------------

    configurar_clave_sqlcipher(
        conn,
        clave
    )

    # -------------------------------------------------
    # Activar claves foráneas.
    # -------------------------------------------------

    conn.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return conn


# =====================================================
#              ENCRIPTAR CONTRASEÑA
# =====================================================

def hash_password(
    password
):

    return hashlib.sha256(
        password.encode()
    ).hexdigest()


# =====================================================
#              REGISTRAR NUEVO USUARIO
# =====================================================

def registrar_usuario(
    username,
    password
):

    conn = None

    try:

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios
            (
                username,
                password,
                rol
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                "USUARIO"
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    except Exception as e:

        print(
            "Error al registrar usuario:",
            e
        )

        return False

    finally:

        if conn:

            conn.close()


# =====================================================
#        VALIDAR LOGIN NORMAL DEL SISTEMA
# =====================================================

def validar_usuario(
    username,
    password
):

    conn = None

    try:

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE username = ?
            AND password = ?
            """,
            (
                username,
                hash_password(password)
            )
        )

        usuario = cursor.fetchone()

        return usuario

    except Exception as e:

        print(
            "Error al validar usuario:",
            e
        )

        return None

    finally:

        if conn:

            conn.close()


# =====================================================
#       VALIDAR QUE EL USUARIO SEA ADMINISTRADOR
# =====================================================

def validar_administrador(
    username,
    password
):

    conn = None

    try:

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id_usuario, username, rol
            FROM usuarios
            WHERE username = ?
            AND password = ?
            AND rol = 'ADMIN'
            """,
            (
                username,
                hash_password(password)
            )
        )

        administrador = cursor.fetchone()

        return administrador

    except Exception as e:

        print(
            "Error al validar administrador:",
            e
        )

        return None

    finally:

        if conn:

            conn.close()


# =====================================================
#          VERIFICAR SI EXISTE UN ADMINISTRADOR
# =====================================================

def existe_administrador():

    conn = None

    try:

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM usuarios
            WHERE rol = 'ADMIN'
            """
        )

        cantidad = cursor.fetchone()[0]

        return cantidad > 0

    except Exception as e:

        print(
            "Error al verificar administrador:",
            e
        )

        return False

    finally:

        if conn:

            conn.close()


# =====================================================
#          CREAR ADMINISTRADOR INICIAL
# =====================================================

def crear_administrador(
    username,
    password
):

    conn = None

    try:

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM usuarios
            WHERE rol = 'ADMIN'
            """
        )

        if cursor.fetchone()[0] > 0:

            return False

        cursor.execute(
            """
            INSERT INTO usuarios
            (
                username,
                password,
                rol
            )
            VALUES (?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                "ADMIN"
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    except Exception as e:

        print(
            "Error al crear administrador:",
            e
        )

        return False

    finally:

        if conn:

            conn.close()


# =====================================================
#              CREAR Y VERIFICAR TABLAS
# =====================================================

def crear_tablas():

    conn = conectar()

    cursor = conn.cursor()

    cursor.executescript(
        """

        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            rol TEXT NOT NULL DEFAULT 'USUARIO'
        );


        CREATE TABLE IF NOT EXISTS profesores (
            id_docente INTEGER PRIMARY KEY AUTOINCREMENT,
            apellido TEXT,
            nombre TEXT,
            dni TEXT,
            cuil TEXT,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            fecha_nacimiento TEXT
        );


        CREATE TABLE IF NOT EXISTS materias (
            id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            descripcion TEXT
        );


        CREATE TABLE IF NOT EXISTS asignacion (
            id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_docente INTEGER,
            id_materia INTEGER NULL,
            dia TEXT,
            cargo TEXT,
            modulos INTEGER DEFAULT 0,
            curso TEXT,
            turno TEXT,
            hentrada TEXT,
            hsalida TEXT,
            situacion_revista TEXT,
            toma_pos TEXT,
            fecha_cese TEXT NULL,
            activo INTEGER DEFAULT 1,

            FOREIGN KEY (id_docente)
                REFERENCES profesores(id_docente),

            FOREIGN KEY (id_materia)
                REFERENCES materias(id_materia)
        );


        CREATE TABLE IF NOT EXISTS inasistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_docente INTEGER,
            fecha_desde TEXT,
            fecha_hasta TEXT,
            motivo TEXT,
            observacion TEXT
        );


        CREATE TABLE IF NOT EXISTS calendario_escolar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            dia_semana TEXT NOT NULL,
            es_habil INTEGER DEFAULT 1,
            es_feriado INTEGER DEFAULT 0,
            descripcion TEXT
        );


        CREATE TABLE IF NOT EXISTS ciclo_lectivo (
            anio INTEGER PRIMARY KEY,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            observacion TEXT
        );


        CREATE TABLE IF NOT EXISTS dias_no_laborables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anio INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descripcion TEXT,
            UNIQUE(anio, fecha)
        );

        """
    )

    # =================================================
    #        MIGRACIÓN DE LA TABLA USUARIOS
    # =================================================

    cursor.execute(
        "PRAGMA table_info(usuarios)"
    )

    columnas = [
        fila[1]
        for fila in cursor.fetchall()
    ]

    if "rol" not in columnas:

        cursor.execute(
            """
            ALTER TABLE usuarios
            ADD COLUMN rol TEXT NOT NULL DEFAULT 'USUARIO'
            """
        )

        print(
            "--> Campo 'rol' agregado "
            "a la tabla usuarios."
        )

    # =================================================
    #     ADMINISTRADOR INICIAL
    # =================================================

    cursor.execute(
        "SELECT COUNT(*) FROM usuarios"
    )

    cantidad_usuarios = (
        cursor.fetchone()[0]
    )

    if cantidad_usuarios == 0:

        clave_encriptada = hash_password(
            "admin123"
        )

        cursor.execute(
            """
            INSERT INTO usuarios
            (
                username,
                password,
                rol
            )
            VALUES (?, ?, ?)
            """,
            (
                "admin",
                clave_encriptada,
                "ADMIN"
            )
        )

        print(
            "--> Usuario administrador "
            "inicial creado."
        )

    # =================================================
    #     COMPATIBILIDAD CON INSTALACIONES ANTERIORES
    # =================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE rol = 'ADMIN'
        """
    )

    cantidad_admin = (
        cursor.fetchone()[0]
    )

    if cantidad_admin == 0:

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE username = 'admin'
            LIMIT 1
            """
        )

        admin_existente = (
            cursor.fetchone()
        )

        if admin_existente:

            cursor.execute(
                """
                UPDATE usuarios
                SET rol = 'ADMIN'
                WHERE id_usuario = ?
                """,
                (
                    admin_existente[0],
                )
            )

            print(
                "--> Usuario 'admin' existente "
                "actualizado a rol ADMIN."
            )

    conn.commit()

    conn.close()


# =====================================================
#                    FIN DEL MÓDULO
# =====================================================