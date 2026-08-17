# ==========================================================
# PRUEBA COMPLETA DEL IMPORTADOR DE ASIGNACIONES
# ==========================================================

from importador_asignaciones import (
    obtener_archivos_excel,
    analizar_archivo,
    importar_registros
)

from database import conectar


# ==========================================================
# ENCABEZADO
# ==========================================================

print("=" * 70)
print(" PRUEBA COMPLETA DEL IMPORTADOR DE ASIGNACIONES")
print("=" * 70)


# ==========================================================
# 1. BUSCAR ARCHIVOS EXCEL
# ==========================================================

archivos = obtener_archivos_excel()

print("\nARCHIVOS ENCONTRADOS")
print("-" * 70)

if not archivos:

    print("No se encontraron archivos Excel.")

    raise SystemExit

for numero, archivo in enumerate(
    archivos,
    start=1
):

    print(
        f"{numero}. {archivo}"
    )


# ==========================================================
# 2. TOMAR EL PRIMER ARCHIVO
# ==========================================================

archivo = archivos[0]

print("\n" + "=" * 70)
print("ANALIZANDO ARCHIVO")
print("=" * 70)

print(archivo)


# ==========================================================
# 3. ANALIZAR
# ==========================================================

resultado = analizar_archivo(
    archivo
)


# ==========================================================
# 4. RESULTADO GENERAL
# ==========================================================

print("\nRESULTADO DEL ANÁLISIS")
print("-" * 70)

print(
    "Columnas correctas :",
    resultado["columnas_ok"]
)

print(
    "Total registros    :",
    resultado["total"]
)

print(
    "Correctos          :",
    resultado["correctos"]
)

print(
    "Errores            :",
    resultado["errores"]
)

print(
    "Advertencias       :",
    resultado["advertencias"]
)


# ==========================================================
# 5. ERRORES
# ==========================================================

if resultado["detalle_errores"]:

    print("\nERRORES")
    print("-" * 70)

    for error in resultado[
        "detalle_errores"
    ]:

        print(
            f"Fila {error['fila']}:"
        )

        for mensaje in error[
            "errores"
        ]:

            print(
                f"   - {mensaje}"
            )


# ==========================================================
# 6. ADVERTENCIAS
# ==========================================================

if resultado["detalle_advertencias"]:

    print("\nADVERTENCIAS")
    print("-" * 70)

    for advertencia in resultado[
        "detalle_advertencias"
    ]:

        print(
            f"Fila {advertencia['fila']}:"
        )

        for mensaje in advertencia[
            "advertencias"
        ]:

            print(
                f"   - {mensaje}"
            )


# ==========================================================
# 7. REGISTROS PREPARADOS
# ==========================================================

print("\nREGISTROS ANALIZADOS")
print("-" * 70)

for registro in resultado[
    "registros"
]:

    print(
        f"\nFila Excel: "
        f"{registro['fila_excel']}"
    )

    print(
        f"  DNI:                  "
        f"{registro['dni']}"
    )

    print(
        f"  ID Docente:           "
        f"{registro['id_docente']}"
    )

    print(
        f"  Materia:              "
        f"{registro['materia']}"
    )

    print(
        f"  ID Materia:           "
        f"{registro['id_materia']}"
    )

    print(
        f"  Día:                  "
        f"{registro['dia']}"
    )

    print(
        f"  Cargo:                "
        f"{registro['cargo']}"
    )

    print(
        f"  Módulos:              "
        f"{registro['modulos']}"
    )

    print(
        f"  Curso:                "
        f"{registro['curso']}"
    )

    print(
        f"  Turno:                "
        f"{registro['turno']}"
    )

    print(
        f"  Entrada:              "
        f"{registro['hentrada']}"
    )

    print(
        f"  Salida:               "
        f"{registro['hsalida']}"
    )

    print(
        f"  Situación de Revista: "
        f"{registro['situacion_revista']}"
    )

    print(
        f"  Toma de Posesión:     "
        f"{registro['toma_pos']}"
    )

    print(
        f"  Cese:                 "
        f"{registro['fecha_cese']}"
    )

    print(
        f"  Activo:               "
        f"{registro['activo']}"
    )

    print(
        f"  Estado:               "
        f"{registro['estado']}"
    )


# ==========================================================
# 8. CONTAR ASIGNACIONES ANTES DE IMPORTAR
# ==========================================================

conn = conectar()

cursor = conn.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM asignacion"
)

total_antes = cursor.fetchone()[0]

conn.close()

print("\n" + "=" * 70)
print("ESTADO DE LA BASE ANTES DE IMPORTAR")
print("=" * 70)

print(
    "Asignaciones existentes:",
    total_antes
)


# ==========================================================
# 9. DECIDIR SI SE PUEDE IMPORTAR
# ==========================================================

if resultado["errores"] > 0:

    print("\n" + "=" * 70)
    print("IMPORTACIÓN CANCELADA")
    print("=" * 70)

    print(
        "\nNo se importará ningún registro "
        "porque existen errores."
    )

    print(
        f"Errores encontrados: "
        f"{resultado['errores']}"
    )

else:

    print("\n" + "=" * 70)
    print("IMPORTANDO REGISTROS")
    print("=" * 70)

    ok, mensaje = importar_registros(
        resultado
    )

    print("\nResultado:")
    print(mensaje)

    # ======================================================
    # 10. CONTAR DESPUÉS DE IMPORTAR
    # ======================================================

    if ok:

        conn = conectar()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM asignacion"
        )

        total_despues = cursor.fetchone()[0]

        conn.close()

        print("\n" + "=" * 70)
        print("ESTADO DE LA BASE DESPUÉS DE IMPORTAR")
        print("=" * 70)

        print(
            "Asignaciones antes :",
            total_antes
        )

        print(
            "Asignaciones después:",
            total_despues
        )

        diferencia = (
            total_despues -
            total_antes
        )

        print(
            "Nuevas asignaciones:",
            diferencia
        )


# ==========================================================
# FIN
# ==========================================================

print("\n" + "=" * 70)
print(" FIN DE LA PRUEBA")
print("=" * 70)
