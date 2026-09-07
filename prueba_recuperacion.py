import secrets

from cryptography.fernet import Fernet

clave_datos = secrets.token_bytes(32)

clave_recuperacion = Fernet.generate_key()

fernet = Fernet(clave_recuperacion)
clave_datos_protegida = fernet.encrypt(clave_datos)

print("CLAVE DE DATOS:")
print(clave_datos)

print()
print("CLAVE DE RECUPERACIÓN:")
print(clave_recuperacion)

print()
print("CLAVE DE RECUPERACIÓN:")
print(fernet)

print()
print("CLAVE DE DATOS PROTEGIDA:")
print(clave_datos_protegida)

clave_recuperada = fernet.decrypt(clave_datos_protegida)

print()
print("CLAVE RECUPERADA:")
print(clave_recuperada)

print()
print("¿La clave recuperada es igual a la original?")
print(clave_datos == clave_recuperada)