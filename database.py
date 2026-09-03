# =====================================================
#            MÓDULO CREACIÓN DE TABLAS DE LA BD
# =====================================================

# ------------------------ LIBRERÍAS -------------------
import sqlite3
import hashlib
import os
import sys

from Backup import crear_backup


# =====================================================
#              CONEXIÓN A LA BASE DE DATOS
# =====================================================

def conectar():
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DATABASE = os.path.join(BASE_DIR, "bdescuela.db")

    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON;")

    return conn


# =====================================================
#              ENCRIPTAR CONTRASEÑA
# =====================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =====================================================
#              REGISTRAR NUEVO USUARIO
# =====================================================

def registrar_usuario(username, password):

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
        # El usuario ya existe
        return False

    except Exception as e:
        print("Error al registrar usuario:", e)
        return False

    finally:
        if conn:
            conn.close()


# =====================================================
#        VALIDAR LOGIN NORMAL DEL SISTEMA
# =====================================================

def validar_usuario(username, password):

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
        print("Error al validar usuario:", e)
        return None

    finally:
        if conn:
            conn.close()


# =====================================================
#       VALIDAR QUE EL USUARIO SEA ADMINISTRADOR
# =====================================================

def validar_administrador(username, password):

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
        print("Error al validar administrador:", e)
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
        print("Error al verificar administrador:", e)
        return False

    finally:
        if conn:
            conn.close()


# =====================================================
#          CREAR ADMINISTRADOR INICIAL
# =====================================================

def crear_administrador(username, password):

    conn = None

    try:
        conn = conectar()
        cursor = conn.cursor()

        # Verificamos que no exista otro administrador
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
        print("Error al crear administrador:", e)
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

    cursor.executescript("""

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

    """)


    # =================================================
    #        MIGRACIÓN DE LA TABLA USUARIOS
    # =================================================
    #
    # Esto sirve para instalaciones anteriores del SGE
    # donde la tabla usuarios fue creada sin el campo rol.
    # =================================================

    cursor.execute("PRAGMA table_info(usuarios)")

    columnas = [fila[1] for fila in cursor.fetchall()]

    if "rol" not in columnas:

        cursor.execute(
            """
            ALTER TABLE usuarios
            ADD COLUMN rol TEXT NOT NULL DEFAULT 'USUARIO'
            """
        )

        print("--> Campo 'rol' agregado a la tabla usuarios.")


    # =================================================
    #     ADMINISTRADOR INICIAL
    # =================================================
    #
    # SOLO se crea cuando la tabla está completamente
    # vacía.
    #
    # Datos iniciales:
    #
    # Usuario: admin
    # Clave:   admin123
    #
    # Una vez creado, el administrador puede utilizar
    # la pantalla de registro para crear usuarios.
    # =================================================

    cursor.execute("SELECT COUNT(*) FROM usuarios")

    cantidad_usuarios = cursor.fetchone()[0]

    if cantidad_usuarios == 0:

        clave_encriptada = hash_password("admin123")

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
            "--> Usuario administrador inicial creado."
        )


    # =================================================
    #     COMPATIBILIDAD CON INSTALACIONES ANTERIORES
    # =================================================
    #
    # Si ya existía el usuario 'admin' de una versión
    # anterior del SGE y todavía no tenía rol ADMIN,
    # lo recuperamos como administrador.
    #
    # Esto evita que una actualización deje al sistema
    # sin ningún administrador.
    # =================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE rol = 'ADMIN'
        """
    )

    cantidad_admin = cursor.fetchone()[0]

    if cantidad_admin == 0:

        cursor.execute(
            """
            SELECT id_usuario
            FROM usuarios
            WHERE username = 'admin'
            LIMIT 1
            """
        )

        admin_existente = cursor.fetchone()

        if admin_existente:

            cursor.execute(
                """
                UPDATE usuarios
                SET rol = 'ADMIN'
                WHERE id_usuario = ?
                """,
                (admin_existente[0],)
            )

            print(
                "--> Usuario 'admin' existente actualizado a rol ADMIN."
            )


    conn.commit()

    # =================================================
    #              CREAR BACKUP
    # =================================================

    crear_backup()

    conn.close()


# =====================================================
#                    FIN DEL MÓDULO
# =====================================================