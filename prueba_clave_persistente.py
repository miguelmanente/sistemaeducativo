import os
import secrets
import ctypes
from ctypes import wintypes


# ============================================================
# ARCHIVO DONDE SE GUARDARÁ LA CLAVE PROTEGIDA
# ============================================================

archivo_clave = "clave_datos_sge.protegida"


# ============================================================
# ESTRUCTURA QUE UTILIZA WINDOWS PARA LOS DATOS
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
# PROTEGER DATOS CON DPAPI
# ============================================================

def proteger_datos(datos):

    buffer_entrada = ctypes.create_string_buffer(datos)

    entrada = DATA_BLOB(
        len(datos),
        ctypes.cast(
            buffer_entrada,
            ctypes.POINTER(ctypes.c_byte)
        )
    )

    salida = DATA_BLOB()

    resultado = crypt32.CryptProtectData(
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
# DESPROTEGER DATOS CON DPAPI
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
# COMIENZA EL PROGRAMA
# ============================================================

print("==============================================")
print("   LABORATORIO 7 - CLAVE PERSISTENTE")
print("==============================================")

print()
print("Archivo de clave protegida:")
print(os.path.abspath(archivo_clave))


# ============================================================
# PRIMERA EJECUCIÓN
# ============================================================

if not os.path.exists(archivo_clave):

    print()
    print("PRIMERA EJECUCIÓN")
    print("------------------")

    # Generamos una única clave de datos
    clave_datos = secrets.token_bytes(32)

    print()
    print("🔑 CLAVE DE DATOS GENERADA:")
    print(clave_datos)

    print()
    print("Cantidad de bytes:")
    print(len(clave_datos))

    print()
    print("Protegiendo la clave con DPAPI...")

    clave_protegida = proteger_datos(clave_datos)

    # Guardamos solamente la versión protegida
    with open(archivo_clave, "wb") as archivo:
        archivo.write(clave_protegida)

    print()
    print("✅ La clave protegida fue guardada.")

    print()
    print("Tamaño de la clave original:")
    print(len(clave_datos), "bytes")

    print()
    print("Tamaño de la clave protegida:")
    print(len(clave_protegida), "bytes")

    print()
    print("⚠️ La clave original NO fue guardada en disco.")


# ============================================================
# EJECUCIONES POSTERIORES
# ============================================================

else:

    print()
    print("EJECUCIÓN POSTERIOR")
    print("--------------------")

    # Leemos la clave protegida
    with open(archivo_clave, "rb") as archivo:
        clave_protegida = archivo.read()

    print()
    print("Tamaño de la clave protegida:")
    print(len(clave_protegida), "bytes")

    print()
    print("Recuperando la clave mediante DPAPI...")

    clave_datos = desproteger_datos(
        clave_protegida
    )

    print()
    print("🔑 CLAVE DE DATOS RECUPERADA:")
    print(clave_datos)

    print()
    print("Cantidad de bytes:")
    print(len(clave_datos))

    if len(clave_datos) == 32:

        print()
        print("✅ La clave recuperada tiene 32 bytes.")

    else:

        print()
        print("❌ La clave recuperada NO tiene el tamaño esperado.")


# ============================================================
# LA CLAVE QUEDA DISPONIBLE EN MEMORIA
# ============================================================

print()
print("==============================================")
print("La clave de datos está disponible en memoria.")
print("==============================================")