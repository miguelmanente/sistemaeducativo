# =====================================================
#            MÓDULO CREACIÓN DE TABLAS DE LA BD
# =====================================================

# ------------------------ LIBRERÍAS  ---------------------------------
import sqlite3
import hashlib
import os, sys
from Backup import crear_backup

#--------- función que permite conectarse a la BD profesores -----------------------
def conectar():
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    DATABASE = os.path.join(BASE_DIR, "bdescuela.db")

    #print("Base de datos:", DATABASE)

    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
# ----------------------------------------------------------------------------------

# -------------------- Encriptar contraseña de usuarios ----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
#-----------------------------------------------------------------------------------

# ----------- Registrar usuario que luego permite loguearse ------------------------
def registrar_usuario(username, password):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Usuario ya existe
# --------------------------- Fin función Registrar Usuario -------------------------


# ---------------------- Validar login del usuario para loguearse -------------------
def validar_usuario(username, password):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE username = ? AND password = ?",
        (username, hash_password(password))
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario
# ---------------------------- Fin función validación---------------------------------------------------


#---------------------  CREAR Y VERIFICAR SI ESTÁN CREADAS LAS TABLAS ----------------
def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.executescript("""
     
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,  
        username TEXT UNIQUE,
        password TEXT
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
                         
    /* ======================================================================= */
    /* 🔥 NUEVA TABLA ASIGNACIONES DOCENTES (MODIFICADA Y OPTIMIZADA)          */
    /* ======================================================================= */
    CREATE TABLE IF NOT EXISTS asignacion (
        id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
        id_profesor INTEGER,              -- Conecta con la tabla profesores
        id_materia INTEGER NULL,          -- Conecta con materias (puede ser NULL si es cargo fijo)
        dia TEXT,                        -- Lunes, Martes, etc.
        cargo TEXT,                  -- 'Módulos', 'Director', 'Preceptor', etc.
        modulos INTEGER DEFAULT 0,
        curso TEXT,                       -- Ej: '4to 1ra'
        turno TEXT,                       -- Mañana, Tarde, Vespertino
        hentrada TEXT,
        hsalida TEXT,
        situacion_revista TEXT,           -- Titular, Provisional, Suplente
        toma_pos TEXT,                    -- Fecha en que el docente tomó posesión del cargo (puede ser NULL)
        fecha_cese TEXT NULL,                    
        activo INTEGER DEFAULT 1,         -- 1 = Activo, 0 = Cesado (para historial)
        
        FOREIGN KEY (id_profesor) REFERENCES profesores(id_profesor),
        FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
    );
                         
    CREATE TABLE IF NOT EXISTS inasistencia (
        id_inasistencia INTEGER PRIMARY KEY AUTOINCREMENT,
        id_asignacion INTEGER NOT NULL,

        f_desde TEXT NOT NULL,
        f_hasta TEXT NOT NULL,

        tot_dias_trab INTEGER,
        cant_inasist INTEGER,
                         
        motivo TEXT,
        observacion TEXT,

        FOREIGN KEY (id_asignacion)
            REFERENCES asignacion(id_asignacion)
    );
                         
    """)

    # 2. Controlamos la inserción del Administrador Encriptado desde Python
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        # Encriptamos la clave usando tu función existente hash_password()
        clave_encriptada = hash_password("admin123")
        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)", 
            ('admin', clave_encriptada)
        )
        print("--> ¡Usuario administrador inicial creado con éxito!")


    conn.commit()
    crear_backup()
    conn.close()