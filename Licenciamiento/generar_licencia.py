
# =====================================================
#       GENERADOR DE LICENCIAS SGE
# =====================================================

import json
import uuid
import base64

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

    with open(
        ARCHIVO_SOLICITUD,
        "r",
        encoding="utf-8"
    ) as archivo:

        return json.load(archivo)


# =====================================================
#       MOSTRAR DATOS DE LA SOLICITUD
# =====================================================

def mostrar_solicitud(solicitud):

    print()
    print("=" * 60)
    print("              SOLICITUD DE LICENCIA SGE")
    print("=" * 60)

    print(
        f"Institución : "
        f"{solicitud.get('institucion')}"
    )

    print(
        f"Localidad   : "
        f"{solicitud.get('localidad')}"
    )

    print(
        f"Provincia   : "
        f"{solicitud.get('provincia')}"
    )

    print(
        f"ID solicitud: "
        f"{solicitud.get('id_solicitud')}"
    )

    print(
        f"Fecha       : "
        f"{solicitud.get('fecha_solicitud')}"
    )

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

    firma = clave_privada.sign(
        datos_canonicos
    )

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

            return fecha.strftime(
                "%Y-%m-%d"
            )

        except ValueError:

            print(
                "❌ Fecha inválida. "
                "Utilice el formato DD/MM/AAAA."
            )


# =====================================================
#       VALIDAR DATOS DE LA SOLICITUD
# =====================================================

def validar_solicitud(solicitud):

    if not isinstance(solicitud, dict):
        raise ValueError(
            "La solicitud no tiene un formato válido."
        )

    campos_requeridos = (
        "producto",
        "id_solicitud",
        "institucion",
        "localidad",
        "provincia",
        "fecha_solicitud"
    )

    for campo in campos_requeridos:

        if campo not in solicitud:

            raise ValueError(
                f"Falta el campo '{campo}' "
                "en la solicitud."
            )

    if solicitud.get("producto") != "SGE":

        raise ValueError(
            "La solicitud no corresponde al SGE."
        )


# =====================================================
#       GENERAR DATOS DE UNA LICENCIA
# =====================================================

def preparar_datos_licencia(
    solicitud,
    tipo,
    version=VERSION_SGE,
    dias_prueba=None,
    fecha_vencimiento_personalizada=None
):
    """
    Prepara los datos que serán firmados.

    Esta función NO firma ni guarda la licencia.
    """

    validar_solicitud(solicitud)

    tipos_validos = (
        "permanente",
        "anual",
        "prueba"
    )

    if tipo not in tipos_validos:

        raise ValueError(
            "Tipo de licencia inválido."
        )

    if not version:
        version = VERSION_SGE

    fecha_emision = datetime.now()

    fecha_vencimiento = None

    # -------------------------------------------------
    # Permanente
    # -------------------------------------------------

    if tipo == "permanente":

        fecha_vencimiento = None

    # -------------------------------------------------
    # Anual
    # -------------------------------------------------

    elif tipo == "anual":

        fecha_vencimiento = (
            fecha_emision +
            timedelta(days=365)
        ).strftime("%Y-%m-%d")

    # -------------------------------------------------
    # Prueba
    # -------------------------------------------------

    elif tipo == "prueba":

        if dias_prueba is None:

            raise ValueError(
                "Debe indicar la cantidad de días "
                "para la licencia de prueba."
            )

        try:
            dias_prueba = int(dias_prueba)

        except (TypeError, ValueError):

            raise ValueError(
                "La cantidad de días de prueba "
                "no es válida."
            )

        if dias_prueba <= 0:

            raise ValueError(
                "La cantidad de días de prueba "
                "debe ser mayor que cero."
            )

        fecha_vencimiento = (
            fecha_emision +
            timedelta(days=dias_prueba)
        ).strftime("%Y-%m-%d")

    # -------------------------------------------------
    # ID de licencia
    # -------------------------------------------------

    id_licencia = (
        f"SGE-{fecha_emision.year}-"
        f"{uuid.uuid4().hex[:8].upper()}"
    )

    # -------------------------------------------------
    # Datos
    # -------------------------------------------------

    datos_licencia = {

        "producto": "SGE",

        "id_licencia": id_licencia,

        "id_solicitud":
            solicitud.get("id_solicitud"),

        "institucion":
            solicitud.get("institucion"),

        "localidad":
            solicitud.get("localidad"),

        "provincia":
            solicitud.get("provincia"),

        "tipo":
            tipo,

        "version":
            version,

        "fecha_emision":
            fecha_emision.strftime("%Y-%m-%d"),

        "fecha_vencimiento":
            fecha_vencimiento
    }

    return datos_licencia


# =====================================================
#          GENERAR Y FIRMAR LICENCIA
# =====================================================

def generar_licencia_desde_datos(
    solicitud,
    tipo,
    version=VERSION_SGE,
    dias_prueba=None,
    ruta_salida=None
):
    """
    Genera y firma una licencia a partir de una solicitud.

    Esta función está pensada para ser utilizada por
    el Administrador de Licencias SGE.

    Devuelve:

        (datos_licencia, ruta_archivo)

    """

    # -------------------------------------------------
    # Cargar clave privada
    # -------------------------------------------------

    clave_privada = cargar_clave_privada()

    # -------------------------------------------------
    # Preparar datos
    # -------------------------------------------------

    datos_licencia = preparar_datos_licencia(
        solicitud=solicitud,
        tipo=tipo,
        version=version,
        dias_prueba=dias_prueba
    )

    # -------------------------------------------------
    # Firmar
    # -------------------------------------------------

    firma = firmar_datos(
        clave_privada,
        datos_licencia
    )

    # -------------------------------------------------
    # Crear archivo completo
    # -------------------------------------------------

    licencia_completa = {

        "datos":
            datos_licencia,

        "firma":
            base64.b64encode(
                firma
            ).decode("ascii")
    }

    # -------------------------------------------------
    # Determinar archivo de salida
    # -------------------------------------------------

    if ruta_salida is None:

        ruta_salida = ARCHIVO_LICENCIA

    else:

        ruta_salida = Path(ruta_salida)

    # -------------------------------------------------
    # Guardar licencia
    # -------------------------------------------------

    with open(
        ruta_salida,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            licencia_completa,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    return (
        datos_licencia,
        ruta_salida
    )


# =====================================================
#             GENERAR LICENCIA DESDE CONSOLA
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

    mostrar_solicitud(
        solicitud
    )

    # -------------------------------------------------
    # Confirmar generación
    # -------------------------------------------------

    respuesta = input(
        "\n¿Desea generar una licencia para "
        "esta solicitud? (S/N): "
    ).strip().upper()

    if respuesta != "S":

        print(
            "\nOperación cancelada."
        )

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

        opcion = input(
            "Seleccione una opción (1-4): "
        ).strip()

        if opcion in (
            "1",
            "2",
            "3",
            "4"
        ):
            break

        print(
            "❌ Opción inválida."
        )

    # -------------------------------------------------
    # Versión
    # -------------------------------------------------

    version = input(
        f"\nVersión de SGE [{VERSION_SGE}]: "
    ).strip()

    if not version:

        version = VERSION_SGE

    # -------------------------------------------------
    # Permanente
    # -------------------------------------------------

    if opcion == "1":

        tipo = "permanente"

        try:

            datos_licencia, archivo_salida = (
                generar_licencia_desde_datos(
                    solicitud,
                    tipo,
                    version
                )
            )

        except Exception as e:

            print()
            print("❌ ERROR")
            print(e)

            return

    # -------------------------------------------------
    # Anual
    # -------------------------------------------------

    elif opcion == "2":

        tipo = "anual"

        try:

            datos_licencia, archivo_salida = (
                generar_licencia_desde_datos(
                    solicitud,
                    tipo,
                    version
                )
            )

        except Exception as e:

            print()
            print("❌ ERROR")
            print(e)

            return

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

                dias = int(
                    dias_texto
                )

                if dias <= 0:

                    print(
                        "❌ La cantidad de días "
                        "debe ser mayor que cero."
                    )

                    continue

                break

            except ValueError:

                print(
                    "❌ Ingrese una cantidad de "
                    "días válida."
                )

        try:

            datos_licencia, archivo_salida = (
                generar_licencia_desde_datos(
                    solicitud,
                    tipo,
                    version,
                    dias_prueba=dias
                )
            )

        except Exception as e:

            print()
            print("❌ ERROR")
            print(e)

            return

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

        fecha_vencimiento = (
            solicitar_fecha_vencimiento()
        )

        fecha_emision = datetime.now()

        fecha_vencimiento_dt = datetime.strptime(
            fecha_vencimiento,
            "%Y-%m-%d"
        )

        if (
            fecha_vencimiento_dt.date()
            >= fecha_emision.date()
        ):

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
        # Para mantener la misma lógica de la versión
        # original, la licencia vencida se genera aquí
        # directamente.
        # -------------------------------------------------

        try:

            clave_privada = cargar_clave_privada()

            fecha_emision = datetime.now()

            id_licencia = (
                f"SGE-{fecha_emision.year}-"
                f"{uuid.uuid4().hex[:8].upper()}"
            )

            datos_licencia = {

                "producto": "SGE",

                "id_licencia":
                    id_licencia,

                "id_solicitud":
                    solicitud.get(
                        "id_solicitud"
                    ),

                "institucion":
                    solicitud.get(
                        "institucion"
                    ),

                "localidad":
                    solicitud.get(
                        "localidad"
                    ),

                "provincia":
                    solicitud.get(
                        "provincia"
                    ),

                "tipo":
                    tipo,

                "version":
                    version,

                "fecha_emision":
                    fecha_emision.strftime(
                        "%Y-%m-%d"
                    ),

                "fecha_vencimiento":
                    fecha_vencimiento
            }

            firma = firmar_datos(
                clave_privada,
                datos_licencia
            )

            licencia_completa = {

                "datos":
                    datos_licencia,

                "firma":
                    base64.b64encode(
                        firma
                    ).decode("ascii")
            }

            archivo_salida = (
                ARCHIVO_LICENCIA_VENCIDA
            )

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

        except Exception as e:

            print()
            print("❌ ERROR")
            print(e)

            return

    # -------------------------------------------------
    # Mostrar resultado
    # -------------------------------------------------

    print()

    print("=" * 60)

    print(
        "             LICENCIA GENERADA"
    )

    print("=" * 60)

    print(
        f"ID licencia       : "
        f"{datos_licencia['id_licencia']}"
    )

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

    print(
        f"Tipo              : "
        f"{datos_licencia['tipo']}"
    )

    print(
        f"Versión           : "
        f"{datos_licencia['version']}"
    )

    print(
        f"Fecha de emisión  : "
        f"{datos_licencia['fecha_emision']}"
    )

    print(
        f"Fecha vencimiento : "
        f"{datos_licencia['fecha_vencimiento']}"
    )

    print()

    print(
        "Archivo generado:"
    )

    print(
        archivo_salida
    )

    print("=" * 60)


# =====================================================
#                    PROGRAMA
# =====================================================

if __name__ == "__main__":

    generar_licencia()

