from PIL import Image

# Archivo original
entrada = "SGE_original.ico"

# Nuevo icono
salida = "SGE.ico"

# Abrir imagen
img = Image.open(entrada)

# Asegurar formato RGBA
img = img.convert("RGBA")

# Tamaños estándar de iconos de Windows
tamanos = [
    (16, 16),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
]

# Crear el ICO
img.save(
    salida,
    format="ICO",
    sizes=tamanos
)

print("Icono creado correctamente.")