
# ============================================================
#             GENERADOR DE SOLICITUD DE LICENCIA SGE
# ============================================================

import json
import os
import uuid
from datetime import datetime

from huella_equipo import obtener_huella_equipo


# ============================================================
#                    UBICACIÓN DEL ARCHIVO
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ARCHIVO_SOLICITUD = os.path.join(
    BASE_DIR,
    "Solicitud_SGE.dat"
)


# ============================================================
#                    ENCABEZADO
# ============================================================

print()
print("============================================================")
print("          SOLICITUD DE LICENCIA DEL SGE")
print("============================================================")
print()

print("Este programa genera una solicitud para que el")
print("administrador del SGE pueda emitir una licencia.")
print()


# ============================================================
#                  DATOS DE LA INSTITUCIÓN
# ============================================================

institucion = input(
    "Nombre de la institución: "
).strip()

localidad = input(
    "Localidad: "
).strip()

provincia = input(
    "Provincia: "
).strip()


# ============================================================
#                 VALIDAR DATOS
# ============================================================

if not institucion:

    print()
    print("ERROR: Debes ingresar el nombre de la institución.")
    print()

    raise SystemExit(1)


if not localidad:

    print()
    print("ERROR: Debes ingresar la localidad.")
    print()

    raise SystemExit(1)


if not provincia:

    print()
    print("ERROR: Debes ingresar la provincia.")
    print()

    raise SystemExit(1)


# ============================================================
#               GENERAR IDENTIFICADOR ÚNICO
# ============================================================

id_solicitud = str(uuid.uuid4())


# ============================================================
#                   FECHA DE SOLICITUD
# ============================================================

fecha_solicitud = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# ============================================================
#                OBTENER HUELLA DEL EQUIPO
# ============================================================

huella_equipo = obtener_huella_equipo()


# ============================================================
#                 CREAR DATOS DE SOLICITUD
# ============================================================

solicitud = {

    "producto": "SGE",

    "id_solicitud": id_solicitud,

    "institucion": institucion,

    "localidad": localidad,

    "provincia": provincia,

    "fecha_solicitud": fecha_solicitud,

    "huella_equipo": huella_equipo

}


# ============================================================
#                 GUARDAR ARCHIVO
# ============================================================

with open(
    ARCHIVO_SOLICITUD,
    "w",
    encoding="utf-8"
) as archivo:

    json.dump(
        solicitud,
        archivo,
        ensure_ascii=False,
        indent=4
    )


# ============================================================
#                       RESULTADO
# ============================================================

print()
print("============================================================")
print("             SOLICITUD GENERADA CORRECTAMENTE")
print("============================================================")
print()

print("Archivo:")
print(ARCHIVO_SOLICITUD)

print()
print("Institución :", institucion)
print("Localidad   :", localidad)
print("Provincia   :", provincia)

print()
print("Identificador de solicitud:")
print(id_solicitud)

print()
print("Fecha:")
print(fecha_solicitud)

print()
print("Huella del equipo:")
print(huella_equipo)

print()
print("La solicitud puede ser enviada al")
print("administrador para generar la licencia.")
print()
