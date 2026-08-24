# ==========================================================================================
#             RANKING DE INASISTENCIAS DE DOCENTES - MÓDULO rankinginasistencias.py
# ==========================================================================================

# ------------------------------------------ LIBRERÍAS -------------------------------------
import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------- Librerías para generación de PDF ----------------------------
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ---------------------------- Fin Librerías ------------------------------------------------


# ==========================================================================================
#                         FUNCIONES AUXILIARES
# ==========================================================================================

def convertir_fecha(fecha):
    """
    Convierte una fecha almacenada en la BD a objeto datetime.

    Admite:
        DD/MM/AAAA
        AAAA-MM-DD
        DD-MM-AAAA
    """

    if not fecha:
        return None

    fecha = str(fecha).strip()

    formatos = (
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y"
    )

    for formato in formatos:
        try:
            return datetime.strptime(fecha, formato).date()
        except ValueError:
            continue

    return None


def dias_habiles(fecha_desde, fecha_hasta):
    """
    Calcula la cantidad de días hábiles entre dos fechas,
    incluyendo ambas fechas.

    Se consideran hábiles:
        Lunes a Viernes

    No se descuentan feriados porque el módulo actual
    no posee una tabla/calendario de feriados.
    """

    inicio = convertir_fecha(fecha_desde)
    fin = convertir_fecha(fecha_hasta)

    if inicio is None or fin is None:
        return 0

    if fin < inicio:
        return 0

    cantidad = 0
    fecha_actual = inicio

    while fecha_actual <= fin:

        # Monday = 0 ... Sunday = 6
        if fecha_actual.weekday() < 5:
            cantidad += 1

        fecha_actual += timedelta(days=1)

    return cantidad


# ==========================================================================================
#                     RANKING DE INASISTENCIAS DE DOCENTES
# ==========================================================================================

class RankingInasistenciasApp:

    def __init__(self, parent, db_path="bdescuela.db"):

        # ------------------------------------------------------------------
        # Ventana principal
        # ------------------------------------------------------------------

        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Ranking de Inasistencias")
        self.ventana.state("zoomed")

        self.db_path = db_path

        # Le da foco a la ventana emergente
        self.ventana.grab_set()

        # Asegura que la ventana quede por encima al abrirse
        self.ventana.focus_set()

        # ------------------------------------------------------------------
        # Contenedor principal
        # ------------------------------------------------------------------

        main_frame = ttk.Frame(
            self.ventana,
            padding=10
        )

        main_frame.pack(
            fill=tk.BOTH,
            expand=True
        )

        # ==================================================================
        # PANEL IZQUIERDO: TABLA DE RANKING
        # ==================================================================

        left_frame = ttk.LabelFrame(
            main_frame,
            text=" Ranking de Docentes ",
            padding=10
        )

        left_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )

        # ------------------------------------------------------------------
        # Treeview
        # ------------------------------------------------------------------

        cols = (
            "ID",
            "Docente",
            "Total Faltas",
            "Cat. Predominante"
        )

        self.tree = ttk.Treeview(
            left_frame,
            columns=cols,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading(
            "ID",
            text="ID"
        )

        self.tree.heading(
            "Docente",
            text="Docente"
        )

        self.tree.heading(
            "Total Faltas",
            text="Total Días"
        )

        self.tree.heading(
            "Cat. Predominante",
            text="Cat. Predominante"
        )

        self.tree.column(
            "ID",
            width=40,
            anchor="center"
        )

        self.tree.column(
            "Docente",
            width=180
        )

        self.tree.column(
            "Total Faltas",
            width=90,
            anchor="center"
        )

        self.tree.column(
            "Cat. Predominante",
            width=150
        )

        self.tree.pack(
            fill=tk.BOTH,
            expand=True
        )

        # Evento de selección
        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_docente_select
        )

        # ==================================================================
        # PANEL DERECHO: GRÁFICO DE TORTA
        # ==================================================================

        self.right_frame = ttk.LabelFrame(
            main_frame,
            text=" Distribución por Motivo ",
            padding=10
        )

        self.right_frame.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True
        )

        # ------------------------------------------------------------------
        # Matplotlib
        # ------------------------------------------------------------------

        self.fig, self.ax = plt.subplots(
            figsize=(5, 4)
        )

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.right_frame
        )

        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True
        )

        # ==================================================================
        # PANEL INFERIOR: BOTONES
        # ==================================================================

        btn_frame = ttk.Frame(
            self.ventana,
            padding=(10, 5, 10, 10)
        )

        btn_frame.pack(
            fill=tk.X,
            side=tk.BOTTOM
        )

        self.btn_exportar = ttk.Button(
            btn_frame,
            text="📄 Exportar Docente a PDF",
            command=self.exportar_pdf
        )

        self.btn_exportar.pack(
            side=tk.LEFT,
            padx=5
        )

        self.btn_cerrar = tk.Button(
            btn_frame,
            text="❌ Cerrar Ventana",
            command=self.cerrar_pantalla
        )

        self.btn_cerrar.pack(
            side=tk.RIGHT,
            padx=5
        )

        # Interceptar la X de la ventana
        self.ventana.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar_pantalla
        )

        # ==================================================================
        # VARIABLE PARA DOCENTE SELECCIONADO
        # ==================================================================

        self.docente_seleccionado = None

        # ==================================================================
        # CARGAR RANKING
        # ==================================================================

        self.cargar_ranking()

    # ======================================================================================
    #                              CERRAR VENTANA
    # ======================================================================================

    def cerrar_pantalla(self):

        # Limpieza de Matplotlib
        if hasattr(self, 'fig'):

            try:
                self.ax.clear()
                self.fig.clf()
                plt.close(self.fig)

            except Exception:
                pass

        self.ventana.destroy()

    # ======================================================================================
    #                         CARGAR RANKING
    # ======================================================================================

    def cargar_ranking(self):

        # ------------------------------------------------------------------
        # Limpiar Treeview
        # ------------------------------------------------------------------

        for item in self.tree.get_children():
            self.tree.delete(item)

        # ------------------------------------------------------------------
        # Conexión
        # ------------------------------------------------------------------

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        try:

            # ------------------------------------------------------------------
            # IMPORTANTE:
            #
            # Ya no utilizamos COUNT(*)
            #
            # Primero obtenemos todas las inasistencias y posteriormente
            # calculamos los días hábiles de cada período.
            # ------------------------------------------------------------------

            query = """
                SELECT
                    i.id_docente,
                    p.nombre || ' ' || p.apellido AS docente,
                    i.motivo,
                    i.fecha_desde,
                    i.fecha_hasta
                FROM inasistencia i
                INNER JOIN profesores p
                    ON p.id_docente = i.id_docente
                ORDER BY
                    p.apellido,
                    p.nombre,
                    i.fecha_desde
            """

            cursor.execute(query)

            registros = cursor.fetchall()

            # ------------------------------------------------------------------
            # Diccionario de acumulación
            #
            # estructura:
            #
            # datos[id_docente] = {
            #     "nombre": "...",
            #     "total": 0,
            #     "motivos": {
            #         "Licencia médica": 10,
            #         "ART": 5
            #     }
            # }
            # ------------------------------------------------------------------

            datos = {}

            for id_docente, docente, motivo, fecha_desde, fecha_hasta in registros:

                dias = dias_habiles(
                    fecha_desde,
                    fecha_hasta
                )

                if id_docente not in datos:

                    datos[id_docente] = {
                        "nombre": docente,
                        "total": 0,
                        "motivos": {}
                    }

                datos[id_docente]["total"] += dias

                if motivo not in datos[id_docente]["motivos"]:
                    datos[id_docente]["motivos"][motivo] = 0

                datos[id_docente]["motivos"][motivo] += dias

            # ------------------------------------------------------------------
            # Ordenar ranking de mayor a menor cantidad de días
            # ------------------------------------------------------------------

            ranking = sorted(
                datos.items(),
                key=lambda x: x[1]["total"],
                reverse=True
            )

            # ------------------------------------------------------------------
            # Cargar Treeview
            # ------------------------------------------------------------------

            for id_docente, info in ranking:

                motivos = info["motivos"]

                if motivos:

                    motivo_predominante = max(
                        motivos,
                        key=motivos.get
                    )

                else:

                    motivo_predominante = "---"

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        id_docente,
                        info["nombre"],
                        info["total"],
                        motivo_predominante
                    )
                )

        except sqlite3.Error as e:

            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo cargar el ranking:\n{e}",
                parent=self.ventana
            )

        finally:

            conn.close()

    # ======================================================================================
    #                    EVENTO AL SELECCIONAR UN DOCENTE
    # ======================================================================================

    def on_docente_select(self, event):

        selected = self.tree.selection()

        if not selected:
            return

        item = self.tree.item(
            selected[0]
        )

        id_docente = item["values"][0]
        nombre_docente = item["values"][1]

        self.docente_seleccionado = {
            "id": id_docente,
            "nombre": nombre_docente,
            "total": item["values"][2]
        }

        self.actualizar_grafico(
            id_docente,
            nombre_docente
        )

    # ======================================================================================
    #                         ACTUALIZAR GRÁFICO
    # ======================================================================================

    def actualizar_grafico(
        self,
        id_docente,
        nombre_docente
    ):

        conn = sqlite3.connect(
            self.db_path
        )

        cursor = conn.cursor()

        try:

            # ------------------------------------------------------------------
            # Traemos los períodos de inasistencia.
            #
            # El gráfico también utilizará días hábiles y no registros.
            # ------------------------------------------------------------------

            query = """
                SELECT
                    motivo,
                    fecha_desde,
                    fecha_hasta
                FROM inasistencia
                WHERE id_docente = ?
            """

            cursor.execute(
                query,
                (id_docente,)
            )

            registros = cursor.fetchall()

        finally:

            conn.close()

        # ------------------------------------------------------------------
        # Acumulamos días por motivo
        # ------------------------------------------------------------------

        motivos_dias = {}

        for motivo, fecha_desde, fecha_hasta in registros:

            dias = dias_habiles(
                fecha_desde,
                fecha_hasta
            )

            if motivo not in motivos_dias:
                motivos_dias[motivo] = 0

            motivos_dias[motivo] += dias

        # ------------------------------------------------------------------
        # Limpiar gráfico anterior
        # ------------------------------------------------------------------

        self.ax.clear()

        if motivos_dias:

            motivos = list(
                motivos_dias.keys()
            )

            cantidades = list(
                motivos_dias.values()
            )

            self.ax.pie(
                cantidades,
                labels=motivos,
                autopct='%1.1f%%',
                startangle=140
            )

            self.ax.set_title(
                f"Motivos de faltas:\n{nombre_docente}"
            )

        else:

            self.ax.text(
                0.5,
                0.5,
                "Sin datos",
                ha='center',
                va='center'
            )

        self.fig.tight_layout()

        self.canvas.draw()

    # ======================================================================================
    #                              EXPORTAR PDF
    # ======================================================================================

    def exportar_pdf(self):

        selected = self.tree.selection()

        if not selected:

            messagebox.showwarning(
                "Atención",
                "Por favor, seleccione un docente de la lista para exportar.",
                parent=self.ventana
            )

            return

        # ------------------------------------------------------------------
        # Obtener datos del docente seleccionado
        # ------------------------------------------------------------------

        item = self.tree.item(
            selected[0]
        )

        valores = item["values"]

        id_docente = valores[0]
        nombre_docente = valores[1]
        total_faltas = valores[2]
        cat_predominante = valores[3]

        # ------------------------------------------------------------------
        # Ruta de salida
        # ------------------------------------------------------------------

        carpeta_destino = os.path.join(
            "reportes",
            "pdf",
            "Faltas_Docentes"
        )

        os.makedirs(
            carpeta_destino,
            exist_ok=True
        )

        nombre_limpio = str(
            nombre_docente
        ).replace(
            " ",
            "_"
        )

        pdf_path = os.path.join(
            carpeta_destino,
            f"Reporte_{nombre_limpio}.pdf"
        )

        # ------------------------------------------------------------------
        # Guardar gráfico temporal
        # ------------------------------------------------------------------

        img_temp = "temp_grafico_inasistencia.png"

        self.fig.savefig(
            img_temp,
            dpi=200,
            bbox_inches='tight'
        )

        try:

            # ------------------------------------------------------------------
            # Documento PDF
            # ------------------------------------------------------------------

            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=40,
                leftMargin=40,
                topMargin=40,
                bottomMargin=40
            )

            styles = getSampleStyleSheet()

            elements = []

            # ------------------------------------------------------------------
            # Título
            # ------------------------------------------------------------------

            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=18,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=15
            )

            elements.append(
                Paragraph(
                    "Informe de Inasistencias Docente",
                    title_style
                )
            )

            elements.append(
                Spacer(1, 10)
            )

            # ------------------------------------------------------------------
            # Datos del docente
            # ------------------------------------------------------------------

            datos_docente = [
                [
                    "Docente:",
                    str(nombre_docente)
                ],
                [
                    "ID / Legajo:",
                    str(id_docente)
                ],
                [
                    "Total Días Faltados:",
                    str(total_faltas)
                ],
                [
                    "Categoría Predominante:",
                    str(cat_predominante)
                ]
            ]

            tabla = Table(
                datos_docente,
                colWidths=[180, 320]
            )

            tabla.setStyle(
                TableStyle([
                    (
                        'BACKGROUND',
                        (0, 0),
                        (-1, -1),
                        colors.HexColor('#f8fafc')
                    ),
                    (
                        'TEXTCOLOR',
                        (0, 0),
                        (0, -1),
                        colors.HexColor('#2d3748')
                    ),
                    (
                        'FONTNAME',
                        (0, 0),
                        (0, -1),
                        'Helvetica-Bold'
                    ),
                    (
                        'FONTNAME',
                        (1, 0),
                        (1, -1),
                        'Helvetica'
                    ),
                    (
                        'FONTSIZE',
                        (0, 0),
                        (-1, -1),
                        11
                    ),
                    (
                        'BOTTOMPADDING',
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        'TOPPADDING',
                        (0, 0),
                        (-1, -1),
                        8
                    ),
                    (
                        'GRID',
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor('#cbd5e1')
                    ),
                ])
            )

            elements.append(
                tabla
            )

            elements.append(
                Spacer(1, 20)
            )

            # ------------------------------------------------------------------
            # Subtítulo gráfico
            # ------------------------------------------------------------------

            sub_style = ParagraphStyle(
                'SubTitle',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=13,
                textColor=colors.HexColor('#2b6cb0'),
                spaceAfter=10
            )

            elements.append(
                Paragraph(
                    "Distribución Porcentual por Motivo de Inasistencia",
                    sub_style
                )
            )

            elements.append(
                Image(
                    img_temp,
                    width=380,
                    height=280
                )
            )

            # ------------------------------------------------------------------
            # Generar PDF
            # ------------------------------------------------------------------

            doc.build(
                elements
            )

            # ------------------------------------------------------------------
            # Eliminar imagen temporal
            # ------------------------------------------------------------------

            if os.path.exists(
                img_temp
            ):
                os.remove(
                    img_temp
                )

            messagebox.showinfo(
                "Éxito",
                f"El informe PDF se guardó correctamente en:\n{pdf_path}",
                parent=self.ventana
            )

        except Exception as e:

            if os.path.exists(
                img_temp
            ):
                os.remove(
                    img_temp
                )

            messagebox.showerror(
                "Error",
                f"Ocurrió un error al generar el PDF:\n{e}",
                parent=self.ventana
            )

    # ======================================================================================