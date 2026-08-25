# ==========================================================================================
#             LISTADOS SIT_REVISTAS DOCENTES - MÓDULO listadoSR.py
# ==========================================================================================

# ----------------------------------- LIBRERÍAS ------------------------------------------
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Fuerza a Matplotlib a usar el backend de Tkinter existente
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import legal
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from centraVent import centrar_ventana
# ----------------------------------------------------------------------------------------

# ------------------------- CLASE QUE MANEJA LA CREACIÓN DE LOS LISTADOS -----------------
class ModuloListados:
    def __init__(self, parent, db_path="bdescuela.db"):
        # Si parent es un Toplevel o Tk, usamos parent directamente
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Exportación de Listados de Docentes")
        self.ventana.geometry("500x400")
        self.ventana.resizable(False, False)
        self.db_path = db_path

        # Le da foco a la ventana emergente
        self.ventana.grab_set()

        # Asegura que la ventana quede por encima al abrirse
        self.ventana.focus_set()
        # self.db_path = db_path

        # Ruta destino requerida
        self.output_dir = os.path.join("reportes", "pdf", "Listado_sit_rev")

        # Variable para controlar la selección
        self.situacion_var = tk.StringVar(value="Titular")
        
        self._crear_interfaz()
    # --------------------------------------------------------------------------------------
    
    # --------------------------- Configuración del listado --------------------------------
    def _crear_interfaz(self):
        frame = ttk.LabelFrame(
            self.ventana, text=" Configuración del Reporte ", padding=15
        )
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        ttk.Label(
            frame,
            text="Seleccione la situación de revista:",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        # Opciones de selección
        opciones = [
            ("Titulares", "Titular"),
            ("Provisorios", "Provisorio"),
            ("Suplentes", "Suplente"),
        ]

        for texto, valor in opciones:
            ttk.Radiobutton(
                frame,
                text=texto,
                value=valor,
                variable=self.situacion_var,
            ).pack(anchor="w", pady=2)

        # Botón para generar PDF
        btn_exportar = ttk.Button(
            frame, text="Exportar a PDF", command=self.generar_pdf
        )
        btn_exportar.pack(pady=15, fill="x")

        self.btn_cerrar = ttk.Button(
            frame, 
            text="❌ Cerrar Ventana", 
            command=self.cerrar_pantalla
        )
        self.btn_cerrar.pack(pady=15, fill="x")
        #centrar_ventana(self.ventana)
        # También intercepta el clic en la "X" de la ventana arriba a la derecha
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_pantalla)
    # -------------------------------------------------------------------------------

    # ------------------ CERRAR VENTANA Y SUS PROCESOS ------------------------------
    def cerrar_pantalla(self):
        # 1. Limpia los recursos de Matplotlib si la figura existe
        if hasattr(self, 'fig'):
            try:
                self.ax.clear()
                self.fig.clf()
                plt.close(self.fig)
            except Exception:
                pass

        # 2. Destruye la ventana Toplevel actual liberando la memoria
        self.ventana.destroy()
    # -------------------------------------------------------------------------------

    # ----------------------------- Buscar datos en la BD  ---------------------------
    def _obtener_datos(self, situacion):
        """Consulta la base de datos según la situación de revista seleccionada."""
        query = """
            SELECT DISTINCT 
                p.apellido, 
                p.nombre, 
                p.dni, 
                p.cuil, 
                a.situacion_revista
            FROM profesores p
            INNER JOIN asignacion a ON p.id_docente = a.id_docente
            WHERE a.situacion_revista = ?
            ORDER BY p.apellido, p.nombre
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, (situacion,))
            filas = cursor.fetchall()
            conn.close()
            return filas
        except sqlite3.Error as e:
            messagebox.showerror(
                "Error de Base de Datos", f"No se pudo consultar la BD:\n{e}", parent=self.ventana
            )
            return []
    # ------------------------------------------------------------------------------------------


    # ---------------------- Exportar planilla PDF listado situación Revista -------------------
    def generar_pdf(self):
        situacion = self.situacion_var.get()
        registros = self._obtener_datos(situacion)

        if not registros:
            messagebox.showwarning(
                "Sin datos",
                f"No se encontraron docentes con situación: {situacion}", parent=self.ventana
            )
            return

        # Crear el directorio si aún no existe
        os.makedirs(self.output_dir, exist_ok=True)

        nombre_archivo = f"Listado_{situacion}.pdf"
        ruta_completa = os.path.join(self.output_dir, nombre_archivo)

        doc = SimpleDocTemplate(
            ruta_completa,
            pagesize=legal,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30,
        )

        elements = []
        styles = getSampleStyleSheet()

        # Encabezado para completar a mano
        estilo_encabezado = ParagraphStyle(
            "EncabezadoHandwritten",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
        )

        texto_encabezado = f"""
        <b>TÍTULO:</b> ____________________________________________________________________<br/><br/>
        <b>FECHA:</b> _____ / _____ / _________ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>DÍA:</b> ______________________
        """
        elements.append(Paragraph(texto_encabezado, estilo_encabezado))
        elements.append(Spacer(1, 15))

        # Título del reporte
        estilo_titulo = ParagraphStyle(
            "TituloReporte",
            parent=styles["Heading2"],
            alignment=1,  # Centrado
            spaceAfter=15,
        )
        elements.append(
            Paragraph(
                f"LISTADO DE DOCENTES: {situacion.upper()}", estilo_titulo
            )
        )

        # Tabla con columna para firma
        headers = [
            "Apellido",
            "Nombre",
            "DNI",
            "CUIL",
            "Sit. Revista",
            "Firma / Observaciones",
        ]
        tabla_datos = [headers]

        for reg in registros:
            tabla_datos.append(
                [reg[0], reg[1], str(reg[2]), str(reg[3]), reg[4], ""]
            )

        col_widths = [90, 90, 65, 80, 70, 140]

        t = Table(tabla_datos, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("TOPPADDING", (0, 0), (-1, 0), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9F9")]),
                ]
            )
        )

        elements.append(t)

        try:
            doc.build(elements)
            messagebox.showinfo(
                "Éxito", f"Archivo guardado correctamente en:\n{ruta_completa}", parent=self.ventana
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo construir el PDF:\n{e}", parent=self.ventana
            )
    # ----------------------------------------------------------------------------------------------
    


   