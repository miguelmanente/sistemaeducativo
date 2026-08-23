import tkinter as tk
from tkinter import ttk

def abrir_ficha_docente(parent, datos):
    """
    Recibe los datos del docente como un diccionario o tupla y los muestra en una ficha.
    'datos' debe ser un diccionario con las claves de la tabla.
    """
    ventana = tk.Toplevel(parent)
    ventana.title(f"Ficha del Docente - {datos.get('nombre', '')} {datos.get('apellido', '')}")
    ventana.geometry("450x420")
    ventana.resizable(False, False)
    
    # Hacer la ventana modal
    ventana.transient(parent)
    ventana.grab_set()

    # --- ENCABEZADO ---
    header_frame = ttk.Frame(ventana, padding=10)
    header_frame.pack(fill="x")

    lbl_titulo = ttk.Label(
        header_frame, 
        text=f"{datos.get('apellido', '').upper()}, {datos.get('nombre', '')}", 
        font=("Arial", 14, "bold")
    )
    lbl_titulo.pack(anchor="w")

    lbl_id = ttk.Label(
        header_frame, 
        text=f"ID Docente: #{datos.get('id_docente', '')}", 
        font=("Arial", 9, "italic"), 
        foreground="gray"
    )
    lbl_id.pack(anchor="w")

    ttk.Separator(ventana, orient="horizontal").pack(fill="x", padx=10, pady=5)

    # --- CUERPO / CONTENEDOR DE LA FICHA ---
    card_frame = ttk.LabelFrame(ventana, text=" Información del Docente ", padding=15)
    card_frame.pack(fill="both", expand=True, padx=15, pady=10)

    # Definimos la lista de campos a renderizar en formato (Etiqueta, Clave en diccionario)
    campos = [
        ("D.N.I.:", "dni"),
        ("C.U.I.L.:", "cuil"),
        ("Fecha de Nacimiento:", "fecha_nacimiento"),
        ("Teléfono:", "telefono"),
        ("E-Mail:", "email"),
        ("Dirección:", "direccion")
    ]

    for i, (etiqueta, clave) in enumerate(campos):
        # Etiqueta (columna izquierda)
        lbl_field = ttk.Label(card_frame, text=etiqueta, font=("Arial", 10, "bold"))
        lbl_field.grid(row=i, column=0, sticky="e", pady=6, padx=10)

        # Valor (columna derecha)
        valor_texto = datos.get(clave, "") if datos.get(clave) else "-"
        lbl_val = ttk.Label(card_frame, text=valor_texto, font=("Arial", 10))
        lbl_val.grid(row=i, column=1, sticky="w", pady=6, padx=5)

    # Configurar columnas del grid dentro del LabelFrame
    card_frame.columnconfigure(1, weight=1)

    # --- BOTÓN DE CIERRE ---
    btn_cerrar = ttk.Button(ventana, text="Cerrar Ficha", command=ventana.destroy)
    btn_cerrar.pack(pady=10)


abrir_ficha_docente()