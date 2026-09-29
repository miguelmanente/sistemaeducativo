
# ============================================================
#          GENERADOR DE CLAVES DEL SISTEMA DE LICENCIAS SGE
# ============================================================

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import os
import sys


# ============================================================
#                    CARPETAS Y ARCHIVOS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_CLAVES = os.path.join(BASE_DIR, "claves")

ARCHIVO_PRIVADA = os.path.join(
    CARPETA_CLAVES,
    "clave_privada.pem"
)

ARCHIVO_PUBLICA = os.path.join(
    CARPETA_CLAVES,
    "clave_publica.pem"
)


# ============================================================
#                  COMPROBAR CLAVES EXISTENTES
# ============================================================

if os.path.exists(ARCHIVO_PRIVADA) or os.path.exists(ARCHIVO_PUBLICA):

    print()
    print("============================================================")
    print("                 CLAVES YA EXISTENTES")
    print("============================================================")
    print()
    print("Ya existen archivos de claves en la carpeta:")
    print(CARPETA_CLAVES)
    print()
    print("NO se generarán nuevas claves.")
    print()
    print("IMPORTANTE:")
    print("No debes generar nuevas claves si ya existen licencias")
    print("emitidas con las claves actuales.")
    print()
    sys.exit(0)


# ============================================================
#                    CREAR CARPETA
# ============================================================

os.makedirs(CARPETA_CLAVES, exist_ok=True)


# ============================================================
#                  GENERAR CLAVE PRIVADA
# ============================================================

print()
print("============================================================")
print("          GENERADOR DE CLAVES DE LICENCIAMIENTO SGE")
print("============================================================")
print()

print("Generando claves criptográficas...")

clave_privada = Ed25519PrivateKey.generate()

clave_publica = clave_privada.public_key()


# ============================================================
#                GUARDAR CLAVE PRIVADA
# ============================================================

datos_clave_privada = clave_privada.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)


with open(ARCHIVO_PRIVADA, "wb") as archivo:
    archivo.write(datos_clave_privada)


# ============================================================
#                 GUARDAR CLAVE PÚBLICA
# ============================================================

datos_clave_publica = clave_publica.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


with open(ARCHIVO_PUBLICA, "wb") as archivo:
    archivo.write(datos_clave_publica)


# ============================================================
#                         RESULTADO
# ============================================================

print()
print("CLAVES GENERADAS CORRECTAMENTE.")
print()
print("Clave privada:")
print(ARCHIVO_PRIVADA)
print()
print("Clave pública:")
print(ARCHIVO_PUBLICA)
print()
print("============================================================")
print("IMPORTANTE")
print("============================================================")
print()
print("La CLAVE PRIVADA es secreta.")
print("NO debe copiarse al SGE ni al instalador.")
print("NO debe enviarse al cliente.")
print()
print("La CLAVE PÚBLICA sí podrá incorporarse al SGE.")
print()
print("============================================================")

