import os
import sqlite3
import base64

from cryptography.fernet import Fernet


# ============================================================
# ARCHIVOS
# ============================================================

carpeta_recuperacion = "RECUPERACION_SGE"

archivo_backup = os.path.join(
    carpeta_recuperacion,
    "backup_prueba_persistente.enc"
)

archivo_datos_recuperacion = os.path.join(
    carpeta_recuperacion,
    "clave_datos_sge.recuperacion"
)

archivo_clave_recuperacion = os.path.join(
    carpeta_recuperacion,
    "clave_recuperacion_sge.key"
)

archivo_bd_recuperada = os.path.join(
    carpeta_recuperacion,
    "bdescuela_recuperada_desastre.db"
)


print("================================================")
print(" LABORATORIO 12 - RECUPERACIÓN DE DESASTRE")
print("================================================")


# ============================================================
# 1. VERIFICAR ARCHIVOS
# ============================================================

print()
print("1. VERIFICANDO PAQUETE DE RECUPERACIÓN")
print("---------------------------------------")

archivos_necesarios = [
    archivo_backup,
    archivo_datos_recuperacion,
    archivo_clave_recuperacion
]

todo_correcto = True

for archivo in archivos_necesarios:

    if os.path.exists(archivo):
        print("✅", archivo)
    else:
        print("❌ FALTA:", archivo)
        todo_correcto = False


if not todo_correcto:

    print()
    print("❌ No se puede continuar.")
    print("Falta uno o más archivos de recuperación.")

    raise SystemExit


# ============================================================
# 2. RECUPERAR CLAVE DE DATOS
# ============================================================

print()
print("2. RECUPERANDO CLAVE DE DATOS")
print("------------------------------")


with open(
    archivo_datos_recuperacion,
    "rb"
) as archivo:

    datos_protegidos = archivo.read()


with open(
    archivo_clave_recuperacion,
    "rb"
) as archivo:

    clave_recuperacion = archivo.read()


print()
print("Clave de recuperación encontrada.")

fernet_recuperacion = Fernet(
    clave_recuperacion
)


clave_datos = fernet_recuperacion.decrypt(
    datos_protegidos
)


print()
print("🔑 CLAVE DE DATOS RECUPERADA.")

print()
print("Cantidad de bytes:")
print(len(clave_datos))


if len(clave_datos) != 32:

    print()
    print("❌ ERROR.")
    print("La clave recuperada no tiene 32 bytes.")

    raise SystemExit


print()
print("✅ La clave tiene 32 bytes.")


# ============================================================
# 3. PREPARAR CLAVE PARA FERNET
# ============================================================

print()
print("3. PREPARANDO CLAVE PARA DESCIFRAR")
print("-----------------------------------")


clave_fernet = base64.urlsafe_b64encode(
    clave_datos
)


fernet = Fernet(
    clave_fernet
)


print()
print("✅ Mecanismo de descifrado preparado.")


# ============================================================
# 4. LEER BACKUP CIFRADO
# ============================================================

print()
print("4. LEYENDO BACKUP CIFRADO")
print("--------------------------")


with open(
    archivo_backup,
    "rb"
) as archivo:

    datos_cifrados = archivo.read()


print()
print("Tamaño del backup cifrado:")
print(len(datos_cifrados), "bytes")


# ============================================================
# 5. DESCIFRAR
# ============================================================

print()
print("5. DESCIFRANDO BACKUP")
print("----------------------")


try:

    datos_recuperados = fernet.decrypt(
        datos_cifrados
    )

except Exception as e:

    print()
    print("❌ ERROR AL DESCIFRAR EL BACKUP.")
    print(e)

    raise SystemExit


print()
print("✅ Backup descifrado correctamente.")

print()
print("Tamaño de los datos recuperados:")
print(len(datos_recuperados), "bytes")


# ============================================================
# 6. GUARDAR BASE RECUPERADA
# ============================================================

print()
print("6. CREANDO BASE DE DATOS RECUPERADA")
print("------------------------------------")


with open(
    archivo_bd_recuperada,
    "wb"
) as archivo:

    archivo.write(
        datos_recuperados
    )


print()
print("✅ Base de datos recuperada.")

print()
print("Archivo:")
print(
    os.path.abspath(
        archivo_bd_recuperada
    )
)


# ============================================================
# 7. ABRIR BASE CON SQLITE
# ============================================================

print()
print("7. ABRIENDO BASE RECUPERADA CON SQLITE")
print("---------------------------------------")


try:

    conn = sqlite3.connect(
        archivo_bd_recuperada
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tablas = cursor.fetchall()

    conn.close()

except Exception as e:

    print()
    print("❌ ERROR AL ABRIR LA BASE CON SQLITE.")
    print(e)

    raise SystemExit


print()
print("✅ La base de datos pudo abrirse correctamente.")

print()
print("TABLAS ENCONTRADAS:")

for tabla in tablas:

    print("-", tabla[0])


# ============================================================
# 8. COMPROBAR TABLAS PRINCIPALES DEL SGE
# ============================================================

print()
print("8. VERIFICANDO TABLAS DEL SGE")
print("------------------------------")


tablas_esperadas = [
    "usuarios",
    "profesores",
    "materias",
    "asignacion",
    "inasistencia",
    "calendario_escolar",
    "ciclo_lectivo",
    "dias_no_laborables"
]


nombres_tablas = [
    tabla[0]
    for tabla in tablas
]


todo_presente = True


for tabla in tablas_esperadas:

    if tabla in nombres_tablas:

        print("✅", tabla)

    else:

        print("❌ FALTA:", tabla)
        todo_presente = False


# ============================================================
# 9. RESULTADO FINAL
# ============================================================

print()
print("================================================")
print(" RESULTADO FINAL")
print("================================================")


if todo_presente:

    print()
    print("🎉 RECUPERACIÓN EXITOSA.")

    print()
    print("La base de datos pudo ser recuperada")
    print("sin utilizar la clave protegida por DPAPI.")

    print()
    print("El backup cifrado y el paquete")
    print("de recuperación fueron suficientes.")

else:

    print()
    print("⚠️ La base fue recuperada,")
    print("pero faltan una o más tablas esperadas.")


print()
print("================================================")
print(" LABORATORIO 12 FINALIZADO")
print("================================================")
