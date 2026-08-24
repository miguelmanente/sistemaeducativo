# ============================================================
# SISTEMA DE GESTIÓN EDUCATIVA
# Resumen Anual de Inasistencias
# ============================================================

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from database import conectar
from pprint import pprint
from negocio.motor_inasistencias import resumen_docente

# ============================================================
# FRAME SUPERIOR
# ============================================================

def crear_frame_superior(ventana):

    frame_superior = ttk.LabelFrame(
        ventana,
        text="Resumen del Docente"
    )

    frame_superior.pack(
        fill="x",
        padx=10,
        pady=10
    )

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    docente_var = tk.StringVar()
    anio_actual = datetime.now().year
    anio_var = tk.StringVar(value=str(anio_actual))

    # --------------------------------------------------------
    # Docente
    # --------------------------------------------------------

    ttk.Label(
        frame_superior,
        text="Docente:"
    ).grid(
        row=0,
        column=0,
        padx=5,
        pady=8,
        sticky="e"
    )

    combo_docente = ttk.Combobox(
        frame_superior,
        textvariable=docente_var,
        width=45,
        state="readonly"
    )

    combo_docente.grid(
        row=0,
        column=1,
        padx=5,
        pady=8,
        sticky="w"
    )

    # --------------------------------------------------------
    # Año
    # --------------------------------------------------------

    ttk.Label(
        frame_superior,
        text="Año:"
    ).grid(
        row=0,
        column=2,
        padx=15,
        pady=8,
        sticky="e"
    )

    combo_anio = ttk.Combobox(
        frame_superior,
        textvariable=anio_var,
        width=10,
        state="readonly",
        values=[str(anio_actual-1), str(anio_actual), str(anio_actual+1)]
    )

    combo_anio.grid(
        row=0,
        column=3,
        padx=5,
        pady=8,
        sticky="w"
    )

    # --------------------------------------------------------
    # Buscar
    # --------------------------------------------------------

    boton_buscar = ttk.Button(
        frame_superior,
        text="Buscar"
    )

    boton_buscar.grid(
        row=0,
        column=4,
        padx=20,
        pady=8
    )

    return docente_var, anio_var, combo_docente, boton_buscar
# -----------------------------------------------------------------------------------

# ============================================================
# CARGAR DOCENTES
# ============================================================
def cargar_docentes(combo_docente):

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id_docente,
            apellido,
            nombre
        FROM profesores
        ORDER BY apellido, nombre
    """)

    datos = cur.fetchall()

    docentes_dict = {}
    lista = []

    for id_docente, apellido, nombre in datos:

        texto = f"{apellido} {nombre}"

        docentes_dict[texto] = id_docente

        lista.append(texto)

    combo_docente["values"] = lista

    conn.close()

    return docentes_dict
#------------------------------------------------------------------------------------

# ============================================================
# BUSCAR RESUMEN
# ============================================================
def buscar_resumen(
        docente_var,
        anio_var,
        docentes_dict,
        apellido_var,
        nombre_var,
        dni_var,
        cuil_var,
        tree_cargos,
        tree_modulos,
        tree_licencias
):

    nombre = docente_var.get()

    if not nombre:
        print("Debe seleccionar un docente.")
        return

    id_docente = docentes_dict[nombre]

    anio = int(anio_var.get())

    resumen = resumen_docente(id_docente, anio)

    # -------------------------------
    # Mostrar datos del docente
    # -------------------------------

    docente = resumen["docente"]

    apellido_var.set(docente["apellido"])
    nombre_var.set(docente["nombre"])
    dni_var.set(docente["dni"])
    cuil_var.set(docente["cuil"])

    mostrar_cargos(tree_cargos, resumen)
    mostrar_modulos(tree_modulos, resumen)
    mostrar_inasistencias(tree_licencias, resumen)
    
# -----------------------------------------------------------------------------------

# ============================================================
# MOSTRAR CARGOS
# ============================================================
def mostrar_cargos(tree_cargos, resumen):

    # Borrar contenido anterior
    tree_cargos.delete(*tree_cargos.get_children())

    # Agregar cargos
    for cargo in resumen["cargos"]:

        tree_cargos.insert(
            "",
            "end",
            values=(
                cargo["cargo"],
                cargo["situacion_revista"],
                cargo["dias_ciclo"],
                cargo["dias_perdidos"],
                cargo["dias_trabajados"]
            )
        )
# -------------------------------------------------------------------------------

# ============================================================
# MOSTRAR MODULOS
# ============================================================
def mostrar_modulos(tree_modulos, resumen):

    # Borrar contenido anterior
    tree_modulos.delete(*tree_modulos.get_children())

    # Agregar módulos
    for modulo in resumen["modulos"]:

        tree_modulos.insert(
            "",
            "end",
            values=(
                modulo["materia"],
                modulo["curso"],
                modulo["situacion_revista"],
                modulo["modulos_ciclo"],
                modulo["modulos_perdidos"],
                modulo["modulos_trabajados"]
            )
        )
# -------------------------------------------------------------------------------

# ============================================================
# MOSTRAR INASISTENCIAS
# ============================================================
def mostrar_inasistencias(tree_licencias, resumen):

    tree_licencias.delete(*tree_licencias.get_children())

    for licencia in resumen["inasistencias"]:

        tree_licencias.insert(
            "",
            "end",
            values=(
                licencia["fecha_desde"],
                licencia["fecha_hasta"],
                licencia["motivo"],
                licencia["observacion"]
            )
        )
# -----------------------------------------------------------------------------------------------

# ========================== VENTANA RESUMEN INASISTENCIAS ==========================
def ventana_resumen():

    ventana = tk.Toplevel()

    ventana.title("Resumen Anual de Inasistencias")
    ventana.state('zoomed')
    #ventana.geometry("1200x750")

    ventana.resizable(True, True)

    # ========================================================
    # FRAME SUPERIOR
    # ========================================================

    docente_var, anio_var, combo_docente, boton_buscar = crear_frame_superior(ventana)

    docentes_dict = cargar_docentes(combo_docente)

    boton_buscar.config(
        command=lambda: buscar_resumen(
            docente_var,
            anio_var,
            docentes_dict,
            apellido_var,
            nombre_var,
            dni_var,
            cuil_var,
            tree_cargos,
            tree_modulos,
            tree_licencias
        )
    )

    # ========================================================
    # FRAME DATOS DOCENTE
    # ========================================================

    frame_docente = ttk.LabelFrame(
        ventana,
        text="Datos del Docente"
    )

    frame_docente.pack(
        fill="x",
        padx=10,
        pady=5
    )

    # --------------------------------------------------------
    # Variables
    # --------------------------------------------------------

    apellido_var = tk.StringVar()
    nombre_var = tk.StringVar()
    dni_var = tk.StringVar()
    cuil_var = tk.StringVar()

    # --------------------------------------------------------
    # Etiquetas
    # --------------------------------------------------------

    ttk.Label(frame_docente, text="Apellido:").grid(
        row=0, column=0, padx=5, pady=5, sticky="e"
    )

    ttk.Label(frame_docente, textvariable=apellido_var).grid(
        row=0, column=1, padx=5, pady=5, sticky="w"
    )

    ttk.Label(frame_docente, text="Nombre:").grid(
        row=0, column=2, padx=20, pady=5, sticky="e"
    )

    ttk.Label(frame_docente, textvariable=nombre_var).grid(
        row=0, column=3, padx=5, pady=5, sticky="w"
    )

    ttk.Label(frame_docente, text="DNI:").grid(
        row=1, column=0, padx=5, pady=5, sticky="e"
    )

    ttk.Label(frame_docente, textvariable=dni_var).grid(
        row=1, column=1, padx=5, pady=5, sticky="w"
    )

    ttk.Label(frame_docente, text="CUIL:").grid(
        row=1, column=2, padx=20, pady=5, sticky="e"
    )

    ttk.Label(frame_docente, textvariable=cuil_var).grid(
        row=1, column=3, padx=5, pady=5, sticky="w"
    )

    # ========================================================
    # BOTON CERRAR
    # ========================================================
    ttk.Button(
        frame_docente,
        text="Cerrar",
        command=ventana.destroy
    ).grid(
        row=0,
        column=4,
        rowspan=2,
        padx=20,
        pady=5,
        sticky="e"
    )
    # ========================================================
    # FRAME CARGOS
    # ========================================================

    frame_cargos = ttk.LabelFrame(
            ventana,
            text="Cargos"
        )

    frame_cargos.pack(
        fill="both",
        expand=False,
        padx=10,
        pady=5
    )

    tree_cargos = ttk.Treeview(
        frame_cargos,
        columns=(
            "cargo",
            "revista",
            "ciclo",
            "perdidos",
            "trabajados"
        ),
        show="headings",
        height=4
    )

    tree_cargos.heading("cargo", text="Cargo")
    tree_cargos.heading("revista", text="Situación")
    tree_cargos.heading("ciclo", text="Días Ciclo")
    tree_cargos.heading("perdidos", text="Perdidos")
    tree_cargos.heading("trabajados", text="Trabajados")

    tree_cargos.column("cargo", width=180)
    tree_cargos.column("revista", width=100, anchor="center")
    tree_cargos.column("ciclo", width=90, anchor="center")
    tree_cargos.column("perdidos", width=90, anchor="center")
    tree_cargos.column("trabajados", width=90, anchor="center")

    tree_cargos.pack(
        fill="x",
        padx=5,
        pady=5
    )

    scroll_cargos = ttk.Scrollbar(
        frame_cargos,
        orient="vertical",
        command=tree_cargos.yview
    )

    tree_cargos.configure(
        yscrollcommand=scroll_cargos.set
    )

    scroll_cargos.pack(
        side="right",
        fill="y"
    )

    tree_cargos.pack(
        side="left",
        fill="both",
        expand=True
    )
    #---------------------------------------------------------------------------

    # ========================================================
    # FRAME MODULOS
    # ========================================================

    frame_modulos = ttk.LabelFrame(
        ventana,
        text="Materias"
    )

    frame_modulos.pack(
        fill="both",
        expand=False,
        padx=10,
        pady=5
    )

    tree_modulos = ttk.Treeview(
        frame_modulos,
        columns=(
            "materia",
            "curso",
            "revista",
            "ciclo",
            "perdidos",
            "dictados"
        ),
        show="headings",
        height=5
    )

    tree_modulos.heading("materia", text="Materia")
    tree_modulos.heading("curso", text="Curso")
    tree_modulos.heading("revista", text="Situación")
    tree_modulos.heading("ciclo", text="Módulos Ciclo")
    tree_modulos.heading("perdidos", text="Perdidos")
    tree_modulos.heading("dictados", text="Dictados")

    tree_modulos.column("materia", width=220)
    tree_modulos.column("curso", width=70, anchor="center")
    tree_modulos.column("revista", width=100, anchor="center")
    tree_modulos.column("ciclo", width=100, anchor="center")
    tree_modulos.column("perdidos", width=90, anchor="center")
    tree_modulos.column("dictados", width=90, anchor="center")

    tree_modulos.pack(
        fill="x",
        padx=5,
        pady=5
    )

    scroll_modulos = ttk.Scrollbar(
        frame_modulos,
        orient="vertical",
        command=tree_modulos.yview
    )

    tree_modulos.configure(
        yscrollcommand=scroll_modulos.set
    )

    scroll_modulos.pack(
        side="right",
        fill="y"
    )

    tree_modulos.pack(
        side="left",
        fill="both",
        expand=True
    )
    # --------------------------------------------------------------------------

    # ========================================================
    # FRAME INASISTENCIAS
    # ========================================================

    frame_licencias = ttk.LabelFrame(
        ventana,
        text="Detalle de Inasistencias"
    )

    frame_licencias.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    tree_licencias = ttk.Treeview(
        frame_licencias,
        columns=(
            "desde",
            "hasta",
            "motivo",
            "observacion"
        ),
        show="headings",
        height=8
    )

    tree_licencias.heading("desde", text="Desde")
    tree_licencias.heading("hasta", text="Hasta")
    tree_licencias.heading("motivo", text="Motivo")
    tree_licencias.heading("observacion", text="Observación")

    tree_licencias.column("desde", width=90, anchor="center")
    tree_licencias.column("hasta", width=90, anchor="center")
    tree_licencias.column("motivo", width=220)
    tree_licencias.column("observacion", width=350)

    tree_licencias.pack(
        fill="both",
        expand=True,
        padx=5,
        pady=5
    )

    scroll_licencias = ttk.Scrollbar(
        frame_licencias,
        orient="vertical",
        command=tree_licencias.yview
    )

    tree_licencias.configure(
        yscrollcommand=scroll_licencias.set
    )

    scroll_licencias.pack(
        side="right",
        fill="y"
    )

    tree_licencias.pack(
        side="left",
        fill="both",
        expand=True
    )





