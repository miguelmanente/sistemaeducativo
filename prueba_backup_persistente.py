
import os
from cryptography.fernet import Fernet


# ==================================================
# ARCHIVOS DEL LABORATORIO
# ==================================================

archivo_bd = "bdescuela_prueba.db"

archivo_clave_protegida = "clave_datos_sge.protegida"

archivo_clave_recuperacion = "clave_recuperacion_sge.key"

archivo_datos_recuperacion = "clave_datos_sge.recuperacion"

archivo_backup_cifrado = "backup_prueba_persistente.enc"


print("================================================")
print(" LABORATORIO 10 - BACKUP CON CLAVE PERSISTENTE")
print("================================================")


# ==================================================
# 1. VERIFICAR LA BASE DE PRUEBA
# ==================================================

print()
print("1. VERIFICANDO BASE DE DATOS")
print("----------------------------")


if not os.path.exists(archivo_bd):

    print()
    print("❌ No existe:")
    print(archivo_bd)

    raise SystemExit


print()
print("✅ Base de datos encontrada.")

print()
print("Tamaño de la base:")
print(os.path.getsize(archivo_bd), "bytes")


# ==================================================
# 2. RECUPERAR LA CLAVE DE DATOS
#    MEDIANTE EL SISTEMA INDEPENDIENTE
# ==================================================

print()
print("2. RECUPERANDO CLAVE DE DATOS")
print("------------------------------")


if not os.path.exists(archivo_datos_recuperacion):

    print()
    print("❌ No existe:")
    print(archivo_datos_recuperacion)

    raise SystemExit


if not os.path.exists(archivo_clave_recuperacion):

    print()
    print("❌ No existe:")
    print(archivo_clave_recuperacion)

    raise SystemExit


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
    print("❌ La clave recuperada no tiene 32 bytes.")

    raise SystemExit


print()
print("✅ La clave tiene 32 bytes.")


# ==================================================
# 3. CONVERTIR LA CLAVE PARA FERNET
# ==================================================

print()
print("3. PREPARANDO CLAVE PARA CIFRADO")
print("---------------------------------")


import base64


clave_fernet = base64.urlsafe_b64encode(
    clave_datos
)


fernet = Fernet(
    clave_fernet
)


print()
print("✅ Clave preparada correctamente.")


# ==================================================
# 4. LEER LA BASE DE DATOS
# ==================================================

print()
print("4. LEYENDO BASE DE DATOS")
print("------------------------")


with open(
    archivo_bd,
    "rb"
) as archivo:

    datos_bd = archivo.read()


print()
print("Datos leídos:")
print(len(datos_bd), "bytes")


# ==================================================
# 5. CIFRAR LA BASE
# ==================================================

print()
print("5. CIFRANDO BACKUP")
print("-------------------")


datos_cifrados = fernet.encrypt(
    datos_bd
)


print()
print("✅ Backup cifrado en memoria.")

print()
print("Tamaño del backup cifrado:")
print(len(datos_cifrados), "bytes")


# ==================================================
# 6. GUARDAR BACKUP CIFRADO
# ==================================================

print()
print("6. GUARDANDO BACKUP CIFRADO")
print("----------------------------")


with open(
    archivo_backup_cifrado,
    "wb"
) as archivo:

    archivo.write(
        datos_cifrados
    )


print()
print("✅ Backup cifrado guardado.")

print()
print("Archivo:")
print(
    os.path.abspath(
        archivo_backup_cifrado
    )
)


# ==================================================
# 7. COMPROBACIONES
# ==================================================

print()
print("7. COMPROBACIONES")
print("------------------")


print()
print("¿Existe el backup cifrado?")

if os.path.exists(archivo_backup_cifrado):

    print("✅ SÍ.")

else:

    print("❌ NO.")


print()
print("¿El backup cifrado tiene contenido?")

if os.path.getsize(
    archivo_backup_cifrado
) > 0:

    print("✅ SÍ.")

else:

    print("❌ NO.")


print()
print("================================================")
print(" LABORATORIO 10 FINALIZADO")
print("================================================")

print()
print("🎯 La base de datos de prueba fue cifrada")
print("utilizando la CLAVE DE DATOS PERSISTENTE.")

