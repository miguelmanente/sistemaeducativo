
# ==========================================================================================
#             RANKING DE INASISTENCIAS DE DOCENTES - MÓDULO rankinginasistencias.py
# ==========================================================================================

# ------------------------------------------ LIBRERÍAS -------------------------------------
import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Fuerza a Matplotlib a usar el backend de Tkinter existente
import matplotlib.pyplot as plt
# ---------------------------- Librerías para generación de PDF (ReportLab)--------------------
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
# ---------------------------- Fin Librerías -------------------------------------------------

# ---------------------------- Función principal ranking -------------------------------------
class RankingInasistenciasApp:
    def __init__(self, parent,  db_path="bdescuela.db"):
        
      # Si parent es un Toplevel o Tk, usamos parent directamente
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Ranking de Inasistencias")
        self.ventana.state("zoomed")
        self.db_path = db_path

        # Le da foco a la ventana emergente
        self.ventana.grab_set()

        # Asegura que la ventana quede por encima al abrirse
        self.ventana.focus_set()
       # self.db_path = db_path

        # Contenedor Principal (Panel Dividido)
        main_frame = ttk.Frame(self.ventana, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel Izquierdo: Tabla de Ranking
        left_frame = ttk.LabelFrame(main_frame, text=" Ranking de Docentes ", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cols = ("ID", "Docente", "Total Faltas", "Cat. Predominante")
        self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Docente", text="Docente")
        self.tree.heading("Total Faltas", text="Total Faltas")
        self.tree.heading("Cat. Predominante", text="Cat. Predominante")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Docente", width=180)
        self.tree.column("Total Faltas", width=90, anchor="center")
        self.tree.column("Cat. Predominante", width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_docente_select)

        # Panel Derecho: Gráfico de Torta
        self.right_frame = ttk.LabelFrame(main_frame, text=" Distribución por Motivo ", padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Matplotlib Figura
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------
        # PANEL INFERIOR: Botones de Acción
        # -------------------------------------------------------------
        btn_frame = ttk.Frame(self.ventana, padding=(10, 5, 10, 10))
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_exportar = ttk.Button(
            btn_frame, 
            text="📄 Exportar Docente a PDF", 
            command=self.exportar_pdf
        )
        self.btn_exportar.pack(side=tk.LEFT, padx=5)

        self.btn_cerrar = tk.Button(
            btn_frame, 
            text="❌ Cerrar Ventana", 
            command=self.cerrar_pantalla
        )
        self.btn_cerrar.pack(side=tk.RIGHT, padx=5)

        # También intercepta el clic en la "X" de la ventana arriba a la derecha
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_pantalla)

        # Variables para mantener la selección actual
        self.docente_seleccionado = None

        self.cargar_ranking()

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
    # --------------------------------------------------------------------------

    # ---------Carga el ranking de inasistencias en la tabla--------------------
    def cargar_ranking(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            WITH ResumenMotivos AS (
                SELECT id_docente, motivo, COUNT(*) AS cantidad,
                    ROW_NUMBER() OVER (PARTITION BY id_docente ORDER BY COUNT(*) DESC) as rn
                FROM inasistencia GROUP BY id_docente, motivo
            ),
            TotalFaltas AS (
                SELECT id_docente, COUNT(*) AS total FROM inasistencia GROUP BY id_docente
            )
            SELECT p.id_docente, p.nombre || ' ' || p.apellido, tf.total, rm.motivo
            FROM TotalFaltas tf
            JOIN profesores p ON p.id_docente = tf.id_docente
            JOIN ResumenMotivos rm ON rm.id_docente = tf.id_docente AND rm.rn = 1
            ORDER BY tf.total DESC;
        """
        
        for row in cursor.execute(query):
            self.tree.insert("", tk.END, values=row)

        conn.close()
    # ------------------------------------------------------------------------------

    # --------------------- Evento al seleccionar un docente en la tabla ------------------
    def on_docente_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        id_docente = item["values"][0]
        nombre_docente = item["values"][1]

        self.docente_seleccionado = {
            "id": id_docente,
            "nombre": nombre_docente,
            "total": item["values"][2]
        }
        self.actualizar_grafico(id_docente, nombre_docente)
    # --------------------------------------------------------------------------------

    # --------------------- Actualiza el gráfico de torta según el docente seleccionado ------------------
    def actualizar_grafico(self, id_docente, nombre_docente):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
        SELECT motivo, COUNT(*) 
        FROM inasistencia 
        WHERE id_docente = ? 
        GROUP BY motivo
        """
        cursor.execute(query, (id_docente,))
        data = cursor.fetchall()
        conn.close()

        self.ax.clear()
        if data:
            motivos = [row[0] for row in data]
            cantidades = [row[1] for row in data]

            self.ax.pie(cantidades, labels=motivos, autopct='%1.1f%%', startangle=140)
            self.ax.set_title(f"Motivos de faltas:\n{nombre_docente}")
        else:
            self.ax.text(0.5, 0.5, "Sin datos", ha='center', va='center')

        self.fig.tight_layout()
        self.canvas.draw()
    # --------------------------------------------------------------------------------

    # --------------------- Exportar PDF del docente seleccionado -------------------------
    def exportar_pdf(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor, seleccione un docente de la lista para exportar.",parent=self.ventana)
            return

        # Obtener valores directamente de la fila seleccionada en la tabla
        item = self.tree.item(selected[0])
        valores = item["values"]
        
        id_docente = valores[0]
        nombre_docente = valores[1]
        total_faltas = valores[2]
        cat_predominante = valores[3]  # <--- Lee directo la columna Cat. Predominante

        # Ruta de salida
        carpeta_destino = os.path.join("reportes", "pdf", "faltadocentes")
        os.makedirs(carpeta_destino, exist_ok=True)

        nombre_limpio = str(nombre_docente).replace(" ", "_")
        pdf_path = os.path.join(carpeta_destino, f"Reporte_{nombre_limpio}.pdf")

        # Guardar gráfico temporal
        img_temp = "temp_grafico_inasistencia.png"
        self.fig.savefig(img_temp, dpi=200, bbox_inches='tight')

        try:
            doc = SimpleDocTemplate(
                pdf_path, 
                pagesize=letter, 
                rightMargin=40, leftMargin=40, 
                topMargin=40, bottomMargin=40
            )
            styles = getSampleStyleSheet()
            elements = []

            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=18,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=15
            )
            elements.append(Paragraph("Informe de Inasistencias Docente", title_style))
            elements.append(Spacer(1, 10))

            datos_docente = [
                ["Docente:", str(nombre_docente)],
                ["ID / Legajo:", str(id_docente)],
                ["Total Días Faltados:", str(total_faltas)],
                ["Categoría Predominante:", str(cat_predominante)]
            ]

            tabla = Table(datos_docente, colWidths=[180, 320])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2d3748')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ]))
            elements.append(tabla)
            elements.append(Spacer(1, 20))

            sub_style = ParagraphStyle(
                'SubTitle',
                parent=styles['Heading2'],
                fontName='Helvetica-Bold',
                fontSize=13,
                textColor=colors.HexColor('#2b6cb0'),
                spaceAfter=10
            )
            elements.append(Paragraph("Distribución Porcentual por Motivo de Inasistencia", sub_style))
            elements.append(Image(img_temp, width=380, height=280))

            doc.build(elements)

            if os.path.exists(img_temp):
                os.remove(img_temp)

            messagebox.showinfo("Éxito", f"El informe PDF se guardó correctamente en:\n{pdf_path}",parent=self.ventana)

        except Exception as e:
            if os.path.exists(img_temp):
                os.remove(img_temp)
            messagebox.showerror("Error", f"Ocurrió un error al generar el PDF:\n{e}",parent=self.ventana)
    # ----------------------------------------------------------------------------------------------


