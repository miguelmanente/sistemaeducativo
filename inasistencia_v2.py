# =============================================================================
# IMPORTACIONES
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox

from database import conectar
from estilos import configurar_estilos


# =============================================================================
# CLASE PRINCIPAL
# =============================================================================

class InasistenciaDocente:

    # =========================================================================
    # 1. INICIALIZACIÓN
    # =========================================================================

    def __init__(self):

        # -------------------------------------------------
        # VARIABLES INTERNAS
        # -------------------------------------------------

        self.docentes = {}          # diccionario: nombre -> id_docente
        self.lista_docentes = []    # lista para combobox

        self.id_inasistencia = None # registro seleccionado

        # -------------------------------------------------
        # VENTANA PRINCIPAL
        # -------------------------------------------------

        self.ventana = tk.Toplevel()
        self.ventana.title("Sistema de Gestión Educativa - Inasistencias")
        self.ventana.state("zoomed")

        configurar_estilos()

        # -------------------------------------------------
        # CONSTRUCCIÓN DE INTERFAZ
        # -------------------------------------------------

        self.crear_widgets()

        # -------------------------------------------------
        # CARGA INICIAL
        # -------------------------------------------------

        self.cargar_docentes()
    # -------------------------------------------------------------------------------

    # =========================  CARGA DEL DOCENTE ==================================
    def cargar_docentes(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_docente, apellido, nombre
            FROM profesores
            ORDER BY apellido, nombre
        """)

        datos = cursor.fetchall()
        conn.close()

        self.docentes = {}
        self.lista_docentes = []

        for id_docente, ape, nom in datos:
            nombre = f"{ape} {nom}"
            self.docentes[nombre] = id_docente
            self.lista_docentes.append(nombre)

        self.cmb_docente["values"] = self.lista_docentes

        # evento
        self.cmb_docente.bind("<<ComboboxSelected>>", self.on_docente_seleccionado)
    # ------------------------------------------------------------------------------

    # ==================== Evento de docente seleccionado ==========================
    def on_docente_seleccionado(self, event=None):

        nombre = self.cmb_docente.get()

        self.id_docente_actual = self.docentes.get(nombre)

        if not self.id_docente_actual:
            return

        self.cargar_asignaciones()
        self.cargar_tree()
    # ------------------------------------------------------------------------------

    # =============== CARGAR ASIGNACIONES COMBO CARGO/MATERIA ======================
    def cargar_asignaciones(self):

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id_asignacion,
                COALESCE(m.nombre, a.cargo) || ' - ' || a.curso
            FROM asignacion a
            LEFT JOIN materias m ON a.id_materia = m.id_materia
            WHERE a.id_docente = ?
        """, (self.id_docente_actual,))

        datos = cursor.fetchall()
        conn.close()

        self.asignaciones_dict = {}
        lista = []

        for id_asig, texto in datos:
            self.asignaciones_dict[texto] = id_asig
            lista.append(texto)

        self.cmb_asignacion["values"] = lista
    # -----------------------------------------------------------------------------

    # ================= cargar treeview (inasistencias +Join) ====================
    def cargar_tree(self):

        # 1. limpiar SIEMPRE
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.id,
                p.apellido || ' ' || p.nombre,
                COALESCE(m.nombre, ''),
                a.cargo,
                a.modulos,
                a.curso,
                a.situacion_revista,
                i.fecha_desde,
                i.fecha_hasta,
                i.motivo,
                i.observacion
            FROM inasistencia i
            JOIN profesores p ON p.id_docente = i.id_docente
            LEFT JOIN asignacion a ON a.id_docente = p.id_docente
            LEFT JOIN materias m ON m.id_materia = a.id_materia
            WHERE i.id_docente = ?
            ORDER BY i.fecha_desde DESC
        """, (self.id_docente_actual,))

        datos = cursor.fetchall()
        conn.close()

        for fila in datos:

            (
                id_inas,
                docente,
                materia,
                cargo,
                modulos,
                curso,
                revista,
                desde,
                hasta,
                motivo,
                obs
            ) = fila

            self.tabla.insert(
                "",
                "end",
                values=(
                    id_inas,
                    docente,
                    materia,
                    cargo,
                    modulos,
                    curso,
                    revista,
                    desde,
                    hasta,
                    motivo,
                    obs
                )
            )
    # -----------------------------------------------------------------------------

    # ========================== VALIDACIÓN SIMPLE ================================
    def validar(self):

        if not self.cmb_docente.get():
            messagebox.showwarning("Atención", "Debe seleccionar un docente",parent=self.ventana)
            return False

        if not self.txt_desde.get():
            messagebox.showwarning("Atención", "Debe ingresar fecha desde",parent=self.ventana)
            return False

        if not self.txt_hasta.get():
            messagebox.showwarning("Atención", "Debe ingresar fecha hasta",parent=self.ventana)
            return False

        if not self.cmb_motivo.get():
            messagebox.showwarning("Atención", "Debe seleccionar un motivo",parent=self.ventana)
            return False

        return True
    # -----------------------------------------------------------------------------

    # ===================== LIMPIAR FORMULARIO ====================================
    def limpiar(self):
       
        self.txt_desde.delete(0, tk.END)
        self.txt_hasta.delete(0, tk.END)
        
        self.cmb_motivo.set("")
        self.txt_observacion.delete(0, tk.END)

        self.id_inasistencia = None

        self.tabla.selection_remove(self.tabla.selection())
    # -----------------------------------------------------------------------------

    # ===================== INSERTAR INASISTENCIAS ================================
    def agregar(self):

        if not self.validar():
            return

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO inasistencia (
                    id_docente,
                    fecha_desde,
                    fecha_hasta,
                    motivo,
                    observacion
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.id_docente_actual,
                self.txt_desde.get(),
                self.txt_hasta.get(),
                self.cmb_motivo.get(),
                self.txt_observacion.get()
            ))

            conn.commit()

        except Exception as e:
            messagebox.showerror("Error", str(e),parent=self.ventana)

        finally:
            conn.close()

        # refrescar
        self.cargar_tree()
        self.limpiar()

        messagebox.showinfo("Éxito", "Inasistencia registrada correctamente",parent=self.ventana)
    # -----------------------------------------------------------------------------

    # ==================== SELECCIONAR FILA DEL TREEVIEW ==========================
    def seleccionar_tree(self, event):

        seleccion = self.tabla.focus()

        if not seleccion:
            return

        valores = self.tabla.item(seleccion, "values")

        # ID REAL de la base de datos
        self.id_inasistencia = int(valores[0])

        # Cargar formulario
        self.txt_desde.delete(0, tk.END)
        self.txt_desde.insert(0, valores[7])

        self.txt_hasta.delete(0, tk.END)
        self.txt_hasta.insert(0, valores[8])

        self.cmb_motivo.set(valores[9])

        self.txt_observacion.delete(0, tk.END)
        self.txt_observacion.insert(0, valores[10])
    # -----------------------------------------------------------------------------

    # ============================ MODIFICAR INASISTENCIA ========================
    def modificar(self):

        if not self.id_inasistencia:
            messagebox.showwarning("Atención", "Debe seleccionar un registro",parent=self.ventana)
            return

        if not self.validar():
            return

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE inasistencia
                SET fecha_desde = ?,
                    fecha_hasta = ?,
                    motivo = ?,
                    observacion = ?
                WHERE id = ?
            """, (
                self.txt_desde.get(),
                self.txt_hasta.get(),
                self.cmb_motivo.get(),
                self.txt_observacion.get(),
                self.id_inasistencia
            ))

            conn.commit()

        except Exception as e:
            messagebox.showerror("Error", str(e),parent=self.ventana)

        finally:
            conn.close()

        self.cargar_tree()
        self.limpiar()

        messagebox.showinfo("OK", "Registro modificado correctamente",parent=self.ventana)
    # -----------------------------------------------------------------------------

    # ===================== ELIMINAR INASISTENCIA =================================
    def eliminar(self):

        if not self.id_inasistencia:
            messagebox.showwarning("Atención", "Debe seleccionar un registro",parent=self.ventana)
            return

        resp = messagebox.askyesno(
            "Confirmar",
            "¿Seguro que desea eliminar este registro?",parent=self.ventana
        )

        if not resp:
            return

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM inasistencia
                WHERE id = ?
            """, (self.id_inasistencia,))

            conn.commit()

        except Exception as e:
            messagebox.showerror("Error", str(e),parent=self.ventana)

        finally:
            conn.close()

        self.cargar_tree()
        self.limpiar()

        messagebox.showinfo("OK", "Registro eliminado correctamente",parent=self.ventana)
    # -----------------------------------------------------------------------------

    # =======================  exportación a pdf ==================================
    def generar_pdf(self):

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    p.apellido || ' ' || p.nombre,
                    i.fecha_desde,
                    i.fecha_hasta,
                    i.motivo,
                    i.observacion
                FROM inasistencia i
                JOIN profesores p ON p.id_docente = i.id_docente
                WHERE i.id_docente = ?
                ORDER BY i.fecha_desde DESC
            """, (self.id_docente_actual,))

            datos = cursor.fetchall()
            conn.close()

            if not datos:
                messagebox.showwarning("Atención", "No hay datos para generar PDF",parent=self.ventana)
                return

            archivo = "inasistencias.pdf"
            c = canvas.Canvas(archivo, pagesize=letter)

            y = 750

            c.setFont("Helvetica-Bold", 14)
            c.drawString(200, y, "REPORTE DE INASISTENCIAS")
            y -= 40

            c.setFont("Helvetica", 10)

            for fila in datos:

                texto = f"{fila[0]} | {fila[1]} al {fila[2]} | {fila[3]} | {fila[4]}"
                c.drawString(30, y, texto)

                y -= 20

                if y < 50:
                    c.showPage()
                    y = 750

            c.save()

            messagebox.showinfo("OK", "PDF generado correctamente",parent=self.ventana)

        except Exception as e:
            messagebox.showerror("Error PDF", str(e),parent=self.ventana)
    # -----------------------------------------------------------------------------

    # =============================================================================
    # 2. CREACIÓN DE INTERFAZ (WIDGETS)
    # =============================================================================

    def crear_widgets(self):

        # -------------------------------------------------
        # FRAME SUPERIOR
        # -------------------------------------------------

        frame_superior = ttk.LabelFrame(
            self.ventana,
            text="Gestión de Inasistencias"
        )
        frame_superior.pack(side="top", fill="x", padx=10, pady=10)

        # -------------------------------------------------
        # DOCENTE
        # -------------------------------------------------

        ttk.Label(frame_superior, text="Docente:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )

        self.cmb_docente = ttk.Combobox(
            frame_superior,
            state="readonly",
            width=40
        )
        self.cmb_docente.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # -------------------------------------------------
        # CARGO / MATERIA
        # -------------------------------------------------

        ttk.Label(frame_superior, text="Cargo / Materia:").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )

        self.cmb_asignacion = ttk.Combobox(
            frame_superior,
            state="readonly",
            width=40
        )
        self.cmb_asignacion.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # -------------------------------------------------
        # FECHAS
        # -------------------------------------------------

        ttk.Label(frame_superior, text="Desde:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )

        self.txt_desde = ttk.Entry(frame_superior)
        self.txt_desde.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_superior, text="Hasta:").grid(
            row=1, column=2, padx=5, pady=5, sticky="e"
        )

        self.txt_hasta = ttk.Entry(frame_superior)
        self.txt_hasta.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        # -------------------------------------------------
        # MOTIVO
        # -------------------------------------------------

        ttk.Label(frame_superior, text="Motivo:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )

        self.cmb_motivo = ttk.Combobox(
            frame_superior,
            state="readonly",
            values=[
                "Licencia Médica",
                "ART",
                "Estudio",
                "Injustificada",
                "Maternidad",
                "Gremial",
                "Particular",
                "Fallecimiento"
            ]
        )
        self.cmb_motivo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # -------------------------------------------------
        # OBSERVACIÓN
        # -------------------------------------------------

        ttk.Label(frame_superior, text="Observación:").grid(
            row=2, column=2, padx=5, pady=5, sticky="e"
        )

        self.txt_observacion = ttk.Entry(frame_superior)
        self.txt_observacion.grid(row=2, column=3, padx=5, pady=5, sticky="ew")

        # -------------------------------------------------
        # BOTONES (placeholder por ahora)
        # -------------------------------------------------

        frame_botones = tk.Frame(frame_superior)
        frame_botones.grid(row=3, column=0, columnspan=4, pady=10)

        tk.Button(frame_botones, text="Agregar", command=self.agregar).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Modificar", command=self.modificar).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Eliminar", command=self.eliminar).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Limpiar", command=self.limpiar).pack(side="left", padx=5)
        tk.Button(frame_botones, text="PDF", command=self.generar_pdf).pack(side="left", padx=5)
        tk.Button(frame_botones, text="Cerrar", command=self.ventana.destroy).pack(side="left", padx=5)


        # -------------------------------------------------
        # FRAME INFERIOR (TREEVIEW)
        # -------------------------------------------------

        frame_inferior = ttk.LabelFrame(
            self.ventana,
            text="Historial de Inasistencias"
        )
        frame_inferior.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

        columnas = (
            "id",
            "docente",
            "materia",
            "cargo",
            "modulos",
            "curso",
            "revista",
            "desde",
            "hasta",
            "motivo",
            "observacion"
        )

        self.tabla = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
        self.tabla.column("id", width=0, stretch=False)
        for col in columnas:
            self.tabla.column("id", width=0, stretch=False)
            self.tabla.heading(col, text=col.capitalize())
            self.tabla.column(col, width=120)
        
        self.tabla.pack(fill="both", expand=True)

        self.tabla.bind("<<TreeviewSelect>>", self.seleccionar_tree)

# =========================  INICIO de la Inasistencia_v2 ==============================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # oculta la ventana principal
    app = InasistenciaDocente()
    root.mainloop()
# --------------------------------------------------------------------------------------

