# ================================================================================
#                       MÓDULO ASIGNACIONES DOCENTES
#=================================================================================

# =============================  LIBRERÍAS =======================================
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar
from centraVent import centrar_ventana
#from backup import crear_backup
from estilos import configurar_estilos
# --------------------------------------------------------------------------------

# ====================== PANTALLA PRINCIPAL DE ASIGNACIONES ======================
def info_asignaciones():
    # -----------------  DEFINICIÓN DE LA VENTANA PRINCIPAL ----------------------
    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Asignaciones Docentes")
    ventana.geometry("1300x600")

    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=2)
    ventana.columnconfigure(0, weight=1)

    # ============================================================================
    # 🔥 VARIABLES COMODÍN (Se declaran aquí para que las usen limpiar y cargar_combos)
    # ============================================================================
    profesores_dict = {}
    materia_dict = {}

    # Variables de control de los campos
    profesor_var = tk.StringVar()
    materia_var = tk.StringVar()
    cargo_var = tk.StringVar()
    curso_var = tk.StringVar()
    turno_var = tk.StringVar() 
    entrada_var = tk.StringVar()
    salida_var = tk.StringVar() 
    situacion_var = tk.StringVar()
    toma_pos_var = tk.StringVar()
    activo_var = tk.IntVar(value=1)

    # =========================
    # FRAME SUPERIOR
    # =========================
    frame_superior = ttk.LabelFrame(ventana, text="Asignar Profesor", padding=20)
    frame_superior.grid(row=0, column=0, sticky="nsew", padx=5, pady=10)

    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # Estilos de Combobox
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))

    # =========================
    # CAMPOS DE LA INTERFAZ
    # =========================
    ttk.Label(frame_superior, text="Docente:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    combo_profesor = ttk.Combobox(frame_superior, textvariable=profesor_var, state="readonly", font=("Arial", 12))
    combo_profesor.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Materia:", font=("Arial", 12)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
    combo_materia = ttk.Combobox(frame_superior, textvariable=materia_var, state="readonly", font=("Arial", 12))
    combo_materia.grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Tipo_Cargo:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    combo_cargo = ttk.Combobox(frame_superior, textvariable=cargo_var, 
    values=["","Director", "ViceDirector", "Secretario", "Profesor", "EMATP", "Enc.Laboratorio", "Jefe Dpto", "Preceptor", "Bibliotecario", "Auxiliar", "Taller"], state="readonly", font=("Arial", 12))
    combo_cargo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Curso:", font=("Arial", 12)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=curso_var, font=("Arial", 12), width=20).grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Turno:", font=("Arial", 12)).grid(row=1, column=4, sticky="e", padx=5, pady=5)
    combo_turno = ttk.Combobox(frame_superior, textvariable=turno_var, state="readonly", font=("Arial", 12), values=["","Mañana", "Tarde", "Vespertino", "Noche"])
    combo_turno.grid(row=1, column=5, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Hora Entrada:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=entrada_var, font=("Arial", 12)).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
    
    ttk.Label(frame_superior, text="Hora Salida:", font=("Arial", 12)).grid(row=2, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=salida_var, font=("Arial", 12)).grid(row=2, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Situación Revista:", font=("Arial", 12)).grid(row=2, column=4, sticky="e", padx=5, pady=5)
    combo_situacion = ttk.Combobox(frame_superior, textvariable=situacion_var,
    values=["","Titular", "Provisorio", "Suplente", "Interino"], state="readonly", font=("Arial", 12)) 
    combo_situacion.grid(row=2, column=5, padx=5, pady=5)

    ttk.Label(frame_superior, text="Toma de Posición:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=toma_pos_var, font=("Arial", 12)).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    # Checkbutton grande para el Estado Activo
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
    chk_activo.grid(row=3, column=2, columnspan=2, sticky="w", padx=5, pady=5)

    # =========================
    # TREEVIEW (Listado inferior)
    # =========================
    frame_inferior = ttk.LabelFrame(ventana, text="Listado Asignaciones", padding=10)
    frame_inferior.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    columnas = ("id", "profesor", "materia", "tipo_cargo", "curso", "turno", "hentrada", "hsalida", "situacion_revista", "toma_pos","activo")

    tree = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")
    tree.heading("id", text="ID")
    tree.heading("profesor", text="PROFESOR")
    tree.heading("materia", text="MATERIA")
    tree.heading("tipo_cargo", text="TIPO DE CARGO")
    tree.heading("curso", text="CURSO")
    tree.heading("turno", text="TURNO")
    tree.heading("hentrada", text="HORA ENTRADA")
    tree.heading("hsalida", text="HORA SALIDA")
    tree.heading("situacion_revista", text="SIT_REVISTA")
    tree.heading("toma_pos", text="TOMA POS.")
    tree.heading("activo", text="ACTIVO")

    tree.column("id", width=0, minwidth=0, stretch=False)
    tree.column("profesor", width=150)
    tree.column("materia", width=150)
    tree.column("tipo_cargo", width=150)
    tree.column("curso", width=50)
    tree.column("turno", width=50)
    tree.column("hentrada", width=70)
    tree.column("hsalida", width=70)
    tree.column("situacion_revista", width=70)
    tree.column("toma_pos", width=50)
    tree.column("activo", width=5)

    scrollbar_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns")

    # ============================================================================
    # 🔥 FUNCIONES INTERNAS (Acomodadas con 'nonlocal' para evitar NameError)
    # ============================================================================
    def cargar_combos():
        # 'nonlocal' le dice a Python que use los diccionarios declarados arriba
        nonlocal profesores_dict, materia_dict
        
        conn = conectar()
        cursor = conn.cursor()

        profesores_dict.clear()
        materia_dict.clear()
        profesores_dict[""] = None
        materia_dict[""] = None

        # Profesores (Corregido: Cambié id_docente por id_profesor según tu tabla)
        cursor.execute("SELECT id_docente, apellido, nombre FROM profesores")
        for id_, apellido, nombre in cursor.fetchall():
            texto = f"{id_} - {apellido}, {nombre}"
            profesores_dict[texto] = id_

        combo_profesor["values"] = list(profesores_dict.keys())

        # Materias
        cursor.execute("SELECT id_materia, nombre FROM materias")
        for id_, nombre in cursor.fetchall():
            texto = f"{id_} - {nombre}"
            materia_dict[texto] = id_

        combo_materia["values"] = list(materia_dict.keys())

        conn.close()

    def limpiar():
        profesor_var.set("")
        materia_var.set("")
        cargo_var.set("")
        curso_var.set("")  
        turno_var.set("")
        entrada_var.set("") 
        salida_var.set("")
        situacion_var.set("")
        toma_pos_var.set("")
        activo_var.set(1) # Resetea el checkbox tildado por defecto

    # ===============================================================================
    #                                 BOTONES
    # ===============================================================================
    frame_botones = ttk.Frame(frame_superior)
    frame_botones.grid(row=4, column=0, columnspan=6, pady=15) # Ampliado el columnspan a 6 para centrar bien

    ttk.Button(frame_botones, text="💾 Guardar", command=lambda: print("Guardar")).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="✏ Modificar", command=lambda: print("Modificar")).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="🗑 Eliminar", command=lambda: print("Eliminar")).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="🧹 Limpiar", command=limpiar).grid(row=0, column=3, padx=5)
    ttk.Button(frame_botones, text="❌ Cerrar", command=ventana.destroy).grid(row=0, column=4, padx=5)

    # =========================
    # INICIO DE LA PANTALLA
    # =========================
    cargar_combos() # Ahora se ejecuta perfectamente sin errores
    centrar_ventana(ventana)