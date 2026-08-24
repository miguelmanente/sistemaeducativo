# =============================================================================
# ALTAS INASISTENCIAS DE DOCENTES - Módulo inasistencia_v2.py
# =============================================================================
""" Módulo para gestionar las inasistencias de los docentes. 
Su funcionalidad incluye la carga, modificación, eliminación y 
visualización de inasistencias, así como la generación de reportes en PDF. """

# =============================================================================
# IMPORTACIONES
# =============================================================================
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
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

    # ==================== DETERMINAR SI ASIGNACIÓN QUEDA AFECTADA =================
    def asignacion_afectada(self, dia_asignacion, fecha_desde, fecha_hasta, cursor):
        """
        Determina si una asignación del docente queda afectada
        por el período de inasistencia.
        """

        try:
            desde = datetime.strptime(fecha_desde, "%d/%m/%Y")
            hasta = datetime.strptime(fecha_hasta, "%d/%m/%Y")
        except ValueError:
            return False

        # Obtener los días no laborables del período
        cursor.execute("""
            SELECT fecha
            FROM dias_no_laborables
            WHERE fecha BETWEEN ? AND ?
        """, (
            fecha_desde,
            fecha_hasta
        ))

        no_laborables = {
            fila[0] for fila in cursor.fetchall()
        }

        dias_semana = {
            0: "Lunes",
            1: "Martes",
            2: "Miércoles",
            3: "Jueves",
            4: "Viernes"
        }

        fecha = desde

        while fecha <= hasta:

            # Sábado y domingo
            if fecha.weekday() <= 4:

                fecha_str = fecha.strftime("%d/%m/%Y")

                # No se trabaja en días no laborables
                if fecha_str not in no_laborables:

                    # Cargo de lunes a viernes
                    if dia_asignacion == "Lunes a Viernes":
                        return True

                    # Materia/asignación de un día específico
                    if dia_asignacion == dias_semana[fecha.weekday()]:
                        return True

            fecha += timedelta(days=1)

        return False
    # ----------------------------------------------------------------------------------

    # ================= cargar treeview (inasistencias +Join) ====================
    def cargar_tree(self):
        # 1. Limpiar siempre
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
                a.dia,
                i.fecha_desde,
                i.fecha_hasta,
                i.motivo,
                i.observacion
            FROM inasistencia i
            JOIN profesores p
                ON p.id_docente = i.id_docente
            LEFT JOIN asignacion a
                ON a.id_docente = p.id_docente
            LEFT JOIN materias m
                ON m.id_materia = a.id_materia
            WHERE i.id_docente = ?
            ORDER BY i.fecha_desde DESC
        """, (self.id_docente_actual,))

        datos = cursor.fetchall()

        for fila in datos:

            (
                id_inas,
                docente,
                materia,
                cargo,
                modulos,
                curso,
                revista,
                dia_asignacion,
                desde,
                hasta,
                motivo,
                obs
            ) = fila

            # Si no hay asignación, no mostramos la fila
            if dia_asignacion is None:
                continue

            # Verificar si esta asignación realmente
            # corresponde a algún día de la inasistencia
            if not self.asignacion_afectada(
                dia_asignacion,
                desde,
                hasta,
                cursor
            ):
                continue

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

        conn.close()
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

   # ======================= EXPORTACIÓN A PDF =======================

    def generar_pdf(self):

        try:

            import os

            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import (
                getSampleStyleSheet,
                ParagraphStyle
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
            # CONEXIÓN A LA BASE DE DATOS
            # ==========================================================

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    p.apellido,
                    p.nombre,
                    i.fecha_desde,
                    i.fecha_hasta,
                    i.motivo,
                    i.observacion
                FROM inasistencia i
                JOIN profesores p
                    ON p.id_docente = i.id_docente
                WHERE i.id_docente = ?
                ORDER BY i.fecha_desde DESC
            """, (self.id_docente_actual,))

            datos = cursor.fetchall()

            conn.close()

            # ==========================================================
            # COMPROBAR DATOS
            # ==========================================================

            if not datos:

                messagebox.showwarning(
                    "Atención",
                    "No hay inasistencias para generar el PDF.",
                    parent=self.ventana
                )

                return

            # ==========================================================
            # DATOS DEL DOCENTE
            # ==========================================================

            apellido = str(datos[0][0] or "").strip()
            nombre = str(datos[0][1] or "").strip()

            docente = f"{apellido}, {nombre}"

            # ==========================================================
            # CARPETA DE DESTINO
            # ==========================================================

            carpeta_modulo = os.path.dirname(
                os.path.abspath(__file__)
            )

            carpeta_reportes = os.path.join(
                carpeta_modulo,
                "reportes"
            )

            carpeta_pdf = os.path.join(
                carpeta_reportes,
                "pdf"
            )

            carpeta_inasistencia = os.path.join(
                carpeta_pdf,
                "Inasistencia"
            )

            os.makedirs(
                carpeta_inasistencia,
                exist_ok=True
            )

            # ==========================================================
            # NOMBRE DEL ARCHIVO
            # ==========================================================

            nombre_archivo = f"Inasistencias_{apellido}_{nombre}.pdf"

            caracteres_invalidos = '<>:"/\\|?*'

            for caracter in caracteres_invalidos:
                nombre_archivo = nombre_archivo.replace(
                    caracter,
                    "_"
                )

            archivo = os.path.join(
                carpeta_inasistencia,
                nombre_archivo
            )

            # ==========================================================
            # CONFIGURACIÓN DEL DOCUMENTO
            # ==========================================================

            documento = SimpleDocTemplate(
                archivo,
                pagesize=A4,
                rightMargin=18 * mm,
                leftMargin=18 * mm,
                topMargin=18 * mm,
                bottomMargin=18 * mm
            )

            estilos = getSampleStyleSheet()

            # ==========================================================
            # ESTILOS
            # ==========================================================

            estilo_titulo = ParagraphStyle(
                "Titulo",
                parent=estilos["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=17,
                leading=20,
                alignment=TA_CENTER,
                textColor=colors.white
            )

            estilo_subtitulo = ParagraphStyle(
                "Subtitulo",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                alignment=TA_CENTER,
                textColor=colors.white
            )

            estilo_etiqueta = ParagraphStyle(
                "Etiqueta",
                parent=estilos["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#555555")
            )

            estilo_valor = ParagraphStyle(
                "Valor",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#1a1a1a")
            )

            estilo_observacion = ParagraphStyle(
                "Observacion",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=colors.HexColor("#1a1a1a")
            )

            estilo_pie = ParagraphStyle(
                "Pie",
                parent=estilos["Normal"],
                fontName="Helvetica",
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#666666")
            )

            elementos = []

            # ==========================================================
            # ENCABEZADO
            # ==========================================================

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
                            "REPORTE DE INASISTENCIAS",
                            estilo_subtitulo
                        )
                    ]
                ],
                colWidths=[174 * mm]
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
                            9
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            9
                        )
                    ]
                )
            )

            elementos.append(encabezado)

            elementos.append(
                Spacer(1, 7 * mm)
            )

            # ==========================================================
            # DOCENTE
            # ==========================================================

            docente_tabla = Table(
                [
                    [
                        Paragraph(
                            "DOCENTE",
                            estilo_etiqueta
                        ),
                        Paragraph(
                            docente,
                            ParagraphStyle(
                                "NomeDocente",
                                parent=estilo_valor,
                                fontName="Helvetica-Bold",
                                fontSize=12
                            )
                        )
                    ]
                ],
                colWidths=[
                    30 * mm,
                    144 * mm
                ]
            )

            docente_tabla.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (0, 0),
                            colors.HexColor("#f4f4f4")
                        ),
                        (
                            "BOX",
                            (0, 0),
                            (-1, -1),
                            0.6,
                            colors.HexColor("#cccccc")
                        ),
                        (
                            "INNERGRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.HexColor("#dddddd")
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

            elementos.append(docente_tabla)

            elementos.append(
                Spacer(1, 7 * mm)
            )

            # ==========================================================
            # CADA INASISTENCIA
            # ==========================================================

            for numero, fila in enumerate(datos, start=1):

                fecha_desde = str(fila[2] or "").strip()
                fecha_hasta = str(fila[3] or "").strip()
                motivo = str(fila[4] or "").strip()
                observacion = str(fila[5] or "").strip()

                # ----------------------------------------------
                # ENCABEZADO DEL REGISTRO
                # ----------------------------------------------

                titulo_registro = Table(
                    [
                        [
                            Paragraph(
                                f"INASISTENCIA N.º {numero}",
                                ParagraphStyle(
                                    "Registro",
                                    parent=estilo_etiqueta,
                                    fontName="Helvetica-Bold",
                                    fontSize=10,
                                    textColor=colors.white
                                )
                            )
                        ]
                    ],
                    colWidths=[174 * mm]
                )

                titulo_registro.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, -1),
                                colors.HexColor("#34495e")
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                8
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                8
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                6
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                6
                            )
                        ]
                    )
                )

                elementos.append(titulo_registro)

                # ----------------------------------------------
                # DATOS DEL REGISTRO
                # ----------------------------------------------

                datos_inasistencia = [
                    [
                        Paragraph(
                            "Período:",
                            estilo_etiqueta
                        ),
                        Paragraph(
                            f"{fecha_desde} al {fecha_hasta}",
                            estilo_valor
                        )
                    ],
                    [
                        Paragraph(
                            "Motivo:",
                            estilo_etiqueta
                        ),
                        Paragraph(
                            motivo if motivo else "-",
                            estilo_valor
                        )
                    ],
                    [
                        Paragraph(
                            "Observación:",
                            estilo_etiqueta
                        ),
                        Paragraph(
                            observacion if observacion else "-",
                            estilo_observacion
                        )
                    ]
                ]

                tabla_inasistencia = Table(
                    datos_inasistencia,
                    colWidths=[
                        30 * mm,
                        144 * mm
                    ]
                )

                tabla_inasistencia.setStyle(
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
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP"
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
                                7
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                7
                            )
                        ]
                    )
                )

                elementos.append(tabla_inasistencia)

                elementos.append(
                    Spacer(1, 5 * mm)
                )

            # ==========================================================
            # PIE DEL DOCUMENTO
            # ==========================================================

            elementos.append(
                HRFlowable(
                    width="100%",
                    thickness=0.6,
                    color=colors.HexColor("#cccccc"),
                    spaceBefore=5,
                    spaceAfter=7
                )
            )

            elementos.append(
                Paragraph(
                    f"Total de inasistencias registradas: {len(datos)}",
                    estilo_pie
                )
            )

            elementos.append(
                Spacer(1, 2 * mm)
            )

            elementos.append(
                Paragraph(
                    "Documento generado por el Sistema de Gestión Educativa (SGE)",
                    estilo_pie
                )
            )

            # ==========================================================
            # GENERAR DOCUMENTO
            # ==========================================================

            documento.build(elementos)

            messagebox.showinfo(
                "PDF generado",
                "El reporte de inasistencias fue generado correctamente.\n\n"
                f"Guardado en:\n{archivo}",
                parent=self.ventana
            )

        except Exception as e:

            messagebox.showerror(
                "Error PDF",
                f"No se pudo generar el PDF.\n\n"
                f"Detalle:\n{e}",
                parent=self.ventana
            )

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

