from importador import (
    procesar_excel_docentes,
    generar_resumen_importacion,
    guardar_importacion_docentes
)


# ==========================================================
# PROCESAR EXCEL
# ==========================================================

resultado_importacion = procesar_excel_docentes(
    "DatosDocentes.xlsx"
)


# ==========================================================
# MOSTRAR RESULTADOS
# ==========================================================

print("\n==========================================")
print("RESULTADO DE IMPORTACIÓN")
print("==========================================")

print(
    "\nErrores del archivo:"
)

print(
    resultado_importacion[
        "errores_archivo"
    ]
)

print(
    "\nCantidad de resultados:"
)

print(
    len(
        resultado_importacion[
            "resultados"
        ]
    )
)


# ==========================================================
# MOSTRAR CADA FILA
# ==========================================================

for resultado in (
    resultado_importacion[
        "resultados"
    ]
):

    print(
        "\n------------------------------------------"
    )

    print(
        "Fila Excel:",
        resultado["fila"]
    )

    print(
        "Estado:",
        resultado["estado"]
    )

    print(
        "Datos:",
        resultado["datos"]
    )

    print(
        "Errores:",
        resultado["errores"]
    )

    print(
        "Advertencias:",
        resultado["advertencias"]
    )

    print(
        "Cambios:",
        resultado["cambios"]
    )


# ==========================================================
# GENERAR RESUMEN
# ==========================================================

resumen = generar_resumen_importacion(
    resultado_importacion[
        "resultados"
    ]
)


print("\n")
print("==========================================")
print("RESUMEN DE IMPORTACIÓN")
print("==========================================")

print(
    "Total:",
    resumen["total"]
)

print(
    "Nuevos:",
    resumen["nuevos"]
)

print(
    "Actualizar:",
    resumen["actualizar"]
)

print(
    "Sin cambios:",
    resumen["sin_cambios"]
)

print(
    "Errores:",
    resumen["errores"]
)


# ==========================================================
# GUARDAR EN LA BASE
# ==========================================================

print("\n")
print("==========================================")
print("GUARDANDO EN LA BASE DE DATOS")
print("==========================================")


resultado_guardado = guardar_importacion_docentes(
    resultado_importacion[
        "resultados"
    ]
)


# ==========================================================
# MOSTRAR RESULTADO DEL GUARDADO
# ==========================================================

print(
    "\nÉxito:",
    resultado_guardado["exito"]
)

print(
    "Insertados:",
    resultado_guardado["insertados"]
)

print(
    "Actualizados:",
    resultado_guardado["actualizados"]
)

print(
    "Omitidos:",
    resultado_guardado["omitidos"]
)

print(
    "Errores:",
    resultado_guardado["errores"]
)


