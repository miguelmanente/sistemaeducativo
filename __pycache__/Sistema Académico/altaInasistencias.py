import tkinter as tk
from tkinter import ttk
from database import conectar


def abrir_inasistencias():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Inasistencias")
    ventana.state("zoomed")

    # ===================== VARIABLES =====================
    docentes_dict = {}

    # ===================== FUNCIONES =====================

    def cargar_docentes():
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id_docente, apellido, nombre
            FROM profesores
            ORDER BY apellido, nombre
        """)

        datos = cur.fetchall()

        lista = []
        for idd, ape, nom in datos:
            nombre = f"{ape} {nom}"
            docentes_dict[nombre] = idd
            lista.append(nombre)

        cmb_docente["values"] = lista
    
    # ========================  Seleccion de docente ====================================
    def on_profesor_seleccionado(event):
        cargar_tabla()
    # -----------------------------------------------------------------------------------

    def cargar_tabla():
        nombre = cmb_docente.get()
        if not nombre:
            return

        id_docente = docentes_dict[nombre]

        conn = conectar()
        cur = conn.cursor()

        for i in tree.get_children():
            tree.delete(i)

        cur.execute("""
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
        """, (id_docente,))

        for fila in cur.fetchall():
            tree.insert("", "end", values=fila)
    
    # ------------------------------------------------------------------------------------

    # ===========================  Fila seleccionada =======================================
    def obtener_fila():
        seleccion = tree.focus()
        if not seleccion:
            return None
        return tree.item(seleccion)["values"]
    # --------------------------------------------------------------------------------------
    
    def agregar():
        nombre = cmb_docente.get()
        if nombre == "":
            return

        id_docente = docentes_dict[nombre]

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO inasistencia
            (id_docente, fecha_desde, fecha_hasta, motivo, observacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            id_docente,
            ent_desde.get(),
            ent_hasta.get(),
            cmb_motivo.get(),
            ent_obs.get()
        ))

        conn.commit()
        cargar_tabla()
    # ------------------------------------------------------------------------------------

    # ===============================Modificar filas  ====================================

    def modificar_inasistencia():
        fila = tree.focus()
        if not fila:
            return

        valores = tree.item(fila)["values"]

        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            UPDATE inasistencia
            SET fecha_desde = ?,
                fecha_hasta = ?,
                motivo = ?,
                observacion = ?
            WHERE id_docente = ? AND fecha_desde = ?
        """, (
            ent_desde.get(),
            ent_hasta.get(),
            cmb_motivo.get(),
            ent_obs.get(),
            docentes_dict[cmb_docente.get()],
            valores[1]  # fecha_desde original
        ))

        
        conn.commit()
        cargar_tabla()
    # ------------------------------------------------------------------------------------

    # ============================  LIMPIAR CAMPOS ========================================
    def limpiar():
        cmb_docente.delete("")
        ent_desde.delete(0, tk.END)
        ent_hasta.delete(0, tk.END)
        ent_obs.delete(0, tk.END)
        cmb_motivo.set("")
    # -------------------------------------------------------------------------------------


    # ========================= PANTALLA PRINCIPAL ========================================

    frame_top = ttk.Frame(ventana)
    frame_top.pack(fill="x", padx=10, pady=10)
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))

    # 1. Combos de Selección
    ttk.Label(frame_top, text="Docente:",font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    cmb_docente = ttk.Combobox(frame_top, font=("Arial", 12), state="readonly", width=40)
    cmb_docente.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    
    
     # 2. Fechas (Desde / Hasta) y Motivos
    ttk.Label(frame_top, text="Fecha Desde:",font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    ent_desde = ttk.Entry(frame_top, font=("Arial", 12)) 
    ent_desde.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    #txt_fecha_desde.insert(0, "DD/MM/AAAA") 

    ttk.Label(frame_top, text="Fecha Hasta:",font=("Arial", 12)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
    ent_hasta = ttk.Entry(frame_top, font=("Arial", 12)) 
    ent_hasta.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
    #txt_fecha_hasta.insert(0, "DD/MM/AAAA") 

    # Desplazamos el motivo a una nueva fila (Fila 2) para que no se amontone
    ttk.Label(frame_top, text="Motivo / Licencia:", font=("Arial",12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    motivos_lista = ["","Licencia Médica", "ART", "Estudio", "Injustificada", "Maternidad", "Gremial", "Razones Particulares", "Fallecimiento"]
    cmb_motivo = ttk.Combobox(frame_top,font=("Arial", 12), state="readonly", values=motivos_lista)
    cmb_motivo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # =========================== OBSERVACIONES ==========================
    ttk.Label(frame_top, text="Observación", font=("Arial", 12)).grid(row=2, column=2)
    ent_obs = ttk.Entry(frame_top, font=("Arial", 12))
    ent_obs.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
    # =================================================================


    # ===================== BOTONES =====================

    btn_frame = ttk.Frame(frame_top)
    btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

    ttk.Button(btn_frame, text="Agregar", command=agregar).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Limpiar", command=limpiar).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Modificar", command=modificar_inasistencia).pack(side="left", padx=5)

    # ===================== TABLA =====================

    frame_bottom = ttk.Frame(ventana)
    frame_bottom.pack(fill="both", expand=True)

    columnas = (
        "docente",
        "desde",
        "hasta",
        "motivo",
        "observacion"
    )

    tree = ttk.Treeview(frame_bottom, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(fill="both", expand=True)

    # ===================== INIT =====================
    cmb_docente.bind("<<ComboboxSelected>>", on_profesor_seleccionado)
    cargar_docentes()