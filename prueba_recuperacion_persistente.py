import os
import base64
from cryptography.fernet import Fernet

import ctypes
from ctypes import wintypes


# ============================================================
# ARCHIVOS DEL LABORATORIO
# ============================================================

archivo_clave_protegida = "clave_datos_sge.protegida"
archivo_recuperacion = "clave_datos_sge.recuperacion"
archivo_clave_recuperacion = "clave_recuperacion_sge.key"


# ============================================================
# ESTRUCTURA DE WINDOWS
# ============================================================

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]


# ============================================================
# DLL DE WINDOWS
# ============================================================

crypt32 = ctypes.windll.crypt32
kernel32 = ctypes.windll.kernel32


# ============================================================
# DESPROTEGER CON DPAPI
# ============================================================

def desproteger_datos(datos_protegidos):

    buffer_entrada = ctypes.create_string_buffer(
        datos_protegidos
    )

    entrada = DATA_BLOB(
        len(datos_protegidos),
        ctypes.cast(
            buffer_entrada,
            ctypes.POINTER(ctypes.c_byte)
        )
    )

    salida = DATA_BLOB()

    resultado = crypt32.CryptUnprotectData(
        ctypes.byref(entrada),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(salida)
    )

    if not resultado:
        raise ctypes.WinError()

    try:
        return ctypes.string_at(
            salida.pbData,
            salida.cbData
        )

    finally:
        kernel32.LocalFree(salida.pbData)


# ============================================================
# COMIENZA EL LABORATORIO
# ============================================================

print("==============================================")
print("   LABORATORIO 8 - RECUPERACIÓN INDEPENDIENTE")
print("==============================================")


# ============================================================
# COMPROBAR QUE EXISTE LA CLAVE PROTEGIDA
# ============================================================

if not os.path.exists(archivo_clave_protegida):

    print()
    print("❌ No existe:")
    print(archivo_clave_protegida)

    print()
    print("Primero debemos ejecutar el Laboratorio 7.")

    raise SystemExit


# ============================================================
# RECUPERAR LA CLAVE DE DATOS MEDIANTE DPAPI
# ============================================================

print()
print("1. RECUPERANDO CLAVE DE DATOS CON DPAPI")
print("----------------------------------------")

with open(archivo_clave_protegida, "rb") as archivo:
    datos_protegidos = archivo.read()

clave_datos = desproteger_datos(
    datos_protegidos
)

print()
print("🔑 CLAVE DE DATOS RECUPERADA:")
print(clave_datos)

print()
print("Cantidad de bytes:")
print(len(clave_datos))


# ============================================================
# CREAR CLAVE DE RECUPERACIÓN
# ============================================================

print()
print("2. CREANDO CLAVE DE RECUPERACIÓN")
print("---------------------------------")

clave_recuperacion = Fernet.generate_key()

print()
print("🔐 CLAVE DE RECUPERACIÓN:")
print(clave_recuperacion)


# ============================================================
# CREAR OBJETO FERNET
# ============================================================

fernet = Fernet(clave_recuperacion)


# ============================================================
# PROTEGER LA CLAVE DE DATOS
# ============================================================

print()
print("3. PROTEGIENDO LA CLAVE DE DATOS")
print("---------------------------------")

clave_datos_protegida_recuperacion = (
    fernet.encrypt(clave_datos)
)

print()
print("Tamaño de la clave de datos:")
print(len(clave_datos), "bytes")

print()
print("Tamaño de la versión protegida:")
print(
    len(clave_datos_protegida_recuperacion),
    "bytes"
)


# ============================================================
# GUARDAR LA PROTECCIÓN DE RECUPERACIÓN
# ============================================================

with open(
    archivo_recuperacion,
    "wb"
) as archivo:

    archivo.write(
        clave_datos_protegida_recuperacion
    )


# ============================================================
# GUARDAR LA CLAVE DE RECUPERACIÓN
# SOLO PARA ESTE LABORATORIO
# ============================================================

with open(
    archivo_clave_recuperacion,
    "wb"
) as archivo:

    archivo.write(
        clave_recuperacion
    )


print()
print("✅ Protección de recuperación guardada.")

print()
print("Archivo:")
print(
    os.path.abspath(
        archivo_recuperacion
    )
)

print()
print("⚠️ Para este laboratorio también")
print("guardamos la clave de recuperación")
print("en un archivo separado.")


# ============================================================
# PRUEBA DE RECUPERACIÓN
# ============================================================

print()
print("4. PROBANDO LA RECUPERACIÓN")
print("----------------------------")

with open(
    archivo_recuperacion,
    "rb"
) as archivo:

    datos_recuperacion = archivo.read()


with open(
    archivo_clave_recuperacion,
    "rb"
) as archivo:

    clave_recuperacion_guardada = archivo.read()


fernet_recuperacion = Fernet(
    clave_recuperacion_guardada
)


clave_datos_recuperada = (
    fernet_recuperacion.decrypt(
        datos_recuperacion
    )
)


print()
print("🔑 CLAVE DE DATOS RECUPERADA:")
print(clave_datos_recuperada)


print()
print("¿Es igual a la clave original?")

if clave_datos == clave_datos_recuperada:

    print("✅ SÍ. SON EXACTAMENTE IGUALES.")

else:

    print("❌ NO. SON DIFERENTES.")


print()
print("==============================================")
print("LABORATORIO 8 FINALIZADO")
print("==============================================")