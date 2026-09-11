
import os
import base64
from cryptography.fernet import Fernet


# ==================================================
# ARCHIVOS
# ==================================================

archivo_bd_original = "bdescuela_prueba.db"

archivo_backup_cifrado = "backup_prueba_persistente.enc"

archivo_datos_recuperacion = "clave_datos_sge.recuperacion"

archivo_clave_recuperacion = "clave_recuperacion_sge.key"

archivo_bd_recuperada = "bdescuela_recuperada.db"


print("================================================")
print(" LABORATORIO 11 - RESTAURACIÓN DEL BACKUP")
print("================================================")


# ==================================================
# 1. VERIFICAR ARCHIVOS NECESARIOS
# ==================================================

print()
print("1. VERIFICANDO ARCHIVOS")
print("-----------------------")


archivos_necesarios = [
    archivo_bd_original,
    archivo_backup_cifrado,
    archivo_datos_recuperacion,
    archivo_clave_recuperacion
]


for archivo in archivos_necesarios:

    if not os.path.exists(archivo):

        print()
        print("❌ No existe:")
        print(archivo)

        raise SystemExit

    print("✅", archivo)


# ==================================================
# 2. RECUPERAR LA CLAVE DE DATOS
# ==================================================

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


fernet_recuperacion = Fernet(
    clave_recuperacion
)


clave_datos = fernet_recuperacion.decrypt(
    datos_protegidos
)


print()
print("🔑 Clave de datos recuperada.")

print()
print("Cantidad de bytes:")
print(len(clave_datos))


if len(clave_datos) != 32:

    print()
    print("❌ La clave no tiene 32 bytes.")

    raise SystemExit


print()
print("✅ La clave tiene 32 bytes.")


# ==================================================
# 3. PREPARAR FERNET
# ==================================================

print()
print("3. PREPARANDO DESCIFRADO")
print("------------------------")


clave_fernet = base64.urlsafe_b64encode(
    clave_datos
)


fernet = Fernet(
    clave_fernet
)


print()
print("✅ Mecanismo de descifrado preparado.")


# ==================================================
# 4. LEER BACKUP CIFRADO
# ==================================================

print()
print("4. LEYENDO BACKUP CIFRADO")
print("--------------------------")


with open(
    archivo_backup_cifrado,
    "rb"
) as archivo:

    datos_cifrados = archivo.read()


print()
print("Tamaño del backup cifrado:")
print(len(datos_cifrados), "bytes")


# ==================================================
# 5. DESCIFRAR BACKUP
# ==================================================

print()
print("5. DESCIFRANDO BACKUP")
print("----------------------")


try:

    datos_recuperados = fernet.decrypt(
        datos_cifrados
    )

except Exception as e:

    print()
    print("❌ No fue posible descifrar el backup.")

    print()
    print("Error:")
    print(e)

    raise SystemExit


print()
print("✅ Backup descifrado correctamente.")


print()
print("Tamaño de los datos recuperados:")
print(len(datos_recuperados), "bytes")


# ==================================================
# 6. GUARDAR BASE RECUPERADA
# ==================================================

print()
print("6. GUARDANDO BASE RECUPERADA")
print("-----------------------------")


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


# ==================================================
# 7. COMPARAR CON LA BASE ORIGINAL
# ==================================================

print()
print("7. COMPARANDO BASES")
print("-------------------")


with open(
    archivo_bd_original,
    "rb"
) as archivo:

    datos_originales = archivo.read()


print()
print("Tamaño base original:")
print(len(datos_originales), "bytes")


print()
print("Tamaño base recuperada:")
print(len(datos_recuperados), "bytes")


print()
print("¿Los archivos son exactamente iguales?")


if datos_originales == datos_recuperados:

    print()
    print("✅ SÍ. SON EXACTAMENTE IGUALES.")

else:

    print()
    print("❌ NO. LOS ARCHIVOS SON DIFERENTES.")


# ==================================================
# 8. COMPROBAR ARCHIVO RECUPERADO
# ==================================================

print()
print("8. COMPROBACIÓN FINAL")
print("----------------------")


if os.path.exists(archivo_bd_recuperada):

    print()
    print("✅ El archivo recuperado existe.")

else:

    print()
    print("❌ El archivo recuperado no existe.")


print()
print("================================================")
print(" LABORATORIO 11 FINALIZADO")
print("================================================")

