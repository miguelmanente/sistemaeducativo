import os
import sqlite3
import base64

from cryptography.fernet import Fernet, InvalidToken


# ============================================================
# LABORATORIO 14
# RECUPERACIÓN EN UNA INSTALACIÓN NUEVA
# ============================================================

CARPETA_RECUPERACION = "RECUPERACION_SGE_NUEVA"
CARPETA_NUEVA = "SGE_NUEVA_INSTALACION"


ARCHIVO_BACKUP = os.path.join(
    CARPETA_RECUPERACION,
    "backup_prueba_persistente.enc"
)

ARCHIVO_DATOS_RECUPERACION = os.path.join(
    CARPETA_RECUPERACION,
    "clave_datos_sge.recuperacion"
)

ARCHIVO_CLAVE_RECUPERACION = os.path.join(
    CARPETA_RECUPERACION,
    "clave_recuperacion_sge.key"
)

ARCHIVO_BD_RECUPERADA = os.path.join(
    CARPETA_NUEVA,
    "bdescuela.db"
)


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


print("=" * 60)
print(" LABORATORIO 14 - RECUPERACIÓN EN INSTALACIÓN NUEVA")
print("=" * 60)


# ============================================================
# 1. PREPARAR CARPETA DE NUEVA INSTALACIÓN
# ============================================================

print()
print("1. PREPARANDO NUEVA INSTALACIÓN")
print("-" * 60)

os.makedirs(CARPETA_NUEVA, exist_ok=True)

print("✅ Carpeta de nueva instalación:")
print(os.path.abspath(CARPETA_NUEVA))


# ============================================================
# 2. VERIFICAR QUE NO EXISTE UNA BASE ANTERIOR
# ============================================================

print()
print("2. VERIFICANDO ESTADO DE LA NUEVA INSTALACIÓN")
print("-" * 60)

if os.path.exists(ARCHIVO_BD_RECUPERADA):

    print("⚠️ Ya existe:")
    print(os.path.abspath(ARCHIVO_BD_RECUPERADA))

    print()
    print("Eliminando la base anterior para")
    print("simular una instalación realmente nueva...")

    os.remove(ARCHIVO_BD_RECUPERADA)

    print("✅ Base anterior eliminada.")

else:

    print("✅ No existe una base de datos.")
    print("La instalación está limpia.")


# ============================================================
# 3. VERIFICAR PAQUETE DE RECUPERACIÓN
# ============================================================

print()
print("3. VERIFICANDO PAQUETE DE RECUPERACIÓN")
print("-" * 60)

archivos_necesarios = [
    ARCHIVO_BACKUP,
    ARCHIVO_DATOS_RECUPERACION,
    ARCHIVO_CLAVE_RECUPERACION
]


for archivo in archivos_necesarios:

    if os.path.exists(archivo):

        print("✅", archivo)

    else:

        print("❌ FALTA:", archivo)

        raise FileNotFoundError(
            f"No se encontró el archivo: {archivo}"
        )


# ============================================================
# 4. RECUPERAR CLAVE DE DATOS
# ============================================================

print()
print("4. RECUPERANDO CLAVE DE DATOS")
print("-" * 60)


with open(
    ARCHIVO_DATOS_RECUPERACION,
    "rb"
) as archivo:

    datos_protegidos = archivo.read()


with open(
    ARCHIVO_CLAVE_RECUPERACION,
    "rb"
) as archivo:

    clave_recuperacion = archivo.read()


print("Clave de recuperación encontrada.")


fernet_recuperacion = Fernet(
    clave_recuperacion
)


try:

    clave_datos = fernet_recuperacion.decrypt(
        datos_protegidos
    )

except InvalidToken:

    print()
    print("❌ No se pudo recuperar la clave de datos.")

    raise


print("🔑 CLAVE DE DATOS RECUPERADA.")

print()
print("Cantidad de bytes:")
print(len(clave_datos))


if len(clave_datos) != 32:

    print()
    print("❌ La clave recuperada no tiene 32 bytes.")

    raise ValueError(
        "La clave de datos tiene un tamaño incorrecto."
    )


print("✅ La clave tiene 32 bytes.")


# ============================================================
# 5. PREPARAR CLAVE PARA DESCIFRAR EL BACKUP
# ============================================================

print()
print("5. PREPARANDO DESCIFRADO DEL BACKUP")
print("-" * 60)


clave_fernet = base64.urlsafe_b64encode(
    clave_datos
)


fernet = Fernet(
    clave_fernet
)


print("✅ Mecanismo de descifrado preparado.")


# ============================================================
# 6. LEER BACKUP CIFRADO
# ============================================================

print()
print("6. LEYENDO BACKUP CIFRADO")
print("-" * 60)


with open(
    ARCHIVO_BACKUP,
    "rb"
) as archivo:

    datos_cifrados = archivo.read()


print("Archivo:")
print(os.path.abspath(ARCHIVO_BACKUP))

print()
print("Tamaño del backup cifrado:")
print(len(datos_cifrados), "bytes")


# ============================================================
# 7. DESCIFRAR BACKUP
# ============================================================

print()
print("7. VERIFICANDO Y DESCIFRANDO BACKUP")
print("-" * 60)

try:

    datos_bd = fernet.decrypt(
        datos_cifrados
    )

except InvalidToken:

    print()
    print("❌ EL BACKUP FUE RECHAZADO.")

    print()
    print(
        "El backup no pudo superar la"
    )
    print(
        "verificación criptográfica."
    )

    raise


print("✅ Backup verificado correctamente.")

print()
print("Tamaño de los datos recuperados:")
print(len(datos_bd), "bytes")


# ============================================================
# 8. CREAR BASE DE DATOS EN LA NUEVA INSTALACIÓN
# ============================================================

print()
print("8. CREANDO BASE DE DATOS EN LA NUEVA INSTALACIÓN")
print("-" * 60)


with open(
    ARCHIVO_BD_RECUPERADA,
    "wb"
) as archivo:

    archivo.write(datos_bd)


print("✅ Base de datos recuperada.")

print()
print("Archivo:")
print(os.path.abspath(ARCHIVO_BD_RECUPERADA))


# ============================================================
# 9. ABRIR BASE RECUPERADA CON SQLITE
# ============================================================

print()
print("9. ABRIENDO BASE RECUPERADA CON SQLITE")
print("-" * 60)


conn = sqlite3.connect(
    ARCHIVO_BD_RECUPERADA
)

cursor = conn.cursor()


cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")


tablas = [
    fila[0]
    for fila in cursor.fetchall()
]


print("✅ La base de datos pudo abrirse correctamente.")


print()
print("TABLAS ENCONTRADAS:")


for tabla in tablas:

    print("-", tabla)


# ============================================================
# 10. VERIFICAR TABLAS DEL SGE
# ============================================================

print()
print("10. VERIFICANDO ESTRUCTURA DEL SGE")
print("-" * 60)


faltantes = []


for tabla in TABLAS_ESPERADAS:

    if tabla in tablas:

        print("✅", tabla)

    else:

        print("❌ FALTA:", tabla)

        faltantes.append(tabla)


conn.close()


# ============================================================
# 11. RESULTADO FINAL
# ============================================================

print()
print("=" * 60)
print(" RESULTADO FINAL")
print("=" * 60)


if len(faltantes) == 0:

    print()
    print("🎉 RECUPERACIÓN EXITOSA.")

    print()
    print(
        "La instalación nueva pudo reconstruir"
    )
    print(
        "la base de datos del SGE."
    )

    print()
    print(
        "La recuperación utilizó únicamente:"
    )

    print(
        "🔐 paquete de recuperación"
    )

    print(
        "📦 backup cifrado"
    )

    print()
    print(
        "No fue necesaria la base de datos original."
    )

    print()
    print(
        "No fue necesaria la protección DPAPI"
    )

    print(
        "de la instalación anterior."
    )

    print()
    print("=" * 60)
    print(" LABORATORIO 14 FINALIZADO")
    print("=" * 60)

else:

    print()
    print("❌ RECUPERACIÓN INCOMPLETA.")

    print()
    print("Tablas faltantes:")

    for tabla in faltantes:

        print("-", tabla)

    print()
    print("=" * 60)
    print(" LABORATORIO 14 FINALIZADO CON ADVERTENCIA")
    print("=" * 60)
    