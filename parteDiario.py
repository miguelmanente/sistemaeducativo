# ========================================================================================
#                  MÓDULO LISTADOS DE PARTE DIARIOS
# ========================================================================================

# ----------------------------------- LIBRERÍAS ------------------------------------------
from tkinter import ttk, Frame, Label, messagebox
from datetime import datetime
import tkinter as tk
from datetime import datetime
from openpyxl import Workbook
import os
# Importaciones necesarias de ReportLab
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from database import conectar
from centraVent import centrar_ventana
# -----------------------------------------------------------------------------------------

# =================  Función Encabezado de pantalla =============================
def encabezado(fecha="", dia=""):       
        texto = f"""
    ========================================
            ESCUELA SECUNDARIA
    ========================================
        Parte diario de personal Docente
    Fecha: {fecha}
    Día: {dia}
    ========================================
    """
        return texto
#    -----------------------------------------------------------------------------

# ======================= FUNCIÓN PRINCIPAL DEL LISTADO DIARIO ==================
def abrir_parte_diario():

    conn = conectar()

    ventana = tk.Toplevel()
    ventana.title("PARTE DIARIO")
    #ventana.geometry("1100x700")
    ventana.state('zoomed') 

    # =========================
    # VARIABLES
    # =========================
    turno_var = tk.StringVar()
    fecha_var = tk.StringVar()
    dia_var = tk.StringVar()
   
    # =========================
    # SELECTORES
    # =========================

    tk.Label(ventana, text="Turno", font=("Arial", 12)).pack()
    tk.Entry(ventana, textvariable=turno_var, font=("Arial", 12)).pack()
    tk.Label(ventana, text="Fecha", font=("Arial", 12)).pack()
    tk.Entry(ventana, textvariable=fecha_var, font=("Arial", 12)).pack()
    tk.Label(ventana, text="Día", font=("Arial", 12)).pack()
    tk.Entry(ventana, textvariable=dia_var, font=("Arial", 12)).pack()
    lbl_encabezado = tk.Label(ventana, text=encabezado(), justify="left", font=("Arial", 12))
    lbl_encabezado.pack()

    # =================  ACTUALIZAR LO QUE ESCRIBO EN LOS ENTRYS ==============
    def actualizar_encabezado(*args):
        lbl_encabezado.config(
            text=encabezado(
                fecha_var.get(),
                dia_var.get()
            )
        )

    fecha_var.trace_add("write", actualizar_encabezado)
    dia_var.trace_add("write", actualizar_encabezado)
    # --------------------------------------------------------------------------
   
    # ==========================================================================
    #                       TREEVIEW
    # ==========================================================================
    style = ttk.Style()
    style.configure("TCombobox", font=("Arial", 12))
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12)) 
    
    tree = ttk.Treeview(ventana, columns=("nombre", "detalle", "entrada", "salida", "reemplaza","firma"), show="headings")

    tree.heading("nombre", text="Apellido Nombres")
    tree.heading("detalle", text="Cargo/Materia")
    tree.heading("entrada", text="Entrada")
    tree.heading("salida", text="Salida")
    tree.heading("reemplaza", text="Reemplaza a") # <-- Nuevo encabezado
    tree.heading("firma", text="Firma")

    tree.pack(fill="both", expand=True)

    tree.column("nombre", width=200)
    tree.column("detalle", width=200)
    tree.column("entrada", width=50)
    tree.column("salida", width=50)
    tree.column("reemplaza", width=200)
    tree.column("firma", width=150)

    
    # -------------------------------------------------------------------------

    # ====================  CARGA LOS TURNOS Y DOCENTES Y DIAS   ===============
    def cargar_parte_diario(tree, turno_var, dia_var, conn):

        cursor = conn.cursor()

        # Limpiamos el Treeview antes de cargar
        for item in tree.get_children():
            tree.delete(item)

        # ---------------------------------------------------------------------
        # CONSULTA UNIFICADA CORREGIDA PARA COMBOS CON "Lunes a Viernes"
        # ---------------------------------------------------------------------
        query_unificada = """
            SELECT 
                -- LÓGICA DE REEMPLAZO: Si hay un suplente activo para el mismo cargo/materia
                CASE 
                    WHEN (SELECT COUNT(*) FROM asignacion a2 
                        WHERE a2.id_materia IS NOT DISTINCT FROM a.id_materia 
                        AND a2.cargo = a.cargo
                        -- CORRECCIÓN: Verifica si el día buscado coincide o está en el rango
                        AND (a2.dia = ? OR (a2.dia = 'Lunes a Viernes' AND ? IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')))
                        AND a2.hentrada = a.hentrada
                        AND a2.situacion_revista = 'Suplente' 
                        AND a2.activo = 1) > 0 THEN '(SUPLENTE) ' || (
                            SELECT p2.apellido || ', ' || p2.nombre FROM asignacion a3
                            JOIN profesores p2 ON a3.id_docente = p2.id_docente
                            WHERE a3.id_materia IS NOT DISTINCT FROM a.id_materia 
                            AND a3.cargo = a.cargo
                            AND (a3.dia = ? OR (a3.dia = 'Lunes a Viernes' AND ? IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')))
                            AND a3.hentrada = a.hentrada
                            AND a3.situacion_revista = 'Suplente' 
                            AND a3.activo = 1 LIMIT 1
                        )
                    ELSE p.apellido || ', ' || p.nombre
                END AS nombre_final,
                
                -- Si no tiene materia (cargos jerárquicos), muestra el nombre del cargo
                CASE 
                    WHEN m.nombre IS NULL THEN a.cargo
                    ELSE m.nombre
                END AS detalle_mostrar,
                
                a.hentrada,
                a.hsalida,
                
                -- NUEVA COLUMNA CALCULADA: Busca quién es el Titular/Interino original
                CASE 
                    WHEN (SELECT COUNT(*) FROM asignacion a2 
                        WHERE a2.id_materia IS NOT DISTINCT FROM a.id_materia 
                        AND a2.cargo = a.cargo
                        AND (a2.dia = ? OR (a2.dia = 'Lunes a Viernes' AND ? IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')))
                        AND a2.hentrada = a.hentrada
                        AND a2.situacion_revista = 'Suplente' 
                        AND a2.activo = 1) > 0 THEN (
                            SELECT p3.apellido || ', ' || p3.nombre FROM asignacion a4
                            JOIN profesores p3 ON a4.id_docente = p3.id_docente
                            WHERE a4.id_materia IS NOT DISTINCT FROM a.id_materia 
                            AND a4.cargo = a.cargo
                            AND (a4.dia = ? OR (a4.dia = 'Lunes a Viernes' AND ? IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado')))
                            AND a4.hentrada = a.hentrada
                            AND a4.situacion_revista IN ('Titular', 'Interino') 
                            AND a4.activo = 1 LIMIT 1
                        )
                    ELSE '---'
                END AS reemplaza_a
                
            FROM asignacion a
            JOIN profesores p ON a.id_docente = p.id_docente
            LEFT JOIN materias m ON a.id_materia = m.id_materia
            
            -- FILTRO PRINCIPAL: Trae si coincide el día exacto O si es de Lunes a Viernes y el día seleccionado está en ese rango
            WHERE (a.dia = ? OR (a.dia = 'Lunes a Viernes' AND ? IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes')))
            AND a.turno = ? 
            AND a.activo = 1
            
            GROUP BY a.id_docente, a.id_materia, a.cargo, a.hentrada, a.hsalida
            ORDER BY
                CASE a.cargo
                    WHEN 'Director' THEN 1
                    WHEN 'Vice Director' THEN 2
                    WHEN 'Vicedirector' THEN 2
                    WHEN 'Secretario' THEN 3
                    WHEN 'Prosecretario' THEN 4
                    WHEN 'Jefe de Área' THEN 5
                    WHEN 'Encargado de Laboratorio' THEN 6
                    ELSE 99
                END, 
                a.hentrada ASC;
        """

        try:
            # Obtenemos los valores actuales de los combos
            dia_seleccionado = dia_var.get()
            turno_seleccionado = turno_var.get()

            # Ojo: Como agregamos más parámetros dinámicos a la consulta debido a las subconsultas, 
            # pasamos las variables en el orden exacto en que aparecen los signos de pregunta '?'
            parametros = (
                dia_seleccionado, dia_seleccionado,  # Para el primer CASE (COUNT)
                dia_seleccionado, dia_seleccionado,  # Para el primer CASE (Nombre suplente)
                dia_seleccionado, dia_seleccionado,  # Para el reemplaza_a (COUNT)
                dia_seleccionado, dia_seleccionado,  # Para el reemplaza_a (Nombre titular)
                dia_seleccionado, dia_seleccionado,  # Para el WHERE principal
                turno_seleccionado                   # Para el turno en el WHERE principal
            )

            cursor.execute(query_unificada, parametros)
            filas = cursor.fetchall()

            for fila in filas:
                tree.insert(
                    "",
                    "end",
                    values=(
                        fila[0], # Nombre (Titular o Suplente)
                        fila[1], # Cargo o Materia
                        fila[2], # Entrada
                        fila[3], # Salida
                        fila[4], # Reemplaza a
                        ""       # Espacio para Firma vacía
                    )
                )
        except Exception as e:
            messagebox.showerror("Error de Carga", f"No se pudo generar el Parte Diario:\n{e}", parent=ventana)
    # --------------------------------------------------------------------------------------------------------------

    # ====================== EXPORTAR PLANILLA DIARIAS A PDF ========================
    def exportar_pdf_pro_corregido(tree, dia_var, turno_var):
        # 1. Validar que el Treeview tenga datos para no generar un PDF vacío
        if not tree.get_children():
            messagebox.showwarning("Advertencia", "No hay datos en la tabla para exportar.", parent=ventana)
            return

        # 2. Configurar carpetas y rutas
        #carpeta = "reportes"  # Cambiado a 'reporte' para cumplir con tu consigna
        #os.makedirs(carpeta, exist_ok=True)
        carpeta = os.path.join("reportes", "planilla diaria")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        # Lógica de la fecha: si el usuario escribió algo, usamos eso. Si está vacío, queda en blanco para escribir a mano.
        fecha_usuario = fecha_var.get().strip()
        
        if fecha_usuario == "":
            fecha_mostrar = "...... / ...... / 202..." # Para rellenar a mano
            fecha_archivo = "en_blanco"
        else:
            fecha_mostrar = fecha_usuario
        # Limpiamos caracteres raros por las dudas para el nombre del archivo
        fecha_archivo = fecha_usuario.replace("/", "-")

        #nombre = f"parte_diario_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        nombre = f"parte_diario_{dia_var.get()}_{turno_var.get()}_{fecha_archivo}.pdf"
        ruta = os.path.join(carpeta, nombre)

        # Definimos el tamaño de hoja estándar
        doc = SimpleDocTemplate(ruta, pagesize=A4)
        elementos = []
        styles = getSampleStyleSheet()

        # =====================================================================
        # ENCABEZADO AUTOMÁTICO
        # =====================================================================
        encabezado_texto = f"<b>PARTE DIARIO DE ASISTENCIA</b><br/>" \
                        f"Día: {dia_var.get()} | Turno: {turno_var.get()}<br/>" \
                        f"<b>Fecha del Parte:</b> {fecha_mostrar}"
                        #f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"
                        
        
        elementos.append(Paragraph(encabezado_texto, styles["Title"]))
        elementos.append(Spacer(1, 15))

        # =====================================================================
        # DATOS TABLA (Ajustado a las 6 columnas de tu nuevo sistema)
        # =====================================================================
        # Agregamos la columna "Reemplaza a" que faltaba en tu lista original
        data = [["Nombre / Personal", "Cargo / Materia", "Entrada", "Salida", "Reemplaza a", "Firma"]]

        for item in tree.get_children():
            # Obtenemos los valores del Treeview
            valores_fila = list(tree.item(item)["values"])
            
            # OJO: Tu consulta SQL deja el último valor como vacío ("") para la firma. 
            # Si tu treeview devuelve 6 elementos, lo dejamos como viene. 
            # Si devuelve 5, le agregamos el espacio en blanco para que coincida con la cabecera.
            if len(valores_fila) == 5:
                valores_fila.append("") 
                
            data.append(valores_fila)

        # Definimos anchos proporcionales para las 6 columnas (Ancho total aproximado: 540 puntos)
        # Nombre, Cargo, Entrada, Salida, Reemplaza a, Firma
        table = Table(data, colWidths=[120, 140, 45, 45, 90, 100])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Centrado vertical para que quede prolijo
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ]))

        elementos.append(table)

        # =====================================================================
        # ESPACIO EXTRA PARA FIRMA DEL DIRECTIVO (Opcional pero muy útil)
        # =====================================================================
        elementos.append(Spacer(1, 40))
        data_firma_autoridad = [["", "_____________________________________"],
                                ["", "Firma del Responsable de Turno"]]
        t_autoridad = Table(data_firma_autoridad, colWidths=[300, 240])
        t_autoridad.setStyle(TableStyle([
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (1, 1), (1, 1), 9),
        ]))
        elementos.append(t_autoridad)

        # 3. Compilar el documento sin pasarle el 'parent' problemático al messagebox
        try:
            doc.build(elementos)
            messagebox.showinfo("PDF Generado", f"El parte diario se exportó con éxito a:\n{ruta}", parent=ventana)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el archivo PDF:\n{e}", parent=ventana)

    # -------------------------------------------------------------------------------

    # =========================================================================
    #                                 BOTONES
    # =========================================================================
  
    # Frame para los botones
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=10)

    tk.Button(frame_botones, text="💾 Cargar Planilla Diaria",font=("Segoe UI Emoji", 12, "bold"),
        command=lambda: cargar_parte_diario(tree, turno_var, dia_var, conn)).pack(side="left", padx=5)

    tk.Button(frame_botones, text=" 📄Exportar a PDF",font=("Segoe UI Emoji", 12, "bold"),
        command=lambda: exportar_pdf_pro_corregido(tree, dia_var, turno_var)       
    ).pack(side="left", padx=5)

    tk.Button(frame_botones, text="❌ Cerrar",font=("Segoe UI Emoji", 12, "bold"),
        command=ventana.destroy).pack(side="left", padx=5)

    # =================================== INICIO ===========================================
    centrar_ventana(ventana)