import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from database import conectar
from estilos import configurar_estilos
import sqlite3 # Asumiendo que usás SQLite

def abrir_inasistencia_docente():
    """
    Función principal para la gestión de inasistencias.
    """
    ventana_inasistencia = tk.Toplevel()
    ventana_inasistencia.title("Sistema de Gestión Educativa - Inasistencias")
    #ventana_inasistencia.geometry("1100x650")
    ventana_inasistencia.state('zoomed')
    
    # -------------------------------------------------------------------------
    # CONEXIÓN Y LÓGICA DE BASE DE DATOS (FUNCIONES INTERNAS)
    # -------------------------------------------------------------------------
    #def conectar_db():
        # Cambiá "mi_base_de_datos.db" por el nombre real de tu archivo de base de datos
       # return sqlite3.connect("mi_base_de_datos.db")

    def cargar_docentes():
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_docente, apellido, nombre
            FROM profesores
            ORDER BY apellido, nombre
        """)

        datos = cursor.fetchall()

        global docentes_dict, lista_docentes

        docentes_dict = {}
        lista_docentes = []

        for id_doc, ape, nom in datos:
            nombre_completo = f"{ape} {nom}"
            docentes_dict[nombre_completo] = id_doc
            lista_docentes.append(nombre_completo)

        cmb_docente['values'] = lista_docentes

    def on_profesor_seleccionado(event):
        conn = conectar()
        cursor = conn.cursor()

        nombre = cmb_docente.get()
        id_docente = docentes_dict.get(nombre)

        if not id_docente:
            return

        cargar_inasistencias_completo(id_docente)


    #================ CARGA INASISTENSIAS ============================================
    def cargar_inasistencias_completo(id_docente):
        conn = conectar()
        cursor = conn.cursor()

        # limpiar tabla
        for item in tabla.get_children():
            tabla.delete(item)

        cursor.execute("""
            SELECT
                p.apellido || ' ' || p.nombre AS docente,
                COALESCE(m.nombre, '') AS materia,
                a.cargo,
                a.modulos,
                a.curso,
                a.situacion_revista,

                i.fecha_desde,
                i.fecha_hasta,
                i.motivo,
                '',
                '',
                i.observacion

            FROM asignacion a
            INNER JOIN profesores p ON a.id_docente = p.id_docente
            LEFT JOIN materias m ON a.id_materia = m.id_materia
            LEFT JOIN inasistencia i ON i.id_docente = a.id_docente

            WHERE a.id_docente = ?
            ORDER BY i.fecha_desde DESC
        """, (id_docente,))

        datos = cursor.fetchall()

        for fila in datos:
            tabla.insert("", "end", values=fila)
    # --------------------------------------------------------------------------------

    # ========================== Agregar Inasistencias ===============================
    def agregar_inasistencia():
        conn = conectar()
        cursor = conn.cursor()

        nombre = cmb_docente.get()
        id_docente = docentes_dict.get(nombre)

        cursor.execute("""
            INSERT INTO inasistencia
            (id_docente, fecha_desde, fecha_hasta, motivo, observacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            id_docente,
            txt_fecha_desde.get(),
            txt_fecha_hasta.get(),
            cmb_motivo.get(),
            txt_observacion.get()
        ))

        conn.commit()
        cargar_inasistencias_completo(id_docente)
    # --------------------------------------------------------------------------------

    #======================== Exportar a PDF =========================================
    def generar_pdf():
        from reportlab.pdfgen import canvas

        nombre = cmb_docente.get()
        id_docente = docentes_dict.get(nombre)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT fecha_desde, fecha_hasta, motivo, observacion
            FROM inasistencia
            WHERE id_docente = ?
        """, (id_docente,))

        datos = cursor.fetchall()

        c = canvas.Canvas("inasistencias.pdf")

        y = 800
        c.drawString(200, 820, f"INASISTENCIAS DE {nombre}")

        for d in datos:
            texto = f"{d[0]} - {d[1]} | {d[2]} | {d[3]}"
            c.drawString(50, y, texto)
            y -= 20

        c.save()
    #---------------------------------------------------------------------------------

    
    # -------------------------------------------------------------------------
    # ZONA SUPERIOR: FORMULARIO Y BOTONES
    # -------------------------------------------------------------------------
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    frame_superior.option_add("*TCombobox*Listbox.font", ("Arial", 12))
    
    frame_superior = ttk.LabelFrame(ventana_inasistencia, text=" Gestión de Inasistencias y Datos de Asignación ")
    frame_superior.pack(side="top", fill="x", padx=10, pady=5)
    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # 1. Combos de Selección
    ttk.Label(frame_superior, text="Docente:",font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    cmb_docente = ttk.Combobox(frame_superior, font=("Arial", 12), state="readonly")
    cmb_docente.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    # Enlazamos el evento de selección a nuestra función interna
    cmb_docente.bind("<<ComboboxSelected>>", on_profesor_seleccionado)
    
    ttk.Label(frame_superior, text="Cargo / Materia:",font=("Arial", 12)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
    cmb_asignacion = ttk.Combobox(frame_superior, font=("Arial", 12), state="readonly")
    cmb_asignacion.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

   # 2. Fechas (Desde / Hasta) y Motivos
    ttk.Label(frame_superior, text="Fecha Desde:",font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    txt_fecha_desde = ttk.Entry(frame_superior, font=("Arial", 12)) 
    txt_fecha_desde.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    #txt_fecha_desde.insert(0, "DD/MM/AAAA") 

    ttk.Label(frame_superior, text="Fecha Hasta:",font=("Arial", 12)).grid(row=1, column=2, padx=5, pady=5, sticky="e")
    txt_fecha_hasta = ttk.Entry(frame_superior, font=("Arial", 12)) 
    txt_fecha_hasta.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
    #txt_fecha_hasta.insert(0, "DD/MM/AAAA") 

    # Desplazamos el motivo a una nueva fila (Fila 2) para que no se amontone
    ttk.Label(frame_superior, text="Motivo / Licencia:", font=("Arial",12)).grid(row=2, column=0, padx=5, pady=5, sticky="e")
    motivos_lista = ["","Licencia Médica", "ART", "Estudio", "Injustificada", "Maternidad", "Gremial", "Razones Particulares", "Fallecimiento"]
    cmb_motivo = ttk.Combobox(frame_superior,font=("Arial", 12), state="readonly", values=motivos_lista)
    cmb_motivo.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

      # =========================== OBSERVACIONES ==========================
    ttk.Label(frame_superior, text="Observación", font=("Arial", 12)).grid(row=2, column=2)
    txt_observacion = ttk.Entry(frame_superior, font=("Arial", 12))
    txt_observacion.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
    # =================================================================

    # -------------------------------------------------------------------------
    # BOTONES DE ACCIÓN Y RESTO DE LA INTERFAZ
    # -------------------------------------------------------------------------
    frame_botones = tk.Frame(frame_superior)
    frame_botones.grid(row=3, column=0, columnspan=4, pady=10)

    # (Mantenemos los mismos botones del diseño anterior...)
    btn_agregar = tk.Button(frame_botones, text="💾 Agregar",font=("Segoe UI Emoji", 14, "bold"),command=agregar_inasistencia)
    btn_agregar.pack(side="left", padx=5)
    btn_modificar = tk.Button(frame_botones, text="✏ Modificar",font=("Segoe UI Emoji", 14, "bold"))
    btn_modificar.pack(side="left", padx=5)
    btn_eliminar = tk.Button(frame_botones, text="🗑 Eliminar",font=("Segoe UI Emoji", 14, "bold"))
    btn_eliminar.pack(side="left", padx=5)
    
    def limpiar_campos():
        cmb_docente.set('')
        cmb_asignacion.set('') # Vacía las opciones del segundo combo
        cmb_asignacion.set('')
        txt_fecha_desde.delete(0, tk.END)
        txt_fecha_hasta.insert('')
        cmb_motivo.set('')
        txt_observacion('')

    btn_limpiar = tk.Button(frame_botones, text="🧹 Limpiar",font=("Segoe UI Emoji", 14, "bold"), command=limpiar_campos)
    btn_limpiar.pack(side="left", padx=5)
    
    btn_pdf = tk.Button(frame_botones, text="📄 Generar PDF",font=("Segoe UI Emoji", 14, "bold"))
    btn_pdf.pack(side="left", padx=5)
    btn_cerrar = tk.Button(frame_botones, text="❌ Cerrar",font=("Segoe UI Emoji", 14, "bold"), command=ventana_inasistencia.destroy)
    btn_cerrar.pack(side="left", padx=5)

    # -------------------------------------------------------------------------
    # ZONA INFERIOR: TREEVIEW (REPORTE HISTÓRICO)
    # -------------------------------------------------------------------------
    frame_inferior = ttk.LabelFrame(ventana_inasistencia, text=" Historial de Inasistencias y Resumen de Carga Horaria ")
    frame_inferior.pack(side="bottom", fill="both", expand=True, padx=10, pady=5)
    frame_inferior.columnconfigure(0, weight=1)
    frame_inferior.rowconfigure(0, weight=1)

    columnas = (
        "apellido_nombre",
        "materia",
        "cargo",
        "modulos",
        "curso",
        "situacion_revista",
        "f_desde",
        "f_hasta",
        "motivo",
        "tot_dias_trab",
        "cant_inasist",
        "observacion"
    )

    tabla = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    
    # (Configuración de encabezados y anchos igual al diseño anterior...)
    tabla.heading("apellido_nombre", text="Apellido y Nombres")
    tabla.heading("materia", text="Materia")
    tabla.heading("cargo", text="Cargo")
    tabla.heading("modulos", text="Módulos")
    tabla.heading("curso", text="Curso")
    tabla.heading("situacion_revista", text="Sit. Revista")
    tabla.heading("f_desde", text="Desde")
    tabla.heading("f_hasta", text="Hasta")
    tabla.heading("motivo", text="Motivo")
    tabla.heading("tot_dias_trab", text="Días Trab.")
    tabla.heading("cant_inasist", text="Inasist.")
    tabla.heading("observacion", text="Observación")

    tabla.column("apellido_nombre", width=160)
    tabla.column("materia", width=100)
    tabla.column("cargo", width=100)
    tabla.column("modulos", width=60, anchor="center")
    tabla.column("curso", width=60, anchor="center")
    tabla.column("situacion_revista", width=100, anchor="center")
    tabla.column("f_desde", width=90, anchor="w")
    tabla.column("f_hasta", width=90, anchor="w")
    tabla.column("motivo", width=120)
    tabla.column("tot_dias_trab", width=80, anchor="center")
    tabla.column("cant_inasist", width=80, anchor="center")
    tabla.column("observacion", width=200, anchor="w")
  
    tabla.grid(row=0, column=0, sticky="nsew")
    scroll_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tabla.yview)
    scroll_y.grid(row=0, column=1, sticky="ns")
    tabla.configure(yscrollcommand=scroll_y.set)

    # -------------------------------------------------------------------------
    # CARGA INICIAL DE DATOS
    # -------------------------------------------------------------------------
    cargar_docentes()
    configurar_estilos()