"""
=========================================================
Sistema de Gestión Educativa (SGE)

Archivo: importador.py

Descripción:
Procesa y valida datos para su importación al sistema.

La importación se realiza en dos etapas:

    1. Procesamiento y validación
    2. Confirmación y guardado

Este módulo no depende de Tkinter.

Autor: Miguel Ángel Manente
=========================================================
"""

# ==========================================================
# IMPORTACIONES
# ==========================================================

from datetime import datetime

import openpyxl

from database import conectar

from utilidades import (
    normalizar_nombre,
    normalizar_cuil,
    normalizar_telefono,
    normalizar_fecha,
)

from validaciones import (
    validar_nombre,
    validar_dni,
    dni_existente,
    validar_cuil,
    validar_fecha,
    validar_fecha_nacimiento,
)


# ==========================================================
# RESULTADO DE UNA FILA
# ==========================================================

def crear_resultado(fila):
    """
    Crea la estructura de resultado para una fila importada.
    """

    return {
        "fila": fila,
        "estado": "OK",
        "errores": [],
        "advertencias": [],
        "datos": {},
        "cambios": {}
    }


# ==========================================================
# AGREGAR ERROR
# ==========================================================

def agregar_error(resultado, mensaje):
    """
    Agrega un error a una fila.
    """

    resultado["errores"].append(mensaje)
    resultado["estado"] = "ERROR"


# ==========================================================
# AGREGAR ADVERTENCIA
# ==========================================================

def agregar_advertencia(resultado, mensaje):
    """
    Agrega una advertencia a una fila.
    """

    resultado["advertencias"].append(mensaje)

    if resultado["estado"] == "OK":
        resultado["estado"] = "ADVERTENCIA"


# ==========================================================
# PROCESAR DNI
# ==========================================================

def procesar_dni(dni, resultado):
    """
    Normaliza y valida un DNI.

    Retorna:
        str  -> DNI normalizado.
        None -> Si es inválido.
    """

    if dni is None:
        agregar_error(
            resultado,
            "DNI vacío."
        )
        return None

    dni = str(dni).strip()

    dni = (
        dni
        .replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )

    if not validar_dni(dni):

        agregar_error(
            resultado,
            f"DNI inválido: {dni}"
        )

        return None

    return dni


# ==========================================================
# CARGAR DOCENTES EXISTENTES
# ==========================================================

def cargar_docentes_existentes():
    """
    Carga los docentes existentes desde la tabla profesores.

    La clave del diccionario es el DNI.
    """

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT
                id_docente,
                apellido,
                nombre,
                dni,
                cuil,
                telefono,
                email,
                direccion,
                fecha_nacimiento
            FROM profesores
        """)

        filas = cursor.fetchall()

    finally:

        conn.close()

    docentes = {}

    for fila in filas:

        id_docente = fila[0]
        apellido = fila[1]
        nombre = fila[2]
        dni = fila[3]
        cuil = fila[4]
        telefono = fila[5]
        email = fila[6]
        direccion = fila[7]
        fecha_nacimiento = fila[8]

        if dni is None:
            continue

        dni = str(dni).strip()

        dni = (
            dni
            .replace(".", "")
            .replace("-", "")
            .replace(" ", "")
        )

        docentes[dni] = {
            "id_docente": id_docente,
            "apellido": apellido or "",
            "nombre": nombre or "",
            "dni": dni,
            "cuil": cuil or "",
            "telefono": telefono or "",
            "email": email or "",
            "direccion": direccion or "",
            "fecha_nacimiento": fecha_nacimiento or "",
        }

    return docentes


# ==========================================================
# COMPARAR DOCENTE
# ==========================================================

def comparar_docente(
        datos_importados,
        docente_existente
):
    """
    Compara los datos importados con los existentes.

    Retorna solamente los campos que cambiaron.
    """

    campos_comparables = [
        "apellido",
        "nombre",
        "cuil",
        "telefono",
        "email",
        "direccion",
        "fecha_nacimiento",
    ]

    cambios = {}

    for campo in campos_comparables:

        valor_nuevo = datos_importados.get(
            campo,
            ""
        )

        valor_anterior = docente_existente.get(
            campo,
            ""
        )

        if valor_nuevo is None:
            valor_nuevo = ""

        if valor_anterior is None:
            valor_anterior = ""

        valor_nuevo = str(
            valor_nuevo
        ).strip()

        valor_anterior = str(
            valor_anterior
        ).strip()

        if valor_nuevo != valor_anterior:

            cambios[campo] = {
                "anterior": valor_anterior,
                "nuevo": valor_nuevo
            }

    return cambios


# ==========================================================
# PROCESAR DOCENTE
# ==========================================================

def procesar_docente(
        datos,
        numero_fila,
        docentes_existentes=None
):
    """
    Procesa UNA fila de docente.

    No modifica la base de datos.
    """

    resultado = crear_resultado(
        numero_fila
    )

    # ======================================================
    # OBTENER DATOS
    # ======================================================

    apellido = datos.get(
        "apellido",
        ""
    )

    nombre = datos.get(
        "nombre",
        ""
    )

    dni = datos.get(
        "dni",
        ""
    )

    cuil = datos.get(
        "cuil",
        ""
    )

    telefono = datos.get(
        "telefono",
        ""
    )

    email = datos.get(
        "email",
        ""
    )

    direccion = datos.get(
        "direccion",
        ""
    )

    fecha_nacimiento = datos.get(
        "fecha_nacimiento",
        ""
    )

    # ======================================================
    # NORMALIZAR Y VALIDAR APELLIDO
    # ======================================================

    apellido = normalizar_nombre(
        apellido
    )

    if not apellido:

        agregar_error(
            resultado,
            "Apellido vacío."
        )

    elif not validar_nombre(
        apellido
    ):

        agregar_error(
            resultado,
            f"Apellido inválido: {apellido}"
        )

    # ======================================================
    # NORMALIZAR Y VALIDAR NOMBRE
    # ======================================================

    nombre = normalizar_nombre(
        nombre
    )

    if not nombre:

        agregar_error(
            resultado,
            "Nombre vacío."
        )

    elif not validar_nombre(
        nombre
    ):

        agregar_error(
            resultado,
            f"Nombre inválido: {nombre}"
        )

    # ======================================================
    # PROCESAR DNI
    # ======================================================

    dni = procesar_dni(
        dni,
        resultado
    )

    # ======================================================
    # NORMALIZAR Y VALIDAR CUIL
    # ======================================================

    cuil = normalizar_cuil(
        cuil
    )

    if cuil is None:

        agregar_error(
            resultado,
            "CUIL inválido."
        )

    elif cuil != "" and not validar_cuil(
        cuil
    ):

        agregar_error(
            resultado,
            f"CUIL inválido: {cuil}"
        )

    # ======================================================
    # NORMALIZAR Y VALIDAR TELÉFONO
    # ======================================================

    telefono = normalizar_telefono(
        telefono
    )

    if telefono is None:

        agregar_error(
            resultado,
            "Teléfono inválido."
        )

    # ======================================================
    # NORMALIZAR Y VALIDAR FECHA DE NACIMIENTO
    # ======================================================

    fecha_nacimiento = normalizar_fecha(
        fecha_nacimiento
    )

    if fecha_nacimiento is None:

        agregar_error(
            resultado,
            "Fecha de nacimiento inválida."
        )

    elif fecha_nacimiento != "":

        if not validar_fecha(
            fecha_nacimiento
        ):

            agregar_error(
                resultado,
                f"Fecha de nacimiento inválida: "
                f"{fecha_nacimiento}"
            )

        elif not validar_fecha_nacimiento(
            fecha_nacimiento
        ):

            agregar_error(
                resultado,
                "Fecha de nacimiento no válida "
                "para un docente."
            )

    # ======================================================
    # PREPARAR DATOS NORMALIZADOS
    # ======================================================

    resultado["datos"] = {

        "apellido": apellido,

        "nombre": nombre,

        "dni": dni,

        "cuil": cuil,

        "telefono": telefono,

        "email": str(email).strip(),

        "direccion": str(direccion).strip(),

        "fecha_nacimiento": fecha_nacimiento,
    }

    # ======================================================
    # COMPROBAR SI EL DOCENTE EXISTE
    # ======================================================

    if (
        dni is not None
        and not resultado["errores"]
    ):

        if docentes_existentes is not None:

            docente_existente = (
                docentes_existentes.get(dni)
            )

        else:

            docente_existente = None

            if dni_existente(dni):
                docente_existente = True

        # ==================================================
        # DOCENTE EXISTENTE
        # ==================================================

        if docente_existente:

            if isinstance(
                docente_existente,
                dict
            ):

                cambios = comparar_docente(
                    resultado["datos"],
                    docente_existente
                )

                resultado["datos"][
                    "id_docente"
                ] = docente_existente[
                    "id_docente"
                ]

                if cambios:

                    resultado["estado"] = (
                        "ACTUALIZAR"
                    )

                    resultado["cambios"] = cambios

                    agregar_advertencia(
                        resultado,
                        "El docente ya existe "
                        "y presenta cambios."
                    )

                else:

                    resultado["estado"] = (
                        "SIN_CAMBIOS"
                    )

            else:

                resultado["estado"] = (
                    "EXISTENTE"
                )

                agregar_advertencia(
                    resultado,
                    "El DNI ya existe en "
                    "la base de datos."
                )

        # ==================================================
        # DOCENTE NUEVO
        # ==================================================

        else:

            resultado["estado"] = (
                "NUEVO"
            )

    return resultado


# ==========================================================
# PROCESAR VARIOS DOCENTES
# ==========================================================

def procesar_docentes(filas):
    """
    Procesa TODAS las filas de docentes.

    Esta función llama a procesar_docente()
    en singular para cada fila.

    No modifica la base de datos.
    """

    docentes_existentes = (
        cargar_docentes_existentes()
    )

    resultados = []

    for datos in filas:

        numero_fila = datos.get(
            "_fila_excel",
            0
        )

        resultado = procesar_docente(
            datos,
            numero_fila,
            docentes_existentes
        )

        resultados.append(
            resultado
        )

    return resultados


# ==========================================================
# CONVERTIR VALOR DE EXCEL
# ==========================================================

def convertir_valor_excel(valor):
    """
    Convierte valores de Excel a texto utilizable
    por el importador.
    """

    if valor is None:
        return ""

    if isinstance(
        valor,
        datetime
    ):

        return valor.strftime(
            "%d/%m/%Y"
        )

    if isinstance(
        valor,
        float
    ):

        if valor.is_integer():

            return str(
                int(valor)
            )

        return str(valor)

    return str(valor).strip()


# ==========================================================
# LEER EXCEL DE DOCENTES
# ==========================================================

def leer_excel_docentes(ruta_archivo):
    """
    Lee un archivo Excel proveniente de Google Forms.

    La columna "Marca temporal" se ignora.

    Encabezados actuales:

        Apellido
        Nombres
        DNI
        CUIL
        Teléfono/Celular
        Email
        Dirección
        Fecha de acimiento

    No modifica la base de datos.
    """

    resultado = {
        "filas": [],
        "errores": []
    }

    # ======================================================
    # ABRIR ARCHIVO
    # ======================================================

    try:

        libro = openpyxl.load_workbook(
            ruta_archivo,
            data_only=True
        )

    except Exception as e:

        resultado["errores"].append(
            f"No se pudo abrir el archivo: {e}"
        )

        return resultado

    # ======================================================
    # HOJA ACTIVA
    # ======================================================

    hoja = libro.active

    # ======================================================
    # LEER ENCABEZADOS
    # ======================================================

    encabezados_excel = []

    for celda in hoja[1]:

        if celda.value is None:

            encabezados_excel.append("")

        else:

            encabezados_excel.append(
                str(celda.value).strip()
            )

    # ======================================================
    # MAPA DE COLUMNAS
    # ======================================================

    mapa_encabezados = {

        "apellido":
            "Apellido",

        "nombre":
            "Nombres",

        "dni":
            "DNI",

        "cuil":
            "CUIL",

        "telefono":
            "Teléfono/Celular",

        "email":
            "Email",

        "direccion":
            "Dirección",

        "fecha_nacimiento":
            "Fecha de acimiento",
    }

    # ======================================================
    # BUSCAR POSICIONES
    # ======================================================

    posiciones = {}

    for nombre_interno, encabezado_excel in (
        mapa_encabezados.items()
    ):

        if encabezado_excel not in encabezados_excel:

            resultado["errores"].append(
                f"No se encontró la columna "
                f"'{encabezado_excel}'."
            )

        else:

            posiciones[nombre_interno] = (
                encabezados_excel.index(
                    encabezado_excel
                )
            )

    # ======================================================
    # DETENER SI FALTAN COLUMNAS
    # ======================================================

    if resultado["errores"]:

        return resultado

    # ======================================================
    # LEER FILAS
    # ======================================================

    for numero_fila, fila in enumerate(
        hoja.iter_rows(
            min_row=2,
            values_only=True
        ),
        start=2
    ):

        datos = {
            "_fila_excel": numero_fila
        }

        for nombre_interno, posicion in (
            posiciones.items()
        ):

            if posicion >= len(fila):

                valor = ""

            else:

                valor = fila[posicion]

            valor = convertir_valor_excel(
                valor
            )

            datos[nombre_interno] = valor

        resultado["filas"].append(
            datos
        )

    return resultado


# ==========================================================
# PROCESAR EXCEL DE DOCENTES
# ==========================================================

def procesar_excel_docentes(ruta_archivo):
    """
    Realiza el circuito completo:

        Excel
          ↓
        lectura
          ↓
        procesamiento
          ↓
        validación
          ↓
        comparación con BD

    No modifica la base de datos.
    """

    lectura = leer_excel_docentes(
        ruta_archivo
    )

    if lectura["errores"]:

        return {
            "errores_archivo": lectura["errores"],
            "resultados": []
        }

    resultados = procesar_docentes(
        lectura["filas"]
    )

    return {
        "errores_archivo": [],
        "resultados": resultados
    }


# ==========================================================
# GENERAR RESUMEN DE IMPORTACIÓN
# ==========================================================

def generar_resumen_importacion(resultados):
    """
    Genera un resumen de los resultados.

    No modifica la base de datos.
    """

    resumen = {
        "total": 0,
        "nuevos": 0,
        "actualizar": 0,
        "sin_cambios": 0,
        "errores": 0,
        "detalle_errores": [],
        "detalle_actualizaciones": [],
    }

    for resultado in resultados:

        resumen["total"] += 1

        estado = resultado["estado"]

        if estado == "NUEVO":

            resumen["nuevos"] += 1

        elif estado == "ACTUALIZAR":

            resumen["actualizar"] += 1

            resumen[
                "detalle_actualizaciones"
            ].append(
                {
                    "fila": resultado["fila"],
                    "datos": resultado["datos"],
                    "cambios": resultado["cambios"],
                }
            )

        elif estado == "SIN_CAMBIOS":

            resumen["sin_cambios"] += 1

        elif estado == "ERROR":

            resumen["errores"] += 1

            resumen[
                "detalle_errores"
            ].append(
                {
                    "fila": resultado["fila"],
                    "datos": resultado["datos"],
                    "errores": resultado["errores"],
                }
            )

    return resumen
# -------------------------------------------------------------------------------------------

# ==========================================================
# GUARDAR IMPORTACIÓN DE DOCENTES
# ==========================================================

def guardar_importacion_docentes(resultados):
    """
    Guarda en la base de datos los resultados de una
    importación previamente procesada.

    Estados que se guardan:

        NUEVO       -> INSERT
        ACTUALIZAR  -> UPDATE

    Estados que NO se guardan:

        SIN_CAMBIOS
        ERROR

    La operación se realiza dentro de una única
    transacción SQLite.

    Si ocurre un error durante el guardado:

        ROLLBACK

    y no se confirma ningún cambio.

    Retorna:

        {
            "exito": True / False,
            "insertados": cantidad,
            "actualizados": cantidad,
            "omitidos": cantidad,
            "errores": [...]
        }

    IMPORTANTE:
        Esta función modifica la base de datos.
    """

    resultado_guardado = {
        "exito": False,
        "insertados": 0,
        "actualizados": 0,
        "omitidos": 0,
        "errores": []
    }

    conn = conectar()
    cursor = conn.cursor()

    try:

        # ==================================================
        # COMENZAR TRANSACCIÓN
        # ==================================================

        conn.execute("BEGIN")

        # ==================================================
        # CONTROL DE DNI NUEVOS DENTRO DEL MISMO ARCHIVO
        # ==================================================

        dnis_nuevos = set()

        # ==================================================
        # PROCESAR RESULTADOS
        # ==================================================

        for resultado in resultados:

            estado = resultado["estado"]

            datos = resultado["datos"]

            # ==================================================
            # ERROR
            # ==================================================

            if estado == "ERROR":

                resultado_guardado["omitidos"] += 1

                continue

            # ==================================================
            # SIN CAMBIOS
            # ==================================================

            if estado == "SIN_CAMBIOS":

                resultado_guardado["omitidos"] += 1

                continue

            # ==================================================
            # NUEVO
            # ==================================================

            if estado == "NUEVO":

                dni = datos["dni"]

                # ------------------------------------------
                # Evitar DNI duplicado dentro del Excel
                # ------------------------------------------

                if dni in dnis_nuevos:

                    raise ValueError(
                        "El DNI "
                        f"{dni} aparece más de una vez "
                        "como docente nuevo en la "
                        "misma importación."
                    )

                dnis_nuevos.add(dni)

                # ------------------------------------------
                # INSERT
                # ------------------------------------------

                cursor.execute("""
                    INSERT INTO profesores (
                        apellido,
                        nombre,
                        dni,
                        cuil,
                        telefono,
                        email,
                        direccion,
                        fecha_nacimiento
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    datos["apellido"],
                    datos["nombre"],
                    datos["dni"],
                    datos["cuil"],
                    datos["telefono"],
                    datos["email"],
                    datos["direccion"],
                    datos["fecha_nacimiento"],
                ))

                resultado_guardado["insertados"] += 1

            # ==================================================
            # ACTUALIZAR
            # ==================================================

            elif estado == "ACTUALIZAR":

                id_docente = datos.get(
                    "id_docente"
                )

                if not id_docente:

                    raise ValueError(
                        "No se encontró el "
                        "id_docente para actualizar "
                        f"la fila {resultado['fila']}."
                    )

                cursor.execute("""
                    UPDATE profesores
                    SET
                        apellido = ?,
                        nombre = ?,
                        cuil = ?,
                        telefono = ?,
                        email = ?,
                        direccion = ?,
                        fecha_nacimiento = ?
                    WHERE id_docente = ?
                """, (
                    datos["apellido"],
                    datos["nombre"],
                    datos["cuil"],
                    datos["telefono"],
                    datos["email"],
                    datos["direccion"],
                    datos["fecha_nacimiento"],
                    id_docente,
                ))

                # ------------------------------------------
                # Verificar que realmente exista
                # ------------------------------------------

                if cursor.rowcount == 0:

                    raise ValueError(
                        "No se pudo actualizar "
                        f"el docente con ID "
                        f"{id_docente}."
                    )

                resultado_guardado["actualizados"] += 1

            # ==================================================
            # ESTADO DESCONOCIDO
            # ==================================================

            else:

                raise ValueError(
                    "Estado de importación desconocido: "
                    f"{estado}"
                )

        # ==================================================
        # CONFIRMAR TRANSACCIÓN
        # ==================================================

        conn.commit()

        resultado_guardado["exito"] = True

    except Exception as e:

        # ==================================================
        # DESHACER TODO
        # ==================================================

        conn.rollback()

        resultado_guardado["errores"].append(
            str(e)
        )

        resultado_guardado["exito"] = False

        # Si hubo rollback, ninguna operación quedó
        # definitivamente guardada.
        resultado_guardado["insertados"] = 0
        resultado_guardado["actualizados"] = 0

    finally:

        conn.close()

    return resultado_guardado
# -----------------------------------------------------------------------------------------------