import os
from cryptography.fernet import Fernet, InvalidToken


# ============================================================
# LABORATORIO 13
# DETECCIÓN DE BACKUP MANIPULADO O DAÑADO
# ============================================================

CARPETA = "RECUPERACION_SGE"

ARCHIVO_BACKUP_ORIGINAL = os.path.join(
    CARPETA,
    "backup_prueba_persistente.enc"
)

ARCHIVO_BACKUP_PRUEBA = os.path.join(
    CARPETA,
    "backup_prueba_manipulado.enc"
)

ARCHIVO_RECUPERACION = os.path.join(
    CARPETA,
    "clave_datos_sge.recuperacion"
)

ARCHIVO_CLAVE_RECUPERACION = os.path.join(
    CARPETA,
    "clave_recuperacion_sge.key"
)

ARCHIVO_BD_RECUPERADA = os.path.join(
    CARPETA,
    "bd_NO_DEBERIA_RECUPERARSE.db"
)


print("=" * 55)
print(" LABORATORIO 13 - INTEGRIDAD DEL BACKUP")
print("=" * 55)


# ============================================================
# 1. VERIFICAR ARCHIVOS NECESARIOS
# ============================================================

print()
print("1. VERIFICANDO ARCHIVOS")
print("-" * 55)

archivos_necesarios = [
    ARCHIVO_BACKUP_ORIGINAL,
    ARCHIVO_RECUPERACION,
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
# 2. RECUPERAR LA CLAVE DE DATOS
# ============================================================

print()
print("2. RECUPERANDO CLAVE DE DATOS")
print("-" * 55)


with open(ARCHIVO_RECUPERACION, "rb") as archivo:

    datos_protegidos = archivo.read()


with open(ARCHIVO_CLAVE_RECUPERACION, "rb") as archivo:

    clave_recuperacion = archivo.read()


fernet_recuperacion = Fernet(clave_recuperacion)


try:

    clave_datos = fernet_recuperacion.decrypt(
        datos_protegidos
    )

except InvalidToken:

    print("❌ No se pudo recuperar la clave de datos.")

    raise


print("✅ Clave de datos recuperada.")

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
# 3. PREPARAR FERNET
# ============================================================

print()
print("3. PREPARANDO DESCIFRADO")
print("-" * 55)


import base64


clave_fernet = base64.urlsafe_b64encode(
    clave_datos
)


fernet = Fernet(clave_fernet)


print("✅ Mecanismo de descifrado preparado.")


# ============================================================
# 4. CREAR COPIA DEL BACKUP
# ============================================================

print()
print("4. CREANDO COPIA DEL BACKUP")
print("-" * 55)


with open(
    ARCHIVO_BACKUP_ORIGINAL,
    "rb"
) as archivo:

    datos_backup = bytearray(
        archivo.read()
    )


print("Tamaño del backup original:")
print(len(datos_backup), "bytes")


# ============================================================
# 5. MODIFICAR DELIBERADAMENTE UN BYTE
# ============================================================

print()
print("5. SIMULANDO MANIPULACIÓN DEL BACKUP")
print("-" * 55)


# Modificamos un solo byte.
# No destruimos el backup original.

posicion = 100


valor_original = datos_backup[posicion]


datos_backup[posicion] = (
    valor_original + 1
) % 256


print("Se modificó deliberadamente un byte.")

print()
print("Posición modificada:")
print(posicion)

print()
print("Valor original:")
print(valor_original)

print()
print("Nuevo valor:")
print(datos_backup[posicion])


# ============================================================
# 6. GUARDAR BACKUP MANIPULADO
# ============================================================

print()
print("6. GUARDANDO BACKUP MANIPULADO")
print("-" * 55)


with open(
    ARCHIVO_BACKUP_PRUEBA,
    "wb"
) as archivo:

    archivo.write(datos_backup)


print("✅ Backup manipulado creado:")

print(
    os.path.abspath(
        ARCHIVO_BACKUP_PRUEBA
    )
)


# ============================================================
# 7. INTENTAR DESCIFRAR EL BACKUP MANIPULADO
# ============================================================

print()
print("7. INTENTANDO DESCIFRAR EL BACKUP")
print("-" * 55)


with open(
    ARCHIVO_BACKUP_PRUEBA,
    "rb"
) as archivo:

    datos_manipulados = archivo.read()


print("Tamaño del backup manipulado:")
print(len(datos_manipulados), "bytes")


print()
print("Intentando descifrar...")


try:

    datos_recuperados = fernet.decrypt(
        datos_manipulados
    )

    print()
    print("⚠️ ATENCIÓN")
    print("El backup pudo ser descifrado.")

except InvalidToken:

    print()
    print("🛡️ BACKUP RECHAZADO")
    print("-" * 55)
    print()
    print(
        "❌ Fernet detectó que el contenido"
    )
    print(
        "   del backup fue alterado o está dañado."
    )

    print()
    print(
        "✅ La restauración fue detenida."
    )

    print()
    print(
        "Esto es exactamente lo que queremos."
    )

    print()
    print("=" * 55)
    print(" RESULTADO DEL LABORATORIO")
    print("=" * 55)

    print()
    print(
        "🎉 INTEGRIDAD VERIFICADA."
    )

    print()
    print(
        "El backup manipulado NO pudo ser"
    )
    print(
        "descifrado ni utilizado para restaurar"
    )
    print(
        "la base de datos."
    )

    print()
    print(
        "El backup original permanece intacto."
    )

    print()
    print("=" * 55)
    print(" LABORATORIO 13 FINALIZADO")
    print("=" * 55)

    raise SystemExit


# ============================================================
# 8. SI LLEGAMOS AQUÍ, ALGO NO SALIÓ COMO ESPERÁBAMOS
# ============================================================

print()
print("⚠️ RESULTADO INESPERADO")

print()
print(
    "El backup manipulado pudo ser descifrado."
)

print(
    "Revisar el procedimiento criptográfico."
)

print()
print("=" * 55)
print(" LABORATORIO 13 FINALIZADO CON ADVERTENCIA")
print("=" * 55)