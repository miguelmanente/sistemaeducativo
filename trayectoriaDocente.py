import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from database import conectar

# Importaciones de ReportLab para el Certificado
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def calcular_tiempo_servicio(f_toma, f_cese_o_str, es_activo):
    """
    Calcula los años y meses trabajados entre dos fechas en formato DD/MM/AAAA.
    Si está activo, calcula hasta la fecha actual.
    """
    try:
        # Convertir fecha de toma de posesión
        inicio = datetime.strptime(f_toma, "%d/%m/%Y")
        
        # Determinar fecha de fin
        if es_activo == "SÍ" or f_cese_o_str == "---" or not f_cese_o_str:
            fin = datetime.now()
        else:
            fin = datetime.strptime(f_cese_o_str, "%d/%m/%Y")
        
        # Calcular diferencia en meses totales
        total_meses = (fin.year - inicio.year) * 12 + (fin.month - inicio.month)
        
        # Ajustar si el día actual es menor al de inicio (para no redondear hacia arriba antes de tiempo)
        if fin.day < inicio.day:
            total_meses -= 1
            
        if total_meses < 0:
            return "0 meses"
            
        anios = total_meses // 12
        meses = total_meses % 12
        
        # Armar texto legible
        resultado = []
        if anios > 0:
            resultado.append(f"{anios} {'año' if anios == 1 else 'años'}")
        if meses > 0:
            resultado.append(f"{meses} {'mes' if meses == 1 else 'meses'}")
            
        return ", ".join(resultado) if resultado else "Menos de 1 mes"
        
    except Exception:
        return "---"

def abrir_trayectoria_docente():
    # -------------------------------------------------------------------------
    # 1. CONFIGURACIÓN DE LA VENTANA
    # -------------------------------------------------------------------------
    ventana = tk.Toplevel()
    ventana.title("Historial y Trayectoria de Docentes")
    ventana.state('zoomed') 
    
    docentes_dict = {}
    id_docente_seleccionado = None
    dni_docente_seleccionado = None 

    ventana.rowconfigure(1, weight=1) 
    ventana.columnconfigure(0, weight=1)

    # -------------------------------------------------------------------------
    # 2. FUNCIONES DE LÓGICA Y BASE DE DATOS
    # -------------------------------------------------------------------------
    def cargar_combo_docentes():
        """Trae todos los docentes de la DB para el buscador, ordenados por apellido."""
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id_docente, apellido, nombre, dni FROM profesores ORDER BY apellido ASC")
            filas = cursor.fetchall()
            valores_combo = []
            docentes_dict.clear()
            
            for f in filas:
                id_doc, apellido, nombre, dni = f
                texto_mostrar = f"{apellido}, {nombre}"
                valores_combo.append(texto_mostrar)
                docentes_dict[texto_mostrar] = (id_doc, dni if dni else "---")
                
            combo_docente['values'] = valores_combo
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los docentes:\n{e}", parent=ventana)
        finally:
            conn.close()

    def buscar_trayectoria(event=None):
        """Busca el historial del docente seleccionado y llena el Treeview."""
        nonlocal id_docente_seleccionado, dni_docente_seleccionado
        nombre_sel = combo_docente.get()
        
        if not nombre_sel or nombre_sel not in docentes_dict:
            return
            
        id_docente_seleccionado, dni_docente_seleccionado = docentes_dict[nombre_sel]
        
        # Limpiamos el Treeview
        for item in tree.get_children():
            tree.delete(item)
            
        conn = conectar()
        cursor = conn.cursor()
        
        # Traemos todos los datos (mantenemos la query original para no romper la DB, 
        # pero procesaremos el descarte de columnas y el cálculo aquí)
        query = """
            SELECT 
                a.id_asignacion,
                IFNULL(m.nombre, '---') AS materia,
                a.dia,
                a.cargo,
                a.modulos,
                a.curso,
                a.turno,
                a.hentrada || ' a ' || a.hsalida AS horario,
                a.situacion_revista,
                a.toma_pos,
                IFNULL(a.fecha_cese, '---') AS cese,
                CASE a.activo WHEN 1 THEN 'SÍ' ELSE 'NO' END AS es_activo
            FROM asignacion a
            LEFT JOIN materias m ON a.id_materia = m.id_materia
            WHERE a.id_docente = ?
            ORDER BY a.toma_pos DESC, a.fecha_cese DESC
        """
        
        try:
            cursor.execute(query, (id_docente_seleccionado,))
            filas = cursor.fetchall()
            
            for f in filas:
                toma_pos = f[9]
                fecha_cese = f[10]
                activo_str = f[11]
                
                # Ejecutamos el cálculo de tiempo en tiempo real
                antiguedad = calcular_tiempo_servicio(toma_pos, fecha_cese, activo_str)
                
                # Insertamos en la grilla saltándonos Turno f[6] y Horario f[7], 
                # e inyectamos la 'antiguedad' calculada al final.
                tree.insert("", "end", values=(
                    f[0],  # ID
                    f[1],  # Materia
                    f[2],  # Día
                    f[3],  # Cargo
                    f[4],  # Módulos
                    f[5],  # Curso
                    f[8],  # Sit. Revista
                    toma_pos, 
                    fecha_cese, 
                    activo_str,
                    antiguedad # <--- Nueva columna calculada
                ))
                
        except Exception as e:
            messagebox.showerror("Error SQL", f"No se pudo obtener el historial:\n{e}", parent=ventana)
        finally:
            conn.close()

    def generar_certificado_pdf():
        """Genera un Certificado de Servicios formal en PDF con la trayectoria, DNI y Antigüedad."""
        if id_docente_seleccionado is None:
            messagebox.showwarning("Atención", "Por favor, seleccione un docente de la lista primero.", parent=ventana)
            return
            
        nombre_docente = combo_docente.get()
        filas_tree = tree.get_children()
        if not filas_tree:
            messagebox.showinfo("Sin Datos", "El docente seleccionado no registra servicios en el sistema.", parent=ventana)
            return
            
        carpeta = os.path.join("reportes", "certificados")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            
        nombre_archivo = os.path.join(carpeta, f"Certificado_{nombre_docente.replace(', ', '_').replace(' ', '_')}.pdf")
        
        try:
            doc = SimpleDocTemplate(
                nombre_archivo, pagesize=landscape(A4),
                rightMargin=30, leftMargin=30, topMargin=35, bottomMargin=35
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            estilo_institucion = ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor("#2c3e50"), spaceAfter=15)
            estilo_titulo = ParagraphStyle('Tit', fontName='Helvetica-Bold', fontSize=22, leading=26, alignment=1, textColor=colors.HexColor("#1a252f"), spaceAfter=15)
            estilo_cuerpo = ParagraphStyle('Cuerpo', fontName='Helvetica', fontSize=11, leading=16, alignment=4, spaceAfter=20)
            estilo_cabecera = ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)
            estilo_celda = ParagraphStyle('C', fontName='Helvetica', fontSize=9, leading=11)
            
            story.append(Paragraph("ESCUELA DE EDUCACIÓN SECUNDARIA TÉCNICA<br/>SAN NICOLÁS, ARGENTINA", estilo_institucion))
            story.append(Spacer(1, 10))
            story.append(Paragraph("CERTIFICADO DE SERVICIOS", estilo_titulo))
            story.append(Spacer(1, 15))
            
            fecha_hoy = datetime.now().strftime('%d de %B de %Y')
            meses = {'January':'Enero','February':'Febrero','March':'Marzo','April':'Abril','May':'Mayo','June':'Junio','July':'Julio','August':'Agosto','September':'Septiembre','October':'Octubre','November':'Noviembre','December':'Diciembre'}
            for eng, esp in meses.items():
                fecha_hoy = fecha_hoy.replace(eng, esp)

            texto_certificado = f"Por la presente se certifica que el/la docente <b>{nombre_docente.upper()}</b>, DNI N° <b>{dni_docente_seleccionado}</b>, ha prestado servicios en este establecimiento educativo, registrando formalmente la trayectoria laboral que se detalla a continuación en el historial de asignaciones técnico-pedagógicas a la fecha de emisión {fecha_hoy}:"
            story.append(Paragraph(texto_certificado, estilo_cuerpo))
            
            # Ajustamos la cabecera de la tabla (10 columnas ahora)
            tabla_datos = [[
                Paragraph("MATERIA", estilo_cabecera), Paragraph("DÍA", estilo_cabecera),
                Paragraph("CARGO", estilo_cabecera), Paragraph("MOD.", estilo_cabecera),
                Paragraph("CURSO", estilo_cabecera), Paragraph("SIT. REVISTA", estilo_cabecera),
                Paragraph("F. TOMA", estilo_cabecera), Paragraph("F. CESE", estilo_cabecera),
                Paragraph("ACTIVO", estilo_cabecera), Paragraph("TIEMPO SERVICIO", estilo_cabecera) # <-- Nueva cabecera
            ]]
            
            for item_id in filas_tree:
                valores = tree.item(item_id)["values"]
                # Los índices cambiaron porque quitamos cosas en la grilla visual
                tabla_datos.append([
                    Paragraph(str(valores[1]), estilo_celda),  # Materia
                    Paragraph(str(valores[2]), estilo_celda),  # Día
                    Paragraph(str(valores[3]), estilo_celda),  # Cargo
                    Paragraph(str(valores[4]), estilo_celda),  # Modulos
                    Paragraph(str(valores[5]), estilo_celda),  # Curso
                    Paragraph(str(valores[6]), estilo_celda),  # Situacion Revista
                    Paragraph(str(valores[7]), estilo_celda),  # Toma Pos
                    Paragraph(str(valores[8]), estilo_celda),  # Cese
                    Paragraph(str(valores[9]), estilo_celda),  # Activo
                    Paragraph(str(valores[10]), estilo_celda)  # Antigüedad calculada
                ])
                
            # Redistribución de anchos para ocupar de forma óptima la hoja horizontal (A4 Landscape = 740 aprox)
            anchos = [160, 70, 160, 40, 40, 80, 70, 70, 50, 95]
            
            t = Table(tabla_datos, colWidths=anchos, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a252f")), 
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#7f8c8d")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")])
            ]))
            story.append(t)
            
            story.append(Spacer(1, 40))
            tabla_firma = Table([["", ""]], colWidths=[370, 370])
            tabla_firma.setStyle(TableStyle([
                ('LINEBELOW', (0, 0), (0, 0), 1, colors.black),  
                ('LINEBELOW', (1, 0), (1, 0), 1, colors.black),  
            ]))
            story.append(tabla_firma)
            
            story.append(Spacer(1, 10))
            estilo_firma = ParagraphStyle('Firma', fontName='Helvetica', fontSize=10, alignment=1)
            f_datos = [[Paragraph("Firma del Interesado", estilo_firma), Paragraph("Firma y Sello de la Dirección", estilo_firma)]]
            t_f_texto = Table(f_datos, colWidths=[370, 370])
            story.append(t_f_texto)

            doc.build(story)
            
            messagebox.showinfo("Éxito", f"Certificado creado correctamente en:\n{nombre_archivo}", parent=ventana)
            os.startfile(nombre_archivo) 
            
        except Exception as e:
            messagebox.showerror("Error PDF", f"No se pudo confeccionar el certificado:\n{e}", parent=ventana)

    # -------------------------------------------------------------------------
    # 3. INTERFAZ GRÁFICA (CON TKINTER / TTK)
    # -------------------------------------------------------------------------
    frame_busqueda = ttk.LabelFrame(ventana, text=" Buscador de Personal Docente ", padding=15)
    frame_busqueda.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=15)
    
    ttk.Label(frame_busqueda, text="Seleccione el Docente:", font=("Arial", 11)).grid(row=0, column=0, padx=5, sticky="w")
    
    combo_docente = ttk.Combobox(frame_busqueda, width=45, font=("Arial", 11), state="readonly")
    combo_docente.grid(row=0, column=1, padx=10, sticky="w")
    combo_docente.bind("<<ComboboxSelected>>", buscar_trayectoria) 
    
    ttk.Button(frame_busqueda, text="🔍 Cargar Historial", command=buscar_trayectoria).grid(row=0, column=2, padx=10)

    frame_grid = ttk.LabelFrame(ventana, text=" Registro Histórico de Asignaciones y Servicios ", padding=10)
    frame_grid.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=5)
    frame_grid.rowconfigure(0, weight=1)
    frame_grid.columnconfigure(0, weight=1)

    # Quitamos "turno" y "horario" de las columnas del Treeview, añadimos "antiguedad"
    columnas = ("id", "materia", "dia", "cargo", "mod", "curso", "situacion", "toma", "cese", "activo", "antiguedad")
    tree = ttk.Treeview(frame_grid, columns=columnas, show="headings")
    
    tree.heading("id", text="ID Asig.")
    tree.heading("materia", text="Materia")
    tree.heading("dia", text="Día")
    tree.heading("cargo", text="Cargo")
    tree.heading("mod", text="Mod.")
    tree.heading("curso", text="Curso")
    tree.heading("situacion", text="Sit. Revista")
    tree.heading("toma", text="F. Toma Pos.")
    tree.heading("cese", text="F. Cese")
    tree.heading("activo", text="Actual?")
    tree.heading("antiguedad", text="Tiempo Servicio") # <-- Cabecera en pantalla

    tree.column("id", width=0, stretch=False, anchor="center")
    tree.column("materia", width=150, anchor="w")
    tree.column("dia", width=70, anchor="center")
    tree.column("cargo", width=120, anchor="w")
    tree.column("mod", width=45, anchor="center")
    tree.column("curso", width=60, anchor="center")
    tree.column("situacion", width=100, anchor="center")
    tree.column("toma", width=95, anchor="center")
    tree.column("cese", width=95, anchor="center")
    tree.column("activo", width=60, anchor="center")
    tree.column("antiguedad", width=130, anchor="w") # <-- Celda en pantalla

    scroll_y = ttk.Scrollbar(frame_grid, orient="vertical", command=tree.yview)
    scroll_x = ttk.Scrollbar(frame_grid, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    
    tree.grid(row=0, column=0, sticky="nsew")
    scroll_y.grid(row=0, column=1, sticky="ns")
    scroll_x.grid(row=1, column=0, sticky="ew")

    frame_botones = ttk.Frame(ventana, padding=10)
    frame_botones.grid(row=2, column=0, columnspan=2, pady=15)
    
    ttk.Button(frame_botones, text="🖨 Exportar Certificado de Servicios (PDF)", command=generar_certificado_pdf, width=40).grid(row=0, column=0, padx=10)
    ttk.Button(frame_botones, text="❌ Cerrar Ventana", command=ventana.destroy, width=15).grid(row=0, column=1, padx=10)

    cargar_combo_docentes()