import sqlite3
import os

archivo_bd = "bdescuela_prueba.db"

print("BASE DE DATOS:")
print(os.path.abspath(archivo_bd))

conn = sqlite3.connect(archivo_bd)

cursor = conn.cursor()

cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
    ORDER BY name
""")

tablas = cursor.fetchall()

print()
print("TABLAS ENCONTRADAS:")

for tabla in tablas:
    print("-", tabla[0])

conn.close()

print()
print("✅ La base de prueba pudo abrirse correctamente.")
