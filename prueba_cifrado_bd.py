import os
import secrets
import base64
from cryptography.fernet import Fernet


# ==========================================
# ARCHIVOS DEL LABORATORIO
# ==========================================

archivo_backup = "backup_prueba.db"
archivo_cifrado = "backup_prueba.enc"
archivo_recuperado = "backup_recuperado.db"


# ==========================================
# 1. GENERAR LA CLAVE DE DATOS
# ==========================================

clave_datos = secrets.token_bytes(32)

print("CLAVE DE DATOS:")
print(clave_datos)

print()
print("Cantidad de bytes:", len(clave_datos))
print("Cantidad de bits:", len(clave_datos) * 8)


# ==========================================
# 2. ADAPTAR LA CLAVE PARA FERNET
# ==========================================

clave_fernet = base64.urlsafe_b64encode(clave_datos)

fernet = Fernet(clave_fernet)


# ==========================================
# 3. LEER EL BACKUP ORIGINAL
# ==========================================

with open(archivo_backup, "rb") as archivo:
    datos_backup = archivo.read()


print()
print("BACKUP ORIGINAL:")
print(os.path.abspath(archivo_backup))

print()
print("Tamaño del backup original:")
print(len(datos_backup), "bytes")


# ==========================================
# 4. CIFRAR EL BACKUP
# ==========================================

datos_cifrados = fernet.encrypt(datos_backup)


# ==========================================
# 5. GUARDAR EL BACKUP CIFRADO
# ==========================================

with open(archivo_cifrado, "wb") as archivo:
    archivo.write(datos_cifrados)


print()
print("BACKUP CIFRADO:")
print(os.path.abspath(archivo_cifrado))

print()
print("Tamaño del backup cifrado:")
print(len(datos_cifrados), "bytes")


# ==========================================
# 6. DESCIFRAR EL BACKUP
# ==========================================

datos_recuperados = fernet.decrypt(datos_cifrados)


# ==========================================
# 7. GUARDAR EL BACKUP RECUPERADO
# ==========================================

with open(archivo_recuperado, "wb") as archivo:
    archivo.write(datos_recuperados)


print()
print("BACKUP RECUPERADO:")
print(os.path.abspath(archivo_recuperado))

print()
print("Tamaño del backup recuperado:")
print(len(datos_recuperados), "bytes")


# ==========================================
# 8. COMPARAR ORIGINAL Y RECUPERADO
# ==========================================

print()
print("¿El backup recuperado es idéntico al original?")

if datos_backup == datos_recuperados:
    print("✅ SÍ. Los archivos son exactamente iguales.")
else:
    print("❌ NO. Los archivos son diferentes.")


# ==========================================
# 9. COMPROBAR ARCHIVOS
# ==========================================

print()
print("¿Existe el backup cifrado?")
print(os.path.exists(archivo_cifrado))

print()
print("¿Existe el backup recuperado?")
print(os.path.exists(archivo_recuperado))