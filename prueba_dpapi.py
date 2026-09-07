# ------------------------  Prueba_dpapi.py ----------------------
import os
import ctypes
from ctypes import wintypes


# ==========================================================
# CONFIGURACIÓN DE WINDOWS DPAPI
# ==========================================================

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte))
    ]


crypt32 = ctypes.windll.crypt32
kernel32 = ctypes.windll.kernel32


# ==========================================================
# PROTEGER DATOS
# ==========================================================

def proteger_datos(datos):
    entrada = DATA_BLOB(
        len(datos),
        ctypes.cast(
            ctypes.create_string_buffer(datos),
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
        return ctypes.string_at(salida.pbData, salida.cbData)
    finally:
        kernel32.LocalFree(salida.pbData)


# ==========================================================
# DESPROTEGER DATOS
# ==========================================================

def desproteger_datos(datos_protegidos):
    entrada = DATA_BLOB(
        len(datos_protegidos),
        ctypes.cast(
            ctypes.create_string_buffer(datos_protegidos),
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
        return ctypes.string_at(salida.pbData, salida.cbData)
    finally:
        kernel32.LocalFree(salida.pbData)


# ==========================================================
# PRUEBA
# ==========================================================

clave_original = os.urandom(32)

print("CLAVE ORIGINAL:")
print(clave_original)

clave_protegida = proteger_datos(clave_original)

print()
print("CLAVE PROTEGIDA:")
print(clave_protegida)

print()
print("¿Son iguales?")
print(clave_original == clave_protegida)

clave_recuperada = desproteger_datos(clave_protegida)

print()
print("CLAVE RECUPERADA:")
print(clave_recuperada)

print()
print("¿La clave recuperada es igual a la original?")
print(clave_original == clave_recuperada)
# --------------------------------------------------------------------------------