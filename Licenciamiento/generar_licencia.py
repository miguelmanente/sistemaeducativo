
# =====================================================
#       GENERADOR DE LICENCIAS SGE
# =====================================================

import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# =====================================================
#                 CONFIGURACIÓN
# =====================================================

VERSION_SGE = "1.0"

CARPETA_BASE = Path(__file__).resolve().parent
CARPETA_CLAVES = CARPETA_BASE / "claves"

ARCHIVO_SOLICITUD = CARPETA_BASE / "Solicitud_SGE.dat"
ARCHIVO_CLAVE_PRIVADA = CARPETA_CLAVES / "clave_privada.pem"

ARCHIVO_LICENCIA = CARPETA_BASE / "Licencia_SGE.lic"
ARCHIVO_LICENCIA_VENCIDA = CARPETA_BASE / "Licencia_SGE_Vencida.lic"


# =====================================================
#           CARGAR CLAVE PRIVADA
# =====================================================

def cargar_clave_privada():

    if not ARCHIVO_CLAVE_PRIVADA.exists():
        raise FileNotFoundError(
            "No se encontró la clave privada:\n"
            f"{ARCHIVO_CLAVE_PRIVADA}"
        )

    with open(ARCHIVO_CLAVE_PRIVADA, "rb") as archivo:
        clave = serialization.load_pem_private_key(
            archivo.read(),
            password=None
        )

    if not isinstance(clave, Ed25519PrivateKey):
        raise TypeError(
            "La clave privada no es una clave Ed25519 válida."
        )

    return clave


# =====================================================
#           CARGAR SOLICITUD
# =====================================================

def cargar_solicitud():

    if not ARCHIVO_SOLICITUD.exists():
        raise FileNotFoundError(
            "No se encontró el archivo de solicitud:\n"
            f"{ARCHIVO_SOLICITUD}"
        )

    with open(ARCHIVO_SOLICITUD, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


# =====================================================
#       MOSTRAR DATOS DE LA SOLICITUD
# =====================================================

def mostrar_solicitud(solicitud):

    print()
    print("=" * 60)
    print("              SOLICITUD DE LICENCIA SGE")
    print("=" * 60)

    print(f"Institución : {solicitud.get('institucion')}")
    print(f"Localidad   : {solicitud.get('localidad')}")
    print(f"Provincia   : {solicitud.get('provincia')}")
    print(f"ID solicitud: {solicitud.get('id_solicitud')}")
    print(f"Fecha       : {solicitud.get('fecha_solicitud')}")

    print("=" * 60)


# =====================================================
#          GENERAR FIRMA DIGITAL
# =====================================================

def firmar_datos(clave_privada, datos):

    datos_canonicos = json.dumps(
        datos,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    ).encode("utf-8")

    firma = clave_privada.sign(datos_canonicos)

    return firma


# =====================================================
#          INGRESAR FECHA PERSONALIZADA
# =====================================================

def solicitar_fecha_vencimiento():

    while True:

        fecha_texto = input(
            "\nIngrese la fecha de vencimiento "
            "(DD/MM/AAAA): "
        ).strip()

        try:

            fecha = datetime.strptime(
                fecha_texto,
                "%d/%m/%Y"
            )

            return fecha.strftime("%Y-%m-%d")

        except ValueError:

            print(
                "❌ Fecha inválida. "
                "Utilice el formato DD/MM/AAAA."
            )


# =====================================================
#             GENERAR LICENCIA
# =====================================================

def generar_licencia():

    try:
        solicitud = cargar_solicitud()
        clave_privada = cargar_clave_privada()

    except Exception as e:

        print()
        print("❌ ERROR")
        print(e)
        return

    # -------------------------------------------------
    # Mostrar solicitud
    # -------------------------------------------------

    mostrar_solicitud(solicitud)

    # -------------------------------------------------
    # Confirmar generación
    # -------------------------------------------------

    respuesta = input(
        "\n¿Desea generar una licencia para esta solicitud? "
        "(S/N): "
    ).strip().upper()

    if respuesta != "S":
        print("\nOperación cancelada.")
        return

    # -------------------------------------------------
    # Tipo de licencia
    # -------------------------------------------------

    print()
    print("Tipo de licencia:")
    print()
    print("1. Permanente")
    print("2. Anual")
    print("3. Prueba")
    print("4. Prueba vencida")
    print()

    while True:

        opcion = input("Seleccione una opción (1-4): ").strip()

        if opcion in ("1", "2", "3", "4"):
            break

        print("❌ Opción inválida.")

    # -------------------------------------------------
    # Versión
    # -------------------------------------------------

    version = input(
        f"\nVersión de SGE [{VERSION_SGE}]: "
    ).strip()

    if not version:
        version = VERSION_SGE

    # -------------------------------------------------
    # Fechas
    # -------------------------------------------------

    fecha_emision = datetime.now()

    fecha_vencimiento = None

    # -------------------------------------------------
    # Permanente
    # -------------------------------------------------

    if opcion == "1":

        tipo = "permanente"

        fecha_vencimiento = None

    # -------------------------------------------------
    # Anual
    # -------------------------------------------------

    elif opcion == "2":

        tipo = "anual"

        fecha_vencimiento = (
            fecha_emision + timedelta(days=365)
        ).strftime("%Y-%m-%d")

    # -------------------------------------------------
    # Prueba
    # -------------------------------------------------

    elif opcion == "3":

        tipo = "prueba"

        while True:

            dias_texto = input(
                "\nCantidad de días de prueba: "
            ).strip()

            try:

                dias = int(dias_texto)

                if dias <= 0:
                    print(
                        "❌ La cantidad de días "
                        "debe ser mayor que cero."
                    )
                    continue

                break

            except ValueError:

                print(
                    "❌ Ingrese una cantidad de días válida."
                )

        fecha_vencimiento = (
            fecha_emision + timedelta(days=dias)
        ).strftime("%Y-%m-%d")

    # -------------------------------------------------
    # Prueba vencida
    # -------------------------------------------------

    else:

        tipo = "prueba"

        print()
        print(
            "⚠ MODO DE PRUEBA DE LICENCIA VENCIDA"
        )
        print(
            "Esta opción permite generar una licencia "
            "firmada con una fecha de vencimiento "
            "personalizada."
        )
        print()

        fecha_vencimiento = solicitar_fecha_vencimiento()

        # Para evitar generar accidentalmente una
        # licencia que todavía no esté vencida.
        fecha_vencimiento_dt = datetime.strptime(
            fecha_vencimiento,
            "%Y-%m-%d"
        )

        if fecha_vencimiento_dt.date() >= fecha_emision.date():

            print()
            print(
                "❌ La fecha ingresada no corresponde "
                "a una licencia vencida."
            )
            print(
                "Ingrese una fecha anterior a hoy."
            )
            return

    # -------------------------------------------------
    # Generar ID de licencia
    # -------------------------------------------------

    id_licencia = (
        f"SGE-{fecha_emision.year}-"
        f"{uuid.uuid4().hex[:8].upper()}"
    )

    # -------------------------------------------------
    # Datos de la licencia
    # -------------------------------------------------

    datos_licencia = {
        "producto": "SGE",
        "id_licencia": id_licencia,
        "id_solicitud": solicitud.get("id_solicitud"),
        "institucion": solicitud.get("institucion"),
        "localidad": solicitud.get("localidad"),
        "provincia": solicitud.get("provincia"),
        "tipo": tipo,
        "version": version,
        "fecha_emision": fecha_emision.strftime("%Y-%m-%d"),
        "fecha_vencimiento": fecha_vencimiento
    }

    # -------------------------------------------------
    # Firmar
    # -------------------------------------------------

    firma = firmar_datos(
        clave_privada,
        datos_licencia
    )

    # -------------------------------------------------
    # Crear archivo final
    # -------------------------------------------------

    licencia_completa = {
        "datos": datos_licencia,
        "firma": __import__("base64").b64encode(
            firma
        ).decode("ascii")
    }

    # -------------------------------------------------
    # Seleccionar archivo de salida
    # -------------------------------------------------

    if opcion == "4":
        archivo_salida = ARCHIVO_LICENCIA_VENCIDA
    else:
        archivo_salida = ARCHIVO_LICENCIA

    # -------------------------------------------------
    # Guardar licencia
    # -------------------------------------------------

    with open(
        archivo_salida,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            licencia_completa,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    # -------------------------------------------------
    # Mostrar resultado
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("             LICENCIA GENERADA")
    print("=" * 60)

    print(f"ID licencia       : {id_licencia}")
    print(
        f"Institución       : "
        f"{datos_licencia['institucion']}"
    )
    print(
        f"Localidad         : "
        f"{datos_licencia['localidad']}"
    )
    print(
        f"Provincia         : "
        f"{datos_licencia['provincia']}"
    )
    print(f"Tipo              : {tipo}")
    print(f"Versión           : {version}")
    print(
        f"Fecha de emisión  : "
        f"{datos_licencia['fecha_emision']}"
    )
    print(
        f"Fecha vencimiento : "
        f"{datos_licencia['fecha_vencimiento']}"
    )

    print()
    print(f"Archivo generado:")
    print(archivo_salida)

    print("=" * 60)


# =====================================================
#                    PROGRAMA
# =====================================================

if __name__ == "__main__":

    generar_licencia()

