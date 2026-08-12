# ============================================================
# SISTEMA DE GESTIÓN EDUCATIVA - Módulo ciclo_lectivo.py
# ============================================================
""" Módulo para gestionar el ciclo lectivo.
    Su funcionalidad incluye la carga, modificación y visualización 
    de los datos del ciclo lectivo,"""

# ------------------------- LIBRERÍAS ------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import conectar
# ------------------------ FIN LIBRERÍAS ---------------------------------------



# ============================================================
# OBTENER CICLO LECTIVO
# ============================================================

def obtener_ciclo(anio):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            anio,
            fecha_inicio,
            fecha_fin,
            observacion
        FROM ciclo_lectivo
        WHERE anio = ?
    """, (anio,))

    dato = cursor.fetchone()

    conn.close()

    return dato


# ============================================================
# GUARDAR / MODIFICAR CICLO LECTIVO
# ============================================================

def guardar_ciclo(
    anio_var,
    fecha_inicio_var,
    fecha_fin_var,
    observacion_var
):

    anio = anio_var.get().strip()
    fecha_inicio = fecha_inicio_var.get().strip()
    fecha_fin = fecha_fin_var.get().strip()
    observacion = observacion_var.get().strip()

    # --------------------------------------------------------
    # Validar año
    # --------------------------------------------------------

    if not anio:
        messagebox.showwarning("Datos incompletos", "Debe seleccionar un año.")
        return

    # --------------------------------------------------------
    # Validar fecha de inicio
    # --------------------------------------------------------

    try:

        inicio = datetime.strptime(
            fecha_inicio,
            "%d/%m/%Y"
        )

    except ValueError:

        messagebox.showerror("Fecha incorrecta", "La fecha de inicio debe tener el formato DD/MM/AAAA.")
        return

    # --------------------------------------------------------
    # Validar fecha de finalización
    # --------------------------------------------------------

    try:

        fin = datetime.strptime(
            fecha_fin,
            "%d/%m/%Y"
        )

    except ValueError:

        messagebox.showerror(
            "Fecha incorrecta",
            "La fecha de finalización debe tener el formato DD/MM/AAAA."
        )

        return

    # --------------------------------------------------------
    # Verificar que las fechas correspondan al año
    # --------------------------------------------------------

    if inicio.year != int(anio):

        messagebox.showerror(
            "Año incorrecto",
            "La fecha de inicio no corresponde al año seleccionado."
        )

        return

    if fin.year != int(anio):

        messagebox.showerror(
            "Año incorrecto",
            "La fecha de finalización no corresponde al año seleccionado."
        )

        return

    # --------------------------------------------------------
    # Verificar orden de fechas
    # --------------------------------------------------------

    if fin < inicio:

        messagebox.showerror(
            "Fechas incorrectas",
            "La fecha de finalización no puede ser anterior "
            "a la fecha de inicio."
        )

        return

    # --------------------------------------------------------
    # Verificar si ya existe
    # --------------------------------------------------------

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT anio
        FROM ciclo_lectivo
        WHERE anio = ?
    """, (int(anio),))

    existe = cursor.fetchone()

    # --------------------------------------------------------
    # MODIFICAR
    # --------------------------------------------------------

    if existe:

        cursor.execute("""
            UPDATE ciclo_lectivo
            SET
                fecha_inicio = ?,
                fecha_fin = ?,
                observacion = ?
            WHERE anio = ?
        """, (
            fecha_inicio,
            fecha_fin,
            observacion,
            int(anio)
        ))

        mensaje = "El ciclo lectivo fue modificado correctamente."

    # --------------------------------------------------------
    # NUEVO
    # --------------------------------------------------------

    else:

        cursor.execute("""
            INSERT INTO ciclo_lectivo (
                anio,
                fecha_inicio,
                fecha_fin,
                observacion
            )
            VALUES (?, ?, ?, ?)
        """, (
            int(anio),
            fecha_inicio,
            fecha_fin,
            observacion
        ))

        mensaje = "El ciclo lectivo fue guardado correctamente."

    conn.commit()
    conn.close()

    messagebox.showinfo(
        "Ciclo lectivo",
        mensaje
    )


# ============================================================
# CARGAR DATOS DEL AÑO
# ============================================================

def cargar_ciclo(
    anio_var,
    fecha_inicio_var,
    fecha_fin_var,
    observacion_var
):

    anio = anio_var.get().strip()

    if not anio:
        return

    dato = obtener_ciclo(int(anio))

    # Limpiar primero

    fecha_inicio_var.set("")
    fecha_fin_var.set("")
    observacion_var.set("")

    if dato:

        fecha_inicio_var.set(dato[1])
        fecha_fin_var.set(dato[2])
        observacion_var.set(dato[3] or "")


# ============================================================
# VENTANA
# ============================================================

def ventana_ciclo_lectivo():

    ventana = tk.Toplevel()

    ventana.title("Ciclo Lectivo")

    ventana.geometry("700x400")
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))

    ventana.resizable(False, False)

    # ========================================================
    # VARIABLES
    # ========================================================

    anio_actual = datetime.now().year

    anio_var = tk.StringVar(
        value=str(anio_actual)
    )

    fecha_inicio_var = tk.StringVar()

    fecha_fin_var = tk.StringVar()

    observacion_var = tk.StringVar()


    # ========================================================
    # FRAME DATOS
    # ========================================================
    style = ttk.Style()

    style.configure("Valido.TEntry", foreground="black")
    style.configure("Error.TEntry", foreground="black")
    style.map("Error.TEntry",
            fieldbackground=[("!disabled", "#ffcccc")])  # rojo claro
    
    frame_datos = ttk.LabelFrame(
        ventana,
        text="Datos del Ciclo Lectivo"
    )

    frame_datos.pack(
        fill="x",
        padx=15,
        pady=15
    )


    # ========================================================
    # AÑO
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Año:"
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="e"
    )

    combo_anio = ttk.Combobox(
        frame_datos,
        textvariable=anio_var,
        width=12,
        state="readonly",
        values=[
            str(anio_actual - 1),
            str(anio_actual),
            str(anio_actual + 1)
        ],
        font=("Arial",12)
    )

    combo_anio.grid(
        row=0,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )


    # ========================================================
    # FECHA INICIO
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Fecha de inicio:"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=10,
        sticky="e"
    )

    ttk.Entry(
        frame_datos,
        textvariable=fecha_inicio_var,
        width=18,
        font=("Arial",12)
    ).grid(
        row=1,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )


    # ========================================================
    # FECHA FIN
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Fecha de finalización:"
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=10,
        sticky="e"
    )

    ttk.Entry(
        frame_datos,
        textvariable=fecha_fin_var,
        width=18,
        font=("Arial",12)
    ).grid(
        row=2,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )


    # ========================================================
    # OBSERVACIÓN
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Observación:"
    ).grid(
        row=3,
        column=0,
        padx=10,
        pady=10,
        sticky="e"
    )

    ttk.Entry(
        frame_datos,
        textvariable=observacion_var,
        width=45,
        font=("Arial",12)
    ).grid(
        row=3,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )


    # ========================================================
    # CAMBIO DE AÑO
    # ========================================================

    combo_anio.bind(
        "<<ComboboxSelected>>",
        lambda event: cargar_ciclo(
            anio_var,
            fecha_inicio_var,
            fecha_fin_var,
            observacion_var
        )
    )


    # ========================================================
    # BOTONES
    # ========================================================

    frame_botones = ttk.Frame(
        ventana
    )

    frame_botones.pack(
        fill="x",
        padx=15,
        pady=15
    )


    ttk.Button(
        frame_botones,
        text="Guardar / Modificar",
        command=lambda: guardar_ciclo(
            anio_var,
            fecha_inicio_var,
            fecha_fin_var,
            observacion_var
        )
    ).pack(
        side="left",
        padx=5
    )


    ttk.Button(
        frame_botones,
        text="Limpiar",
        command=lambda: (
            fecha_inicio_var.set(""),
            fecha_fin_var.set(""),
            observacion_var.set("")
        )
    ).pack(
        side="left",
        padx=5
    )


    ttk.Button(
        frame_botones,
        text="Cerrar",
        command=ventana.destroy
    ).pack(
        side="right",
        padx=5
    )


    # ========================================================
    # CARGAR AÑO ACTUAL
    # ========================================================

    cargar_ciclo(
        anio_var,
        fecha_inicio_var,
        fecha_fin_var,
        observacion_var
    )

