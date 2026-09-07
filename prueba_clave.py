
#  ------------------------  Prueba_clave.py ----------------------
import secrets

# Generamos una clave aleatoria de 32 bytes
clave_datos = secrets.token_bytes(32)

print("Clave generada:")
print(clave_datos)

print()
print("Cantidad de bytes:", len(clave_datos))
print("Cantidad de bits:", len(clave_datos) * 8)

# --------------------------------------------------------