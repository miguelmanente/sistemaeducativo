"""
=========================================================
Sistema de Gestión Educativa (SGE)

Archivo: exportarPDF.py

Descripción:
Generación de fichas de docentes en formato PDF.

Los archivos se guardan automáticamente en:

    reportes/
        pdf/
            ficha_docente/

Autor: Miguel Ángel Manente
=========================================================
"""

# ==========================================================
# IMPORTACIONES
# ==========================================================

import os
import tkinter as tk
from tkinter import messagebox

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)


# ==========================================================
# EXPORTAR FICHA DEL DOCENTE
# ==========================================================

def exportar_ficha_docente(
    apellido,
    nombre,
    dni,
    cuil,
    telefono,
    email,
    direccion,
    fecha_nacimiento,
    parent=None
):
    """
    Exporta los datos personales de un docente a un archivo PDF.

    Los archivos se guardan automáticamente en:

        reportes/pdf/ficha_docente/

    Parámetros:
        apellido
        nombre
        dni
        cuil
        telefono
        email
        direccion
        fecha_nacimiento
        parent -> ventana padre de Tkinter

    Retorna:
        True  -> PDF generado correctamente.
        False -> Si ocurrió un error.
    """

    # ======================================================
    # DATOS
    # ======================================================

    apellido = str(apellido or "").strip()
    nombre = str(nombre or "").strip()
    dni = str(dni or "").strip()
    cuil = str(cuil or "").strip()
    telefono = str(telefono or "").strip()
    email = str(email or "").strip()
    direccion = str(direccion or "").strip()
    fecha_nacimiento = str(fecha_nacimiento or "").strip()

    nombre_completo = f"{apellido}, {nombre}".strip(", ")

    if not nombre_completo:
        nombre_completo = "Docente"

    # ======================================================
    # DETERMINAR CARPETA DEL PROYECTO
    # ======================================================

    carpeta_modulo = os.path.dirname(os.path.abspath(__file__))

    carpeta_reportes = os.path.join(
        carpeta_modulo,
        "reportes"
    )

    carpeta_pdf = os.path.join(
        carpeta_reportes,
        "pdf"
    )

    carpeta_ficha_docente = os.path.join(
        carpeta_pdf,
        "ficha_docente"
    )

    # Crear las carpetas si todavía no existen
    os.makedirs(
        carpeta_ficha_docente,
        exist_ok=True
    )

    # ======================================================
    # NOMBRE DEL ARCHIVO
    # ======================================================

    nombre_archivo = nombre_completo

    # Caracteres no permitidos en nombres de archivo
    caracteres_invalidos = '<>:"/\\|?*'

    for caracter in caracteres_invalidos:
        nombre_archivo = nombre_archivo.replace(
            caracter,
            "_"
        )

    nombre_archivo = f"Ficha_{nombre_archivo}.pdf"

    ruta_pdf = os.path.join(
        carpeta_ficha_docente,
        nombre_archivo
    )

    # ======================================================
    # CONFIGURACIÓN DEL DOCUMENTO
    # ======================================================

    try:

        documento = SimpleDocTemplate(
            ruta_pdf,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm
        )

        estilos = getSampleStyleSheet()

        estilo_titulo = ParagraphStyle(
            "TituloFicha",
            parent=estilos["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            textColor=colors.white
        )

        estilo_subtitulo = ParagraphStyle(
            "SubtituloFicha",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#555555")
        )

        estilo_etiqueta = ParagraphStyle(
            "Etiqueta",
            parent=estilos["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#555555")
        )

        estilo_valor = ParagraphStyle(
            "Valor",
            parent=estilos["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#1a1a1a")
        )

        elementos = []

        # ==================================================
        # ENCABEZADO
        # ==================================================

        encabezado = Table(
            [
                [
                    Paragraph(
                        "SISTEMA DE GESTIÓN EDUCATIVA",
                        estilo_titulo
                    )
                ],
                [
                    Paragraph(
                        "FICHA DE DATOS PERSONALES DEL DOCENTE",
                        ParagraphStyle(
                            "SubtituloHeader",
                            parent=estilo_titulo,
                            fontSize=11,
                            leading=14
                        )
                    )
                ]
            ],
            colWidths=[170 * mm]
        )

        encabezado.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#2c3e50")
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    )
                ]
            )
        )

        elementos.append(encabezado)

        elementos.append(
            Spacer(1, 8 * mm)
        )

        # ==================================================
        # NOMBRE DEL DOCENTE
        # ==================================================

        nombre_tabla = Table(
            [
                [
                    Paragraph(
                        nombre_completo,
                        ParagraphStyle(
                            "NombreDocente",
                            parent=estilos["Heading2"],
                            fontName="Helvetica-Bold",
                            fontSize=16,
                            leading=20,
                            alignment=TA_CENTER,
                            textColor=colors.HexColor("#2c3e50")
                        )
                    )
                ]
            ],
            colWidths=[170 * mm]
        )

        nombre_tabla.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        colors.HexColor("#f4f4f4")
                    ),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        colors.HexColor("#d0d0d0")
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    )
                ]
            )
        )

        elementos.append(nombre_tabla)

        elementos.append(
            Spacer(1, 8 * mm)
        )

        # ==================================================
        # DATOS PERSONALES
        # ==================================================

        def valor_mostrar(valor):
            return valor if valor else "-"

        datos = [
            [
                Paragraph("DNI:", estilo_etiqueta),
                Paragraph(valor_mostrar(dni), estilo_valor),
                Paragraph("CUIL:", estilo_etiqueta),
                Paragraph(valor_mostrar(cuil), estilo_valor)
            ],
            [
                Paragraph("Teléfono:", estilo_etiqueta),
                Paragraph(valor_mostrar(telefono), estilo_valor),
                Paragraph("Email:", estilo_etiqueta),
                Paragraph(valor_mostrar(email), estilo_valor)
            ],
            [
                Paragraph("Dirección:", estilo_etiqueta),
                Paragraph(valor_mostrar(direccion), estilo_valor),
                Paragraph("Fecha Nac.:", estilo_etiqueta),
                Paragraph(
                    valor_mostrar(fecha_nacimiento),
                    estilo_valor
                )
            ]
        ]

        tabla_datos = Table(
            datos,
            colWidths=[
                28 * mm,
                57 * mm,
                28 * mm,
                57 * mm
            ],
            hAlign="LEFT"
        )

        tabla_datos.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#d0d0d0")
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, -1),
                        colors.HexColor("#f4f4f4")
                    ),
                    (
                        "BACKGROUND",
                        (2, 0),
                        (2, -1),
                        colors.HexColor("#f4f4f4")
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ]
            )
        )

        elementos.append(tabla_datos)

        elementos.append(
            Spacer(1, 12 * mm)
        )

        # ==================================================
        # PIE DE FICHA
        # ==================================================

        elementos.append(
            HRFlowable(
                width="100%",
                thickness=0.7,
                color=colors.HexColor("#cccccc"),
                spaceBefore=5,
                spaceAfter=8
            )
        )

        elementos.append(
            Paragraph(
                "Documento generado por el Sistema de Gestión Educativa (SGE)",
                estilo_subtitulo
            )
        )

        # ==================================================
        # GENERAR PDF
        # ==================================================

        documento.build(elementos)

        messagebox.showinfo(
            "PDF generado",
            "La ficha del docente fue exportada correctamente.\n\n"
            f"Guardada en:\n"
            f"{ruta_pdf}",
            parent=parent
        )

        return True

    except Exception as e:

        messagebox.showerror(
            "Error al generar PDF",
            "No se pudo generar el archivo PDF.\n\n"
            f"Detalle:\n{e}",
            parent=parent
        )

        return False