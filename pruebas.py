import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# NOMBRE DE TU BASE DE DATOS REAL
NOMBRE_BD = "bdescuela.db"  # Cambiá por el nombre de tu archivo .db


def obtener_conexion():
    return sqlite3.connect(NOMBRE_BD)

def salir():
    ventana.destroy()

# ---------------------------------------------------------
# CONSULTA SQL CON FILTRO DOBLE (AND)
# ---------------------------------------------------------
def consultar_datos_doble(campo1, valor1, campo2=None, valor2=None):
    conn = obtener_conexion()
    cursor = conn.cursor()

    query = """
        SELECT 
            p.apellido || ' ' || p.nombre AS docente,
            COALESCE(m.nombre, a.cargo) AS materia_o_cargo,
            a.dia,
            a.curso,
            a.turno,
            a.hentrada,
            a.hsalida,
            a.situacion_revista
        FROM asignacion a
        LEFT JOIN profesores p ON a.id_docente = p.id_docente
        LEFT JOIN materias m ON a.id_materia = m.id_materia
        WHERE a.{} LIKE ?
    """
    params = [f"%{valor1}%"]

    # Si se especificó un segundo filtro válido, agregamos el AND
    if campo2 and valor2:
        query += f" AND a.{campo2} LIKE ?"
        params.append(f"%{valor2}%")

    query += " ORDER BY a.dia ASC, a.hentrada ASC"

    cursor.execute(query.format(campo1), params)
    registros = cursor.fetchall()
    conn.close()
    return registros


# ---------------------------------------------------------
# GENERACIÓN DEL PDF
# ---------------------------------------------------------

def generar_pdf_desde_interfaz():
    campo1 = combo_campo1.get()
    valor1 = entry_valor1.get().strip()

    campo2 = combo_campo2.get()
    valor2 = entry_valor2.get().strip()

    if not valor1:
        messagebox.showwarning("Atención", "Ingrese al menos el primer valor para filtrar.", parent=ventana)
        return

    try:
        registros = consultar_datos_doble(
            campo1, valor1,
            campo2 if campo2 != "Ninguno" else None,
            valor2 if campo2 != "Ninguno" else None
        )
    except sqlite3.Error as e:
        messagebox.showerror("Error de Base de Datos", f"No se pudo consultar la BD:\n{e}", parent=ventana)
        return

    if not registros:
        messagebox.showinfo("Sin resultados", "No se encontraron registros que coincidan con los criterios.", parent=ventana)
        return

    # ---------------------------------------------------------
    # GESTIÓN DE CARPETAS Y RUTA DE SALIDA
    # ---------------------------------------------------------
    # Directorio actual donde está el script
    dir_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Crear la estructura de carpetas: reportes/pdf/Listados_cursos
    carpeta_destino = os.path.join(dir_actual, "reportes", "pdf", "Listados_cursos")
    os.makedirs(carpeta_destino, exist_ok=True)

    # Nombre del archivo
    valor1_limpio = valor1.replace("°", "").replace(" ", "_")
    nombre_archivo = f"reporte_{campo1}_{valor1_limpio}.pdf"
    
    # Ruta completa donde se guardará el PDF
    ruta_pdf = os.path.join(carpeta_destino, nombre_archivo)

    # ---------------------------------------------------------
    # GENERACIÓN DEL PDF CON REPORTLAB
    # ---------------------------------------------------------
    doc = SimpleDocTemplate(
        ruta_pdf,  # <--- Se pasa la ruta completa
        pagesize=landscape(A4),
        rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
    )

    story = []
    styles = getSampleStyleSheet()

    subtitulo = f"{campo1.upper()}: {valor1}"
    if campo2 != "Ninguno" and valor2:
        subtitulo += f" | {campo2.upper()}: {valor2}"

    story.append(Paragraph(f"<b>Listado de Asignaciones — {subtitulo}</b>", styles["Title"]))
    story.append(Spacer(1, 15))

    headers = ["Docente", "Materia / Cargo", "Día", "Curso", "Turno", "H. Entrada", "H. Salida", "Revista"]
    tabla_datos = [headers] + registros

    tabla = Table(tabla_datos, colWidths=[150, 150, 70, 60, 60, 75, 75, 80], repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (0,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#EDF2F7')]),
    ]))

    story.append(tabla)
    doc.build(story)

    messagebox.showinfo("Éxito", f"PDF generado correctamente en:\n{ruta_pdf}", parent=ventana)

# ---------------------------------------------------------
# INTERFAZ GRÁFICA TKINTER (CON FILTRO DOBLE)
# ---------------------------------------------------------
ventana = tk.Tk()
ventana.title("Listados PDF de Cursos, Cargos...")
ventana.geometry("600x400")
ventana.resizable(False, False)

frame = ttk.LabelFrame(ventana, text=" Configuración de Filtros ", padding=15)
frame.pack(fill="both", expand=True, padx=15, pady=15)

campos_disponibles = ["curso", "cargo", "dia", "turno", "situacion_revista", "activo"]

# --- FILTRO 1 ---
ttk.Label(frame, text="Primer campo:").grid(row=0, column=0, sticky="w", pady=5)
combo_campo1 = ttk.Combobox(frame, values=campos_disponibles, state="readonly", width=18)
combo_campo1.current(0)  # curso
combo_campo1.grid(row=0, column=1, pady=5, padx=5)

entry_valor1 = ttk.Entry(frame, width=15)
entry_valor1.insert(0, "1°1°")
entry_valor1.grid(row=0, column=2, pady=5, padx=5)

# --- FILTRO 2 (OPCIONAL) ---
campos_filtro2 = ["Ninguno"] + campos_disponibles

ttk.Label(frame, text="Segundo campo:").grid(row=1, column=0, sticky="w", pady=5)
combo_campo2 = ttk.Combobox(frame, values=campos_filtro2, state="readonly", width=18)
combo_campo2.current(2)  # dia por defecto
combo_campo2.grid(row=1, column=1, pady=5, padx=5)

entry_valor2 = ttk.Entry(frame, width=15)
entry_valor2.insert(0, "Lunes")
entry_valor2.grid(row=1, column=2, pady=5, padx=5)

# --- BOTÓN ---
btn_generar = ttk.Button(frame, text="📄 Generar PDF", command=generar_pdf_desde_interfaz)
btn_generar.grid(row=2, column=0, columnspan=3, pady=15)

btn_generar = ttk.Button(frame, text="❌ Cerrar Listados", command=salir)
btn_generar.grid(row=2, column=2, columnspan=3,padx=15, pady=15)

ventana.mainloop()