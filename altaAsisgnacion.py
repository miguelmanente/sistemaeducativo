# ================================================================================
#                       MÓDULO ASIGNACIONES DOCENTES
#=================================================================================

# =============================  LIBRERÍAS =======================================
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import conectar
from centraVent import centrar_ventana
#from backup import crear_backup
from estilos import configurar_estilos

# Importaciones necesarias de ReportLab para el PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
# --------------------------------------------------------------------------------

# ====================== PANTALLA PRINCIPAL DE ASIGNACIONES ======================
def info_asignaciones():
    # -----------------  DEFINICIÓN DE LA VENTANA PRINCIPAL ----------------------
    ventana = tk.Toplevel()
    configurar_estilos()
    ventana.title("Asignaciones Docentes")
    #ventana.geometry("1300x600")
    ventana.state('zoomed')

    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=2)
    ventana.columnconfigure(0, weight=1)

    # ============================================================================
    # 🔥 VARIABLES COMODÍN (Se declaran aquí para que las usen limpiar y cargar_combos)
    # ============================================================================
 
    # Variables de control de los campos
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

    ttk.Label(frame_superior, text="Día:", font=("Arial", 12)).grid(row=0, column=4, sticky="e", padx=5, pady=5)
    combo_dia = ttk.Combobox(frame_superior, textvariable=dia_var,
    values=["","Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"], state="readonly", font=("Arial", 12))
    combo_dia.grid(row=0, column=5, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Tipo_Cargo:", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    combo_cargo = ttk.Combobox(frame_superior, textvariable=cargo_var, 
    values=["","Director", "ViceDirector", "Secretario", "Profesor", "EMATP", "Enc.Laboratorio", "Jefe Dpto", "Preceptor", "Bibliotecario", "Auxiliar", "Taller"], state="readonly", font=("Arial", 12))
    combo_cargo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Módulos:", font=("Arial", 12)).grid(row=1, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=modulos_var, font=("Arial", 12), width=20).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
    
    ttk.Label(frame_superior, text="Curso:", font=("Arial", 12)).grid(row=1, column=4, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=curso_var, font=("Arial", 12), width=20).grid(row=1, column=5, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Turno:", font=("Arial", 12)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    combo_turno = ttk.Combobox(frame_superior, textvariable=turno_var, state="readonly", font=("Arial", 12), values=["","Mañana", "Tarde", "Vespertino", "Noche"])
    combo_turno.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Hora Entrada:", font=("Arial", 12)).grid(row=2, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=entrada_var, font=("Arial", 12)).grid(row=2, column=3, sticky="ew", padx=5, pady=5)
    
    ttk.Label(frame_superior, text="Hora Salida:", font=("Arial", 12)).grid(row=2, column=4, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=salida_var, font=("Arial", 12)).grid(row=2, column=5, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Situación Revista:", font=("Arial", 12)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    combo_situacion = ttk.Combobox(frame_superior, textvariable=situacion_var,
    values=["","Titular", "Provisorio", "Suplente", "Interino"], state="readonly", font=("Arial", 12)) 
    combo_situacion.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(frame_superior, text="Toma de Posición:", font=("Arial", 12)).grid(row=3, column=2, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=toma_pos_var, font=("Arial", 12)).grid(row=3, column=3, sticky="ew", padx=5, pady=5)

    ttk.Label(frame_superior, text="Fecha Cese:", font=("Arial", 12)).grid(row=3, column=4, sticky="e", padx=5, pady=5)
    ttk.Entry(frame_superior, textvariable=fecha_cese_var, font=("Arial", 12)).grid(row=3, column=5, sticky="ew", padx=5, pady=5)
    
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
    chk_activo.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=5)

    # =========================
    # TREEVIEW (Listado inferior)
    # =========================
    frame_inferior = ttk.LabelFrame(ventana, text="Listado Asignaciones", padding=10)
    frame_inferior.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    columnas = ("id", "profesor", "materia", "dia", "tipo_cargo", "módulos", "curso", "turno", "hentrada", "hsalida", "situacion_revista", "toma_pos", "fecha_cese", "activo")

    tree = ttk.Treeview(frame_inferior, columns=columnas, show="headings")
    tree.grid(row=0, column=0, sticky="nsew")
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

    tree.column("id", width=0, minwidth=0, stretch=False)
    tree.column("profesor", width=150)
    tree.column("materia", width=150)
    tree.column("dia", width=70)
    tree.column("tipo_cargo", width=150)
    tree.column("módulos", width=30)
    tree.column("curso", width=20)
    tree.column("turno", width=70)
    tree.column("hentrada", width=50)
    tree.column("hsalida", width=50)
    tree.column("situacion_revista", width=70)
    tree.column("toma_pos", width=70)
    tree.column("fecha_cese", width=70)
    tree.column("activo", width=10)

    scrollbar_y = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.grid(row=0, column=1, sticky="ns")

    # ============================================================================
    #                        CARGAS DE COMBOS PROFESOR Y MATERIAS
    # ============================================================================
    def cargar_combos():
        nonlocal profesores_dict, materia_dict
        
        conn = conectar()
        cursor = conn.cursor()

        profesores_dict.clear()
        materia_dict.clear()
        profesores_dict[""] = None
        materia_dict[""] = None

        #  ComboProfesores 
        cursor.execute("SELECT id_docente, apellido, nombre FROM profesores")
        for id_, apellido, nombre in cursor.fetchall():
            texto = f"{id_} - {apellido}, {nombre}"
            profesores_dict[texto] = id_

        combo_profesor["values"] = list(profesores_dict.keys())

        # Combo Materias
        cursor.execute("SELECT id_materia, nombre FROM materias")
        for id_, nombre in cursor.fetchall():
            texto = f"{id_} - {nombre}"
            materia_dict[texto] = id_

        combo_materia["values"] = list(materia_dict.keys())

        conn.close()
    # ----------------------------------------------------------------------------

    # =============================  GUARDA ASIGNACIONES DOCENTES  ======================
    def guardar():
        if not profesor_var.get():
            messagebox.showwarning("Atención", "Complete todos los campos", parent=ventana)
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

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
                    activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profesores_dict[profesor_var.get()],
                materia_dict[materia_var.get()],
                dia_var.get(),
                cargo_var.get(),
                modulos_var.get(),
                curso_var.get(),
                turno_var.get(),
                entrada_var.get(),
                salida_var.get(),
                situacion_var.get(),
                toma_pos_var.get(),
                fecha_cese_var.get(),
                activo_var.get()
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo("OK", "Asignación guardada", parent=ventana)
            cargar_tree()
            limpiar()

        except Exception as e:
            messagebox.showerror("Error", str(e), parent=ventana)
    # -------------------------------------------------------------------------------------

     # =========================== MUESTRA DATOS EN EL TREEVIEW  ============================
    def cargar_tree():
        # 1. Limpiamos todas las filas actuales del Treeview para no duplicar datos
        for item in tree.get_children():
            tree.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        
        # 2. Consulta SQL avanzada con JOINs para ver Nombres en lugar de IDs numéricos
        # Usamos IFNULL(materias.nombre, '---') para que si es cargo fijo muestre rayas en vez de "None"
        query= """
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
                CASE a.activo WHEN 1 THEN 'SÍ' ELSE 'NO' END AS estado_activo
            FROM asignacion a
            INNER JOIN profesores p ON a.id_docente = p.id_docente
            LEFT JOIN materias m ON a.id_materia = m.id_materia
            ORDER BY a.id_asignacion DESC;
        """
        
        try:
            cursor.execute(query)
            registros = cursor.fetchall()
            
            # 3. Cargamos los datos dentro del Treeview
            for fila in registros:
                tree.insert("", "end", values=fila)
                
        except sqlite3.OperationalError as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudo cargar el listado:\n{e}")
            
        finally:
            conn.close()
    # -------------------------------------------------------------------------------------

     # =============================  Modifica registro de Asignación ========================
    id_seleccionado = None

    def modificar():
        nonlocal id_seleccionado

        if id_seleccionado is None:
            messagebox.showwarning(
                "Atención",
                "Seleccione un registro", parent=ventana
            )
            return

        # Obtenemos de los diccionarios el número de ID de forma segura
        id_doc = profesores_dict.get(profesor_var.get(), None)
        id_mat = materia_dict.get(materia_var.get(), None)

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE asignacion
                SET
                    id_docente=?,     -- Dejado como id_docente según tu tabla
                    id_materia=?,
                    dia=?,             -- ¡Con la coma puesta!
                    cargo=?,
                    modulos=?,
                    curso=?,
                    turno=?,
                    hentrada=?,
                    hsalida=?,
                    situacion_revista=?,
                    toma_pos=?,
                    fecha_cese=?,
                    activo=?           -- El último campo antes del WHERE
                WHERE id_asignacion=?
            """, (
                id_doc,                # 1. id_docente
                id_mat,                # 2. id_materia
                dia_var.get(),         # 3. dia
                cargo_var.get(),       # 4. cargo
                modulos_var.get(),     # 5. modulos
                curso_var.get(),       # 6. curso
                turno_var.get(),       # 7. turno
                entrada_var.get(),     # 8. hentrada
                salida_var.get(),      # 9. hsalida
                situacion_var.get(),   # 10. situacion_revista
                toma_pos_var.get(),    # 11. toma_pos
                fecha_cese_var.get(),  # 12. fecha_cese
                activo_var.get(),      # 13. activo
                id_seleccionado        # 14. WHERE id_asignacion
            ))

            conn.commit()
            messagebox.showinfo(
                "OK",
                "Asignación modificada", parent=ventana
            )
            
            cargar_tree()
            limpiar()

        except sqlite3.OperationalError as e:
            messagebox.showerror("Error SQL", f"Ocurrió un problema:\n{e}", parent=ventana)
        finally:
            conn.close()
    # -------------------------------------------------------------------------------------

    # ============================ SELECCIONAR REGISTRO EN EL TREEVIEW ====================
    def on_tree_select(event):
        # 🔥 Avisamos que vamos a modificar la variable que creamos arriba
        nonlocal id_seleccionado 

        seleccion = tree.selection()
        if not seleccion:
            return  

        item = tree.item(seleccion[0])
        valores = item["values"]

        if valores:
            # 🔥 ¡PASO CLAVE! Guardamos el ID de la asignación seleccionada
            id_seleccionado = valores[0] 
            
            # (El resto de tus .set() quedan exactamente igual que antes...)
            profesor_var.set(valores[1])
            materia_var.set(valores[2])
            if valores[2] == "---":
                materia_var.set("")
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
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    # -------------------------------------------------------------------------------------
    def on_tree_select(event):
        nonlocal id_seleccionado 

        seleccion = tree.selection()
        if not seleccion:
            return  

        item = tree.item(seleccion[0])
        valores = item["values"]

        if valores:
            id_seleccionado = valores[0] 
            
            # --- 🔥 AQUÍ ESTÁ EL CAMBIO CLAVE ---
            # valores[0] tiene el id del profesor asignado de forma indirecta en esa fila.
            # Como en el Treeview mostramos el texto procesado, vamos a reconstruir la clave exacta:
            
            # Si tu consulta trae el texto de la fila tal cual, lo ideal es usar el ID que ya sabemos de la fila:
            # Reconstruimos el formato "ID - Apellido, Nombre" para que el diccionario lo reconozca
            txt_profesor = f"{valores[0]} - {valores[1]}" # O si guardaste el ID del profesor en otra columna oculta
            
            # Una forma más directa y limpia para no renegar:
            # Como en el Treeview dice "Almada, Alicia", pero en el combo necesitas "ID - Almada, Alicia"
            # Vamos a buscar en el Treeview si ya tenés los IDs a mano o los extraemos.
            
            # Si tu Treeview muestra en la columna 1 el texto "Almada, Alicia", podemos buscar en el diccionario
            # qué clave de las que existen TERMINA con ese nombre:
            nombre_buscado = valores[1]
            encontrado = ""
            for clave in profesores_dict.keys():
                if clave.endswith(nombre_buscado):
                    encontrado = clave
                    break
            
            profesor_var.set(encontrado if encontrado else valores[1])
            
            # Hacemos exactamente lo mismo para la materia si no es "---"
            materia_buscada = valores[2]
            if materia_buscada != "---":
                materia_encontrada = ""
                for clave in materia_dict.keys():
                    if clave.endswith(materia_buscada):
                        materia_encontrada = clave
                        break
                materia_var.set(materia_encontrada if materia_encontrada else valores[2])
            else:
                materia_var.set("")
            # ------------------------------------

            # El resto de tus variables quedan exactamente igual:
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

    tree.bind("<<TreeviewSelect>>", on_tree_select)
    # -------------------------------------------------------------------------------------

     # ================================= ELIMINA ASIGNACIONES ==============================
    def eliminar():
        nonlocal id_seleccionado

        if not id_seleccionado:
            messagebox.showwarning("Atención", "Seleccione un registro", parent=ventana)
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar asignación?", parent=ventana):
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM asignacion WHERE id_asignacion=?", (id_seleccionado,))
        conn.commit()
        conn.close()

        cargar_tree()
        limpiar()
    # ------------------------------------------------------------------------------------------

    # ========================  EXPORTAR ASIGNACIONES A PDF  ===================================
    def generar_pdf():
        # 1. Le pedimos al usuario el curso mediante un cuadro de diálogo rápido
        # Podés cambiar "Curso" por lo que quieras filtrar, o dejar que busque por aproximación
        curso_buscado = simpledialog.askstring(
            "Exportar a PDF", 
            "Ingrese el Curso a exportar (Ej: 1° 1°, 4to 1ra) o deje vacío para TODOS:",
            parent=ventana
        )
        
        # Si el usuario presiona "Cancelar" en el cuadro, salimos sin hacer nada
        if curso_buscado is None:
            return
            
        curso_buscado = curso_buscado.strip()

        # 2. Conectamos a la base de datos para buscar la información
        conn = conectar()
        cursor = conn.cursor()
        
        # Misma consulta SQL con los JOINs que ya usamos para tu Treeview
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
                CASE a.activo WHEN 1 THEN 'SÍ' ELSE 'NO' END AS estado_activo
            FROM asignacion a
            INNER JOIN profesores p ON a.id_docente = p.id_docente
            LEFT JOIN materias m ON a.id_materia = m.id_materia
        """
        
        # Si escribió algo, filtramos por curso; si lo dejó vacío, trae todos
        if curso_buscado:
            query += " WHERE a.curso LIKE ? ORDER BY a.curso ASC, p.apellido ASC"
            parametros = (f"%{curso_buscado}%",)
        else:
            query += " ORDER BY a.curso ASC, p.apellido ASC"
            parametros = ()
            
        cursor.execute(query, parametros)
        filas = cursor.fetchall()
        conn.close()
        
        if not filas:
            messagebox.showinfo("Sin resultados", f"No se encontraron asignaciones para: '{curso_buscado}'", parent=ventana)
            return
        
        nombre_archivo = f"Reporte_Curso_{curso_buscado.replace(' ', '_') if curso_buscado else 'Completo'}.pdf"
        
        # 1. Definimos la ruta de la carpeta donde queremos guardar los archivos
        carpeta_destino = os.path.join("reportes", "pdfs")
        
        # 2. Si la carpeta no existe, Python la crea en un segundo (crea 'reportes' y adentro 'pdfs')
        if not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino)
            
        # 3. Armamos el nombre del archivo base
        nombre_base = f"Reporte_Curso_{curso_buscado.replace(' ', '_') if curso_buscado else 'Completo'}.pdf"
        
        # 4. Combinamos la carpeta con el nombre del archivo para tener la ruta final completa
        nombre_archivo = os.path.join(carpeta_destino, nombre_base)

        try:
            # Configuración de hoja horizontal A4
            doc = SimpleDocTemplate(
                nombre_archivo, 
                pagesize=landscape(A4),
                rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Estilos visuales del PDF
            estilo_titulo = ParagraphStyle('T', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor("#2c3e50"), spaceAfter=4)
            estilo_subt = ParagraphStyle('S', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor("#7f8c8d"), spaceAfter=15)
            estilo_celda = ParagraphStyle('C', parent=styles['Normal'], fontSize=9, leading=11)
            estilo_cabecera = ParagraphStyle('H', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.white, fontName="Helvetica-Bold")
            
            # Encabezados en el documento
            story.append(Paragraph("SISTEMA ACADÉMICO - LISTADO DE ASIGNACIONES", estilo_titulo))
            txt_filtro = f"Filtro: Curso '{curso_buscado}'" if curso_buscado else "Filtro: Todas las asignaciones"
            story.append(Paragraph(f"{txt_filtro} | Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", estilo_subt))
        
           # Cabecera de la tabla (Corregido: Exactamente 12 títulos en orden)
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
            
            # Carga de filas al PDF (Corregido: Va del r[0] al r[11], total 12 campos)
            for r in filas:
                tabla_datos.append([
                    Paragraph(str(r[0]), estilo_celda),   # profesor
                    Paragraph(str(r[1]), estilo_celda),   # materia
                    Paragraph(str(r[2]), estilo_celda),   # dia
                    Paragraph(str(r[3]), estilo_celda),   # cargo
                    Paragraph(str(r[4]), estilo_celda),   # modulos
                    Paragraph(str(r[5]), estilo_celda),   # curso
                    Paragraph(str(r[6]), estilo_celda),   # turno
                    Paragraph(str(r[7]), estilo_celda),   # horario
                    Paragraph(str(r[8]), estilo_celda),   # situacion_revista
                    Paragraph(str(r[9]), estilo_celda),   # toma_pos
                    Paragraph(str(r[10]), estilo_celda),  # f_cese
                    Paragraph(str(r[11]), estilo_celda)   # estado_activo
                ])
            
            # Anchos de las columnas (Corregido: Exactamente 12 medidas que suman 780 píxeles horizontales)
            anchos = [135, 110, 50, 75, 40, 45, 50, 80, 75, 60, 55, 50]
            
            t = Table(tabla_datos, colWidths=anchos, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")])
            ]))
            
            story.append(t)
            doc.build(story)
            
            # Mensaje final y lo abre automáticamente
            messagebox.showinfo("Éxito", f"PDF creado con éxito:\n{nombre_archivo}", parent=ventana)
            os.startfile(nombre_archivo)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}", parent=ventana)
    # ------------------------------------------------------------------------------------------

    # ============================================================================
    #                       LIMPIAR CAMPOS
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
        activo_var.set("") # Resetea el checkbox tildado por defecto
    # -------------------------------------------------------------------------------

    # ===============================================================================
    #                                 BOTONES
    # ===============================================================================
    frame_botones = ttk.Frame(frame_superior)
    frame_botones.grid(row=5, column=0, columnspan=6, pady=15) # Ampliado el columnspan a 6 para centrar bien

    ttk.Button(frame_botones, text="💾 Guardar", command=guardar).grid(row=0, column=0, padx=5)
    ttk.Button(frame_botones, text="✏ Modificar", command=modificar).grid(row=0, column=1, padx=5)
    ttk.Button(frame_botones, text="🗑 Eliminar", command=eliminar).grid(row=0, column=2, padx=5)
    ttk.Button(frame_botones, text="🖨 Crear PDF", command=generar_pdf).grid(row=0, column=3, padx=5)
    ttk.Button(frame_botones, text="🧹 Limpiar", command=limpiar).grid(row=0, column=4, padx=5)
    ttk.Button(frame_botones, text="❌ Cerrar", command=ventana.destroy).grid(row=0, column=5, padx=5)

    # =========================
    # INICIO DE LA PANTALLA
    # =========================
    cargar_combos() # Ahora se ejecuta perfectamente sin errores
    cargar_tree()
    centrar_ventana(ventana)