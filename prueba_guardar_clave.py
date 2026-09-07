# ------------------------  Prueba_guardar_clave.py ----------------------
import secrets
import os

# ==========================================================
# 1. GENERAMOS LA CLAVE DE DATOS
# ==========================================================

clave_datos = secrets.token_bytes(32)

print("CLAVE ORIGINAL:")
print(clave_datos)


# ==========================================================
# 2. GUARDAMOS LA CLAVE EN UN ARCHIVO
# ==========================================================

archivo_clave = "clave_datos.key"

with open(archivo_clave, "wb") as archivo:
    archivo.write(clave_datos)

print()
print("Clave guardada en:", os.path.abspath(archivo_clave))


# ==========================================================
# 3. VOLVEMOS A LEER LA CLAVE
# ==========================================================

with open(archivo_clave, "rb") as archivo:
    clave_recuperada = archivo.read()

print()
print("CLAVE RECUPERADA:")
print(clave_recuperada)


# ==========================================================
# 4. COMPROBAMOS SI SON IGUALES
# ==========================================================

print()

if clave_datos == clave_recuperada:
    print("✅ Las claves son exactamente iguales.")
else:
    print("❌ Las claves son diferentes.")

# ------------------------------------------------------------------------------