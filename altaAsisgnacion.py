# ================================================================================
#                       MÓDULO ASIGNACIONES DOCENTES
# ================================================================================

# =============================  LIBRERÍAS =======================================
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import conectar
from centraVent import centrar_ventana
from Backup import crear_backup
from estilos import configurar_estilos
from utilidades import normalizar_fecha, normalizar_hora
from validaciones import (
    existe_asignacion,
    hay_incompatibilidad_horaria,
    validar_fecha,
    validar_horario,
    validar_rango_fechas
)

# Importaciones necesarias de ReportLab para el PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import os
import time

# --------------------------------------------------------------------------------


# ====================== PANTALLA PRINCIPAL DE ASIGNACIONES ======================
def info_asignaciones():

    # ----------------- DEFINICIÓN DE LA VENTANA PRINCIPAL -----------------------
    ventana = tk.Toplevel()
    configurar_estilos()

    ventana.title("Asignaciones Docentes")
    ventana.state('zoomed')

    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=2)
    ventana.columnconfigure(0, weight=1)

    # ============================================================================
    # VARIABLES
    # ============================================================================

    profesor_var = tk.StringVar()
    materia_var = tk.StringVar()
    dia_var = tk.StringVar()
    cargo_var = tk.StringVar()
    modulos_var = tk.IntVar()
    curso_var = tk.StringVar()
    turno_var = tk.StringVar()
    entrada_var = tk.StringVar()
    salida_var = tk.StringVar()
    situacion_var = tk.StringVar()
    toma_pos_var = tk.StringVar()
    fecha_cese_var = tk.StringVar()
    activo_var = tk.IntVar(value=1)

    profesores_dict = {}
    materia_dict = {}

    id_seleccionado = None

    # ============================================================================
    # FRAME SUPERIOR
    # ============================================================================

    frame_superior = ttk.LabelFrame(
        ventana,
        text="Asignar Profesor",
        padding=20
    )

    frame_superior.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=5,
        pady=10
    )

    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # ============================================================================
    # ESTILOS DE COMBOBOX
    # ============================================================================

    style = ttk.Style()

    style.configure(
        "TCombobox",
        font=("Arial", 12)
    )

    ventana.option_add(
        "*TCombobox*Listbox.font",
        ("Arial", 12)
    )

    # ============================================================================
    # CAMPOS DE LA INTERFAZ
    # ============================================================================

    ttk.Label(
        frame_superior,
        text="Docente:",
        font=("Arial", 12)
    ).grid(row=0, column=0, sticky="e", padx=5, pady=5)

    combo_profesor = ttk.Combobox(
        frame_superior,
        textvariable=profesor_var,
        state="readonly",
        font=("Arial", 12)
    )

    combo_profesor.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Materia:",
        font=("Arial", 12)
    ).grid(row=0, column=2, sticky="e", padx=5, pady=5)

    combo_materia = ttk.Combobox(
        frame_superior,
        textvariable=materia_var,
        state="readonly",
        font=("Arial", 12)
    )

    combo_materia.grid(
        row=0,
        column=3,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Día:",
        font=("Arial", 12)
    ).grid(row=0, column=4, sticky="e", padx=5, pady=5)

    combo_dia = ttk.Combobox(
        frame_superior,
        textvariable=dia_var,
        values=[
            "",
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Lunes a Viernes"
        ],
        state="readonly",
        font=("Arial", 12)
    )

    combo_dia.grid(
        row=0,
        column=5,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Tipo_Cargo:",
        font=("Arial", 12)
    ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

    combo_cargo = ttk.Combobox(
        frame_superior,
        textvariable=cargo_var,
        values=[
            "",
            "Director",
            "ViceDirector",
            "Secretario",
            "Profesor",
            "EMATP",
            "Enc.Laboratorio",
            "Jefe Dpto",
            "Preceptor",
            "Bibliotecario",
            "Auxiliar",
            "Taller"
        ],
        state="readonly",
        font=("Arial", 12)
    )

    combo_cargo.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Módulos:",
        font=("Arial", 12)
    ).grid(row=1, column=2, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=modulos_var,
        font=("Arial", 12),
        width=20
    ).grid(
        row=1,
        column=3,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Curso:",
        font=("Arial", 12)
    ).grid(row=1, column=4, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=curso_var,
        font=("Arial", 12),
        width=20
    ).grid(
        row=1,
        column=5,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Turno:",
        font=("Arial", 12)
    ).grid(row=2, column=0, sticky="e", padx=5, pady=5)

    combo_turno = ttk.Combobox(
        frame_superior,
        textvariable=turno_var,
        state="readonly",
        font=("Arial", 12),
        values=[
            "",
            "Mañana",
            "Tarde",
            "Vespertino",
            "Noche"
        ]
    )

    combo_turno.grid(
        row=2,
        column=1,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Hora Entrada:",
        font=("Arial", 12)
    ).grid(row=2, column=2, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=entrada_var,
        font=("Arial", 12)
    ).grid(
        row=2,
        column=3,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Hora Salida:",
        font=("Arial", 12)
    ).grid(row=2, column=4, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=salida_var,
        font=("Arial", 12)
    ).grid(
        row=2,
        column=5,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Situación Revista:",
        font=("Arial", 12)
    ).grid(row=3, column=0, sticky="e", padx=5, pady=5)

    combo_situacion = ttk.Combobox(
        frame_superior,
        textvariable=situacion_var,
        values=[
            "",
            "Titular",
            "Provisorio",
            "Suplente",
            "Interino"
        ],
        state="readonly",
        font=("Arial", 12)
    )

    combo_situacion.grid(
        row=3,
        column=1,
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Toma de Posición:",
        font=("Arial", 12)
    ).grid(row=3, column=2, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=toma_pos_var,
        font=("Arial", 12)
    ).grid(
        row=3,
        column=3,
        sticky="ew",
        padx=5,
        pady=5
    )

    ttk.Label(
        frame_superior,
        text="Fecha Cese:",
        font=("Arial", 12)
    ).grid(row=3, column=4, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=fecha_cese_var,
        font=("Arial", 12)
    ).grid(
        row=3,
        column=5,
        sticky="ew",
        padx=5,
        pady=5
    )

    # ============================================================================
    # CHECKBUTTON ACTIVO
    # ============================================================================

    chk_activo = tk.Checkbutton(
        frame_superior,
        text="Docente Activo ?",
        variable=activo_var,
        onvalue=1,
        offvalue=0,
        font=("Arial", 18, "bold"),
        bg="#ecf0f1",
        activebackground="#ecf0f1"
    )

    chk_activo.grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="w",
        padx=5,
        pady=5
    )

    # ============================================================================
    # TREEVIEW
    # ============================================================================

    style.configure(
        "Valido.TEntry",
        foreground="black"
    )

    style.configure(
        "Error.TEntry",
        foreground="black"
    )

    style.map(
        "Error.TEntry",
        fieldbackground=[("!disabled", "#ffcccc")]
    )

    frame_inferior = ttk.LabelFrame(
        ventana,
        text="Listado Asignaciones",
        padding=10
    )

    frame_inferior.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=20,
        pady=10
    )

    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    columnas = (
        "id",
        "profesor",
        "materia",
        "dia",
        "tipo_cargo",
        "módulos",
        "curso",
        "turno",
        "hentrada",
        "hsalida",
        "situacion_revista",
        "toma_pos",
        "fecha_cese",
        "activo"
    )

    tree = ttk.Treeview(
        frame_inferior,
        columns=columnas,
        show="headings"
    )

    tree.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    # ============================================================================
    # ENCABEZADOS
    # ============================================================================

    tree.heading("id", text="ID")
    tree.heading("profesor", text="Docente")
    tree.heading("materia", text="Materia")
    tree.heading("dia", text="Día")
    tree.heading("tipo_cargo", text="Cargo")
    tree.heading("módulos", text="Módulos")
    tree.heading("curso", text="Curso")
    tree.heading("turno", text="Turno")
    tree.heading("hentrada", text="Entrada")
    tree.heading("hsalida", text="Salida")
    tree.heading("situacion_revista", text="Sit_Rev")
    tree.heading("toma_pos", text="Toma_Pos.")
    tree.heading("fecha_cese", text="Fec_Cese")
    tree.heading("activo", text="Activo")

    # ============================================================================
    # COLUMNAS
    # ============================================================================

    tree.column(
        "id",
        width=0,
        minwidth=0,
        stretch=False
    )

    tree.column("profesor", width=150)
    tree.column("materia", width=150)
    tree.column("dia", width=70)
    tree.column("tipo_cargo", width=150)
    tree.column("módulos", width=50)
    tree.column("curso", width=70)
    tree.column("turno", width=70)
    tree.column("hentrada", width=60)
    tree.column("hsalida", width=60)
    tree.column("situacion_revista", width=80)
    tree.column("toma_pos", width=80)
    tree.column("fecha_cese", width=80)
    tree.column("activo", width=50)

    # ============================================================================
    # SCROLLBARS
    # ============================================================================

    scrollbar_y = ttk.Scrollbar(
        frame_inferior,
        orient="vertical",
        command=tree.yview
    )

    scrollbar_x = ttk.Scrollbar(
        frame_inferior,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    scrollbar_y.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    scrollbar_x.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    # ============================================================================
    # CARGA DE COMBOS
    # ============================================================================

    def cargar_combos():

        nonlocal profesores_dict, materia_dict

        conn = conectar()
        cursor = conn.cursor()

        profesores_dict.clear()
        materia_dict.clear()

        profesores_dict[""] = None
        materia_dict[""] = None

        # -------------------- Profesores --------------------

        cursor.execute("""
            SELECT id_docente, apellido, nombre
            FROM profesores
            ORDER BY apellido COLLATE NOCASE, nombre COLLATE NOCASE
        """)

        for id_, apellido, nombre in cursor.fetchall():

            texto = f"{id_} - {apellido}, {nombre}"

            profesores_dict[texto] = id_

        combo_profesor["values"] = list(profesores_dict.keys())

        # -------------------- Materias --------------------

        cursor.execute("""
            SELECT id_materia, nombre
            FROM materias
            ORDER BY nombre COLLATE NOCASE
        """)

        for id_, nombre in cursor.fetchall():

            texto = f"{id_} - {nombre}"

            materia_dict[texto] = id_

        combo_materia["values"] = list(materia_dict.keys())

        conn.close()

    # ============================================================================
    # GUARDAR
    # ============================================================================

    def guardar():

        if not profesor_var.get():

            messagebox.showwarning(
                "Atención",
                "Complete todos los campos",
                parent=ventana
            )

            return

        hentrada = normalizar_hora(
            entrada_var.get()
        )

        hsalida = normalizar_hora(
            salida_var.get()
        )

        toma_pos = normalizar_fecha(
            toma_pos_var.get()
        )

        fecha_cese = normalizar_fecha(
            fecha_cese_var.get()
        )

        # ---------------- Validación horas ----------------

        if hentrada is None or hsalida is None:

            messagebox.showerror(
                "Error",
                "El formato de la hora debe ser HH:MM.",
                parent=ventana
            )

            return

        if not validar_horario(
            hentrada,
            hsalida
        ):

            messagebox.showerror(
                "Error",
                "La hora de entrada debe ser menor que la hora de salida.",
                parent=ventana
            )

            return

        # ------------- Incompatibilidad horaria -------------

        if hay_incompatibilidad_horaria(
            profesores_dict[profesor_var.get()],
            dia_var.get(),
            hentrada,
            hsalida
        ):

            messagebox.showwarning(
                "Incompatibilidad horaria",
                "El docente ya posee una asignación en ese horario.",
                parent=ventana
            )

            return

        # ------------- Fecha toma posesión ------------------

        if toma_pos is None:

            messagebox.showerror(
                "Error",
                "La fecha de toma de posesión debe tener el formato DD/MM/AAAA.",
                parent=ventana
            )

            return

        # ---------------- Fecha cese -----------------------

        if (
            fecha_cese_var.get().strip() != ""
            and fecha_cese is None
        ):

            messagebox.showerror(
                "Error",
                "La fecha de cese debe tener el formato DD/MM/AAAA.",
                parent=ventana
            )

            return

        if not validar_fecha(toma_pos):

            messagebox.showerror(
                "Error",
                "La fecha de toma de posesión no es válida.",
                parent=ventana
            )

            return

        if fecha_cese and not validar_fecha(fecha_cese):

            messagebox.showerror(
                "Error",
                "La fecha de cese no es válida.",
                parent=ventana
            )

            return

        if not validar_rango_fechas(
            toma_pos,
            fecha_cese
        ):

            messagebox.showerror(
                "Error",
                "La fecha de cese no puede ser anterior a la fecha de toma de posesión.",
                parent=ventana
            )

            return

        # ====================================================
        # GUARDAR EN BASE DE DATOS
        # ====================================================

        try:

            conn = conectar()
            cursor = conn.cursor()

            if existe_asignacion(
                profesores_dict[profesor_var.get()],
                materia_dict.get(materia_var.get()),
                dia_var.get(),
                cargo_var.get(),
                modulos_var.get(),
                curso_var.get(),
                turno_var.get(),
                hentrada,
                hsalida
            ):

                messagebox.showwarning(
                    "Asignación duplicada",
                    "Esta asignación ya se encuentra registrada.",
                    parent=ventana
                )

                conn.close()
                return

            cursor.execute("""
                INSERT INTO asignacion(
                    id_docente,
                    id_materia,
                    dia,
                    cargo,
                    modulos,
                    curso,
                    turno,
                    hentrada,
                    hsalida,
                    situacion_revista,
                    toma_pos,
                    fecha_cese,
                    activo
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profesores_dict[profesor_var.get()],
                materia_dict[materia_var.get()],
                dia_var.get(),
                cargo_var.get(),
                modulos_var.get(),
                curso_var.get(),
                turno_var.get(),
                hentrada,
                hsalida,
                situacion_var.get(),
                toma_pos,
                fecha_cese,
                activo_var.get()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "OK",
                "Asignación guardada",
                parent=ventana
            )

            cargar_tree()
            limpiar()

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e),
                parent=ventana
            )

    # ============================================================================
    # CARGAR TREEVIEW
    # ============================================================================

    def cargar_tree():

        nonlocal id_seleccionado

        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        # ------------------------------------------------------------------------
        # ORDEN PRINCIPAL:
        #
        #   1. CURSO
        #   2. APELLIDO
        #   3. NOMBRE
        #   4. MATERIA
        #
        # Esto permite visualizar primero todas las asignaciones de cada curso.
        # ------------------------------------------------------------------------

        query = """
            SELECT
                a.id_asignacion,
                p.apellido || ', ' || p.nombre AS profesor,
                IFNULL(m.nombre, '---') AS materia,
                a.dia,
                a.cargo,
                a.modulos,
                a.curso,
                a.turno,
                a.hentrada,
                a.hsalida,
                a.situacion_revista,
                a.toma_pos,
                IFNULL(a.fecha_cese, '') AS f_cese,
                CASE
                    WHEN a.activo = 1 THEN 'SÍ'
                    ELSE 'NO'
                END AS estado_activo

            FROM asignacion a

            INNER JOIN profesores p
                ON a.id_docente = p.id_docente

            LEFT JOIN materias m
                ON a.id_materia = m.id_materia

            ORDER BY
                a.curso COLLATE NOCASE ASC,
                p.apellido COLLATE NOCASE ASC,
                p.nombre COLLATE NOCASE ASC,
                m.nombre COLLATE NOCASE ASC
        """

        try:

            cursor.execute(query)

            registros = cursor.fetchall()

            for fila in registros:

                tree.insert(
                    "",
                    "end",
                    values=fila
                )

        except sqlite3.OperationalError as e:

            messagebox.showerror(
                "Error de Base de Datos",
                f"No se pudo cargar el listado:\n{e}",
                parent=ventana
            )

        finally:

            conn.close()

        # Al terminar de cargar, dejamos preparado el Treeview
        # para utilizar la búsqueda por teclado.

        hijos = tree.get_children()

        if hijos:

            tree.selection_set(hijos[0])
            tree.focus(hijos[0])
            tree.see(hijos[0])

    # ============================================================================
    # MODIFICAR REGISTRO
    # ============================================================================

    def modificar():

        nonlocal id_seleccionado

        if id_seleccionado is None:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro",
                parent=ventana
            )

            return

        id_doc = profesores_dict.get(
            profesor_var.get(),
            None
        )

        id_mat = materia_dict.get(
            materia_var.get(),
            None
        )

        conn = conectar()
        cursor = conn.cursor()

        hentrada = normalizar_hora(
            entrada_var.get()
        )

        hsalida = normalizar_hora(
            salida_var.get()
        )

        toma_pos = normalizar_fecha(
            toma_pos_var.get()
        )

        fecha_cese = normalizar_fecha(
            fecha_cese_var.get()
        )

        # ---------------- Validación horas ----------------

        if hentrada is None or hsalida is None:

            messagebox.showerror(
                "Error",
                "El formato de la hora debe ser HH:MM.",
                parent=ventana
            )

            conn.close()
            return

        if not validar_horario(
            hentrada,
            hsalida
        ):

            messagebox.showerror(
                "Error",
                "La hora de entrada debe ser menor que la hora de salida.",
                parent=ventana
            )

            conn.close()
            return

        # ---------------- Incompatibilidad ----------------

        if hay_incompatibilidad_horaria(
            id_doc,
            dia_var.get(),
            hentrada,
            hsalida,
            id_seleccionado
        ):

            messagebox.showwarning(
                "Incompatibilidad horaria",
                "El docente ya posee una asignación en ese horario.",
                parent=ventana
            )

            conn.close()
            return

        # ---------------- Validaciones fechas --------------

        if toma_pos is None:

            messagebox.showerror(
                "Error",
                "La fecha de toma de posesión no es válida (DD/MM/AAAA).",
                parent=ventana
            )

            conn.close()
            return

        if (
            fecha_cese_var.get().strip() != ""
            and fecha_cese is None
        ):

            messagebox.showerror(
                "Error",
                "La fecha de cese no es válida (DD/MM/AAAA).",
                parent=ventana
            )

            conn.close()
            return

        if not validar_fecha(toma_pos):

            messagebox.showerror(
                "Error",
                "La fecha de toma de posesión no es válida.",
                parent=ventana
            )

            conn.close()
            return

        if fecha_cese and not validar_fecha(fecha_cese):

            messagebox.showerror(
                "Error",
                "La fecha de cese no es válida.",
                parent=ventana
            )

            conn.close()
            return

        if not validar_rango_fechas(
            toma_pos,
            fecha_cese
        ):

            messagebox.showerror(
                "Error",
                "La fecha de cese no puede ser anterior a la toma de posesión.",
                parent=ventana
            )

            conn.close()
            return

        # ====================================================
        # ACTUALIZACIÓN
        # ====================================================

        try:

            cursor.execute("""
                UPDATE asignacion
                SET
                    id_docente=?,
                    id_materia=?,
                    dia=?,
                    cargo=?,
                    modulos=?,
                    curso=?,
                    turno=?,
                    hentrada=?,
                    hsalida=?,
                    situacion_revista=?,
                    toma_pos=?,
                    fecha_cese=?,
                    activo=?

                WHERE id_asignacion=?
            """, (
                id_doc,
                id_mat,
                dia_var.get(),
                cargo_var.get(),
                modulos_var.get(),
                curso_var.get(),
                turno_var.get(),
                hentrada,
                hsalida,
                situacion_var.get(),
                toma_pos,
                fecha_cese,
                activo_var.get(),
                id_seleccionado
            ))

            conn.commit()

            messagebox.showinfo(
                "OK",
                "Asignación modificada",
                parent=ventana
            )

            cargar_tree()
            limpiar()

        except sqlite3.OperationalError as e:

            messagebox.showerror(
                "Error SQL",
                f"Ocurrió un problema:\n{e}",
                parent=ventana
            )

        finally:

            conn.close()

    # ============================================================================
    # SELECCIONAR REGISTRO
    # ============================================================================

    def on_tree_select(event):

        nonlocal id_seleccionado

        seleccion = tree.selection()

        if not seleccion:
            return

        item = tree.item(
            seleccion[0]
        )

        valores = item["values"]

        if not valores:
            return

        # ID DE LA ASIGNACIÓN
        id_seleccionado = valores[0]

        # -------------------------------------------------
        # DOCENTE
        # -------------------------------------------------

        nombre_buscado = valores[1]

        encontrado = ""

        for clave in profesores_dict.keys():

            if clave.endswith(nombre_buscado):

                encontrado = clave
                break

        profesor_var.set(
            encontrado if encontrado else nombre_buscado
        )

        # -------------------------------------------------
        # MATERIA
        # -------------------------------------------------

        materia_buscada = valores[2]

        if materia_buscada != "---":

            materia_encontrada = ""

            for clave in materia_dict.keys():

                if clave.endswith(materia_buscada):

                    materia_encontrada = clave
                    break

            materia_var.set(
                materia_encontrada
                if materia_encontrada
                else materia_buscada
            )

        else:

            materia_var.set("")

        # -------------------------------------------------
        # RESTO DE CAMPOS
        # -------------------------------------------------

        dia_var.set(valores[3])
        cargo_var.set(valores[4])
        modulos_var.set(valores[5])
        curso_var.set(valores[6])
        turno_var.set(valores[7])
        entrada_var.set(valores[8])
        salida_var.set(valores[9])
        situacion_var.set(valores[10])
        toma_pos_var.set(valores[11])
        fecha_cese_var.set(valores[12])

        if valores[13] == "SÍ":
            activo_var.set(1)
        else:
            activo_var.set(0)

    tree.bind(
        "<<TreeviewSelect>>",
        on_tree_select
    )

    # ============================================================================
    # BÚSQUEDA RÁPIDA POR APELLIDO
    # ============================================================================
    #
    # IMPORTANTE:
    #
    # Aunque el Treeview está ordenado por CURSO, la búsqueda se realiza sobre
    # el APELLIDO del docente.
    #
    # Ejemplo:
    #
    #   M
    #   MA
    #   MAR
    #
    # buscará docentes cuyo apellido comience con esas letras.
    #
    # La búsqueda recorre todo el Treeview, por lo que no depende del criterio
    # de ordenamiento.
    # ============================================================================

    texto_busqueda = ""
    ultimo_tiempo_busqueda = 0

    def buscar_treeview(event):

        nonlocal texto_busqueda
        nonlocal ultimo_tiempo_busqueda

        ahora = time.time()

        # Si pasó más de un segundo,
        # comenzamos una nueva búsqueda.

        if ahora - ultimo_tiempo_busqueda > 1:

            texto_busqueda = ""

        ultimo_tiempo_busqueda = ahora

        # -------------------------------------------------
        # Ignorar teclas que no sean letras
        # -------------------------------------------------

        if not event.char or not event.char.isalpha():

            return

        texto_busqueda += event.char.lower()

        items = tree.get_children()

        if not items:
            return

        # -------------------------------------------------
        # Determinar desde dónde comenzar
        # -------------------------------------------------

        seleccion = tree.selection()

        start_index = 0

        if seleccion:

            try:

                start_index = (
                    items.index(seleccion[0]) + 1
                )

            except ValueError:

                start_index = 0

        # -------------------------------------------------
        # Buscar recorriendo todo el Treeview
        # -------------------------------------------------

        for i in range(len(items)):

            idx = (
                start_index + i
            ) % len(items)

            item = items[idx]

            valores = tree.item(
                item,
                "values"
            )

            if not valores:
                continue

            # Columna 1 = profesor
            texto_profesor = str(
                valores[1]
            ).strip().lower()

            # El Treeview muestra:
            #
            # APELLIDO, Nombre
            #
            # Por eso tomamos lo que está antes de la coma.

            apellido = texto_profesor.split(",")[0].strip()

            if apellido.startswith(
                texto_busqueda
            ):

                tree.selection_set(item)
                tree.focus(item)
                tree.see(item)

                break

    tree.bind(
        "<Key>",
        buscar_treeview
    )

    # ============================================================================
    # ELIMINAR ASIGNACIÓN
    # ============================================================================

    def eliminar():

        nonlocal id_seleccionado

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro",
                parent=ventana
            )

            return

        if not messagebox.askyesno(
            "Confirmar",
            "¿Eliminar asignación?",
            parent=ventana
        ):

            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM asignacion
            WHERE id_asignacion=?
            """,
            (id_seleccionado,)
        )

        conn.commit()
        conn.close()

        cargar_tree()
        limpiar()

    # ============================================================================
    # EXPORTAR ASIGNACIONES A PDF
    # ============================================================================

    def generar_pdf():

        curso_buscado = simpledialog.askstring(
            "Exportar a PDF",
            "Ingrese el Curso a exportar (Ej: 1° 1°, 4to 1ra) o deje vacío para TODOS:",
            parent=ventana
        )

        if curso_buscado is None:
            return

        curso_buscado = curso_buscado.strip()

        conn = conectar()
        cursor = conn.cursor()

        query = """
            SELECT
                p.apellido || ', ' || p.nombre AS profesor,
                IFNULL(m.nombre, '---') AS materia,
                a.dia,
                a.cargo,
                a.modulos,
                a.curso,
                a.turno,
                a.hentrada || ' a ' || a.hsalida AS horario,
                a.situacion_revista,
                a.toma_pos,
                IFNULL(a.fecha_cese, '') AS f_cese,
                CASE
                    WHEN a.activo = 1 THEN 'SÍ'
                    ELSE 'NO'
                END AS estado_activo

            FROM asignacion a

            INNER JOIN profesores p
                ON a.id_docente = p.id_docente

            LEFT JOIN materias m
                ON a.id_materia = m.id_materia
        """

        if curso_buscado:

            query += """
                WHERE a.curso LIKE ?
                ORDER BY
                    a.curso COLLATE NOCASE ASC,
                    p.apellido COLLATE NOCASE ASC,
                    p.nombre COLLATE NOCASE ASC
            """

            parametros = (
                f"%{curso_buscado}%",
            )

        else:

            query += """
                ORDER BY
                    a.curso COLLATE NOCASE ASC,
                    p.apellido COLLATE NOCASE ASC,
                    p.nombre COLLATE NOCASE ASC
            """

            parametros = ()

        cursor.execute(
            query,
            parametros
        )

        filas = cursor.fetchall()

        conn.close()

        if not filas:

            messagebox.showinfo(
                "Sin resultados",
                f"No se encontraron asignaciones para: '{curso_buscado}'",
                parent=ventana
            )

            return

        carpeta_destino = os.path.join(
            "reportes",
            "pdf",
            "Asignacion_Docente"
        )

        if not os.path.exists(
            carpeta_destino
        ):

            os.makedirs(
                carpeta_destino
            )

        nombre_base = (
            f"Reporte_Curso_"
            f"{curso_buscado.replace(' ', '_') if curso_buscado else 'Completo'}.pdf"
        )

        nombre_archivo = os.path.join(
            carpeta_destino,
            nombre_base
        )

        try:

            doc = SimpleDocTemplate(
                nombre_archivo,
                pagesize=landscape(A4),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            story = []

            styles = getSampleStyleSheet()

            estilo_titulo = ParagraphStyle(
                'T',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor("#2c3e50"),
                spaceAfter=4
            )

            estilo_subt = ParagraphStyle(
                'S',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#7f8c8d"),
                spaceAfter=15
            )

            estilo_celda = ParagraphStyle(
                'C',
                parent=styles['Normal'],
                fontSize=9,
                leading=11
            )

            estilo_cabecera = ParagraphStyle(
                'H',
                parent=styles['Normal'],
                fontSize=9,
                leading=11,
                textColor=colors.white,
                fontName="Helvetica-Bold"
            )

            story.append(
                Paragraph(
                    "SISTEMA ACADÉMICO - LISTADO DE ASIGNACIONES",
                    estilo_titulo
                )
            )

            txt_filtro = (
                f"Filtro: Curso '{curso_buscado}'"
                if curso_buscado
                else "Filtro: Todas las asignaciones"
            )

            story.append(
                Paragraph(
                    f"{txt_filtro} | Generado el: "
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    estilo_subt
                )
            )

            tabla_datos = [[
                Paragraph("PROFESOR", estilo_cabecera),
                Paragraph("MATERIA", estilo_cabecera),
                Paragraph("DÍA", estilo_cabecera),
                Paragraph("CARGO", estilo_cabecera),
                Paragraph("MOD.", estilo_cabecera),
                Paragraph("CURSO", estilo_cabecera),
                Paragraph("TURNO", estilo_cabecera),
                Paragraph("HORARIO", estilo_cabecera),
                Paragraph("SIT. REVISTA", estilo_cabecera),
                Paragraph("TOMA POS.", estilo_cabecera),
                Paragraph("FEC. CESE", estilo_cabecera),
                Paragraph("ACTIVO", estilo_cabecera)
            ]]

            for r in filas:

                tabla_datos.append([
                    Paragraph(str(r[0]), estilo_celda),
                    Paragraph(str(r[1]), estilo_celda),
                    Paragraph(str(r[2]), estilo_celda),
                    Paragraph(str(r[3]), estilo_celda),
                    Paragraph(str(r[4]), estilo_celda),
                    Paragraph(str(r[5]), estilo_celda),
                    Paragraph(str(r[6]), estilo_celda),
                    Paragraph(str(r[7]), estilo_celda),
                    Paragraph(str(r[8]), estilo_celda),
                    Paragraph(str(r[9]), estilo_celda),
                    Paragraph(str(r[10]), estilo_celda),
                    Paragraph(str(r[11]), estilo_celda)
                ])

            anchos = [
                135,
                110,
                50,
                75,
                40,
                45,
                50,
                80,
                75,
                60,
                55,
                50
            ]

            t = Table(
                tabla_datos,
                colWidths=anchos,
                repeatRows=1
            )

            t.setStyle(
                TableStyle([
                    (
                        'BACKGROUND',
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2c3e50")
                    ),
                    (
                        'VALIGN',
                        (0, 0),
                        (-1, -1),
                        'MIDDLE'
                    ),
                    (
                        'TOPPADDING',
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        'BOTTOMPADDING',
                        (0, 0),
                        (-1, -1),
                        5
                    ),
                    (
                        'GRID',
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#bdc3c7")
                    ),
                    (
                        'ROWBACKGROUNDS',
                        (0, 1),
                        (-1, -1),
                        [
                            colors.white,
                            colors.HexColor("#f8f9fa")
                        ]
                    )
                ])
            )

            story.append(t)

            doc.build(story)

            messagebox.showinfo(
                "Éxito",
                f"PDF creado con éxito:\n{nombre_archivo}",
                parent=ventana
            )

            os.startfile(
                nombre_archivo
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo generar el PDF:\n{e}",
                parent=ventana
            )

    # ============================================================================
    # LIMPIAR CAMPOS
    # ============================================================================

    def limpiar():

        nonlocal id_seleccionado

        id_seleccionado = None

        profesor_var.set("")
        materia_var.set("")
        dia_var.set("")
        cargo_var.set("")
        modulos_var.set("")
        curso_var.set("")
        turno_var.set("")
        entrada_var.set("")
        salida_var.set("")
        situacion_var.set("")
        toma_pos_var.set("")
        fecha_cese_var.set("")

        # Al limpiar dejamos el docente activo
        # como valor predeterminado.

        activo_var.set(1)

    # ============================================================================
    # BOTONES
    # ============================================================================

    frame_botones = ttk.Frame(
        frame_superior
    )

    frame_botones.grid(
        row=5,
        column=0,
        columnspan=6,
        pady=15
    )

    tk.Button(
        frame_botones,
        text="💾 Guardar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=guardar
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="✏ Modificar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=modificar
    ).grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="🗑 Eliminar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=eliminar
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="📄 Crear PDF",
        font=("Segoe UI Emoji", 12, "bold"),
        command=generar_pdf
    ).grid(
        row=0,
        column=3,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="🧹 Limpiar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=limpiar
    ).grid(
        row=0,
        column=4,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="❌ Cerrar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=ventana.destroy
    ).grid(
        row=0,
        column=5,
        padx=5
    )

    # ============================================================================
    # INICIO DE LA PANTALLA
    # ============================================================================

    cargar_combos()
    cargar_tree()

    centrar_ventana(ventana)

    # Dejamos el Treeview preparado para la búsqueda por teclado.
    tree.focus_set()
    