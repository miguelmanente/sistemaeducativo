
# ============================================================
# prueba_integridad_nueva.py
# Laboratorio de integridad del backup del SGE
#
# Objetivo:
#   - Tomar un backup cifrado real de laboratorio
#   - Crear una copia manipulada
#   - Modificar un solo byte
#   - Intentar restaurarla
#   - Comprobar que Fernet rechaza el backup
#
# IMPORTANTE:
#   Este laboratorio NO modifica:
#   - la base de datos original
#   - la base de datos de laboratorio
#   - el backup original
#
#   Solamente crea una copia manipulada para la prueba.
# ============================================================

import os
import sys

from cryptography.fernet import InvalidToken

from restauracion_nueva import descifrar_backup


# ------------------------------------------------------------
# UBICACIÓN BASE DEL SGE
# ------------------------------------------------------------

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# RUTAS DEL LABORATORIO
# ------------------------------------------------------------

CARPETA_BACKUPS = os.path.join(
    BASE_DIR,
    "backups_prueba"
)

NOMBRE_BACKUP_MANIPULADO = (
    "backup_sge_manipulado.enc"
)

RUTA_BACKUP_MANIPULADO = os.path.join(
    CARPETA_BACKUPS,
    NOMBRE_BACKUP_MANIPULADO
)

RUTA_BD_QUE_NO_DEBERIA_CREARSE = os.path.join(
    BASE_DIR,
    "bdescuela_no_deberia_crearse.db"
)


# ------------------------------------------------------------
# BUSCAR EL BACKUP ORIGINAL
# ------------------------------------------------------------

def obtener_backup_original():
    if not os.path.isdir(CARPETA_BACKUPS):
        raise FileNotFoundError(
            "No existe la carpeta de backups de laboratorio:\n\n"
            f"{CARPETA_BACKUPS}"
        )

    archivos = [
        archivo
        for archivo in os.listdir(CARPETA_BACKUPS)
        if archivo.endswith(".enc")
        and archivo != NOMBRE_BACKUP_MANIPULADO
    ]

    if not archivos:
        raise FileNotFoundError(
            "No se encontró ningún backup .enc "
            "para realizar la prueba."
        )

    archivos.sort()

    return os.path.join(
        CARPETA_BACKUPS,
        archivos[-1]
    )


# ------------------------------------------------------------
# CREAR COPIA MANIPULADA
# ------------------------------------------------------------

def crear_backup_manipulado(
    ruta_backup_original,
    ruta_backup_manipulado
):
    with open(ruta_backup_original, "rb") as archivo:
        datos = bytearray(
            archivo.read()
        )

    if not datos:
        raise ValueError(
            "El backup original está vacío."
        )

    # Elegimos una posición interna del archivo.
    posicion = 100

    if len(datos) <= posicion:
        raise ValueError(
            "El backup es demasiado pequeño "
            "para realizar esta prueba."
        )

    valor_original = datos[posicion]

    # Cambiamos un solo byte.
    if valor_original == 255:
        nuevo_valor = 0
    else:
        nuevo_valor = valor_original + 1

    datos[posicion] = nuevo_valor

    with open(ruta_backup_manipulado, "wb") as archivo:
        archivo.write(datos)

    return posicion, valor_original, nuevo_valor


# ------------------------------------------------------------
# PRUEBA PRINCIPAL
# ------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBA DE INTEGRIDAD DEL BACKUP DEL SGE")
    print("=" * 60)

    try:

        # ----------------------------------------------------
        # 1. Obtener backup original
        # ----------------------------------------------------

        ruta_backup_original = obtener_backup_original()

        print()
        print("📦 BACKUP ORIGINAL:")
        print(ruta_backup_original)

        # ----------------------------------------------------
        # 2. Eliminar resultados anteriores de la prueba
        # ----------------------------------------------------

        if os.path.exists(RUTA_BACKUP_MANIPULADO):
            os.remove(RUTA_BACKUP_MANIPULADO)

        if os.path.exists(RUTA_BD_QUE_NO_DEBERIA_CREARSE):
            os.remove(RUTA_BD_QUE_NO_DEBERIA_CREARSE)

        # ----------------------------------------------------
        # 3. Crear copia manipulada
        # ----------------------------------------------------

        print()
        print("🧪 Creando copia manipulada...")

        posicion, valor_original, nuevo_valor = (
            crear_backup_manipulado(
                ruta_backup_original,
                RUTA_BACKUP_MANIPULADO
            )
        )

        print()
        print("✅ Copia manipulada creada:")
        print(RUTA_BACKUP_MANIPULADO)

        print()
        print("📍 Byte modificado:")
        print("Posición:", posicion)

        print()
        print("Valor original:")
        print(valor_original)

        print()
        print("Nuevo valor:")
        print(nuevo_valor)

        print()
        print("⚠️ Se modificó solamente UN byte.")

        # ----------------------------------------------------
        # 4. Intentar descifrar el backup manipulado
        # ----------------------------------------------------

        print()
        print("🔓 Intentando restaurar el backup manipulado...")

        try:

            descifrar_backup(
                RUTA_BACKUP_MANIPULADO,
                RUTA_BD_QUE_NO_DEBERIA_CREARSE
            )

            # Si llegamos aquí, la prueba falló.

            print()
            print("❌ ATENCIÓN")
            print()
            print(
                "El backup manipulado pudo ser descifrado."
            )

            print()
            print(
                "La prueba de integridad FALLÓ."
            )

        except InvalidToken:

            # ------------------------------------------------
            # RESULTADO ESPERADO
            # ------------------------------------------------

            print()
            print("🛡️ BACKUP RECHAZADO")
            print()
            print(
                "❌ Fernet detectó que el contenido"
            )
            print(
                "   del backup fue alterado o está dañado."
            )

            print()
            print(
                "✅ La restauración fue detenida."
            )

            # ------------------------------------------------
            # 5. Comprobar que NO se creó la base
            # ------------------------------------------------

            if os.path.exists(
                RUTA_BD_QUE_NO_DEBERIA_CREARSE
            ):

                print()
                print(
                    "❌ ERROR:"
                )
                print(
                    "Se creó una base de datos cuando "
                    "no debería haberse creado."
                )

                print()
                print(
                    "La prueba de seguridad FALLÓ."
                )

            else:

                print()
                print(
                    "✅ No se creó ninguna base de datos."
                )

                print()
                print(
                    "🎉 INTEGRIDAD VERIFICADA."
                )

                print()
                print(
                    "El SGE rechazó correctamente "
                    "el backup manipulado."
                )

        # ----------------------------------------------------
        # 6. Comprobar que el original sigue intacto
        # ----------------------------------------------------

        print()
        print("🔍 Verificando que el backup original "
              "siga intacto...")

        with open(
            ruta_backup_original,
            "rb"
        ) as archivo:

            datos_original = archivo.read()

        with open(
            RUTA_BACKUP_MANIPULADO,
            "rb"
        ) as archivo:

            datos_manipulado = archivo.read()

        if datos_original != datos_manipulado:

            print()
            print(
                "✅ El backup manipulado es diferente "
                "del original."
            )

            print()
            print(
                "✅ El backup original NO fue modificado."
            )

        else:

            print()
            print(
                "❌ ERROR: el backup original y "
                "el manipulado son iguales."
            )

        print()
        print("=" * 60)
        print("PRUEBA FINALIZADA")
        print("=" * 60)

    except Exception as error:

        print()
        print("❌ ERROR INESPERADO")
        print()
        print(str(error))
        print()
        print("=" * 60)

