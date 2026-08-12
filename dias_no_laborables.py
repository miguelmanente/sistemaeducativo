# ============================================================
# SISTEMA DE GESTIÓN EDUCATIVA - # Gestión de Días No Laborables
# ============================================================

# ------------------------- LIBRERÍAS ---------------------------------
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from database import conectar
from negocio.motor_inasistencias import obtener_dias_no_laborables
# ---------------------------------------------------------------------

# ============================================================
# VENTANA
# ============================================================
# ============================================================
# Cargar registros en el Treeview
# ============================================================

def cargar_dias_no_laborables(tree, anio):

    # Limpiar el listado
    for item in tree.get_children():
        tree.delete(item)

    datos = obtener_dias_no_laborables(anio)

    for dato in datos:

        tree.insert(
            "",
            "end",
            values=(
                dato["id"],
                dato["fecha"],
                dato["tipo"],
                dato["descripcion"]
            )
        )


# ============================================================
# Guardar día no laborable
# ============================================================

def guardar_dia_no_laborable(
    anio_var,
    fecha_var,
    tipo_var,
    descripcion_var,
    tree
):

    anio = anio_var.get().strip()
    fecha = fecha_var.get().strip()
    tipo = tipo_var.get().strip()
    descripcion = descripcion_var.get().strip()

    # --------------------------------------------------------
    # Validar año
    # --------------------------------------------------------

    if not anio:
        messagebox.showwarning(
            "Datos incompletos",
            "Debe seleccionar un año."
        )
        return

    # --------------------------------------------------------
    # Validar fecha
    # --------------------------------------------------------

    if not fecha:
        messagebox.showwarning(
            "Datos incompletos",
            "Debe ingresar una fecha."
        )
        return

    try:

        fecha_dt = datetime.strptime(
            fecha,
            "%d/%m/%Y"
        )

    except ValueError:

        messagebox.showerror(
            "Fecha incorrecta",
            "La fecha debe tener el formato DD/MM/AAAA."
        )
        return

    # --------------------------------------------------------
    # Verificar que el año coincida
    # --------------------------------------------------------

    if fecha_dt.year != int(anio):

        messagebox.showerror(
            "Año incorrecto",
            "El año de la fecha no coincide con el año seleccionado."
        )
        return

    # --------------------------------------------------------
    # Validar tipo
    # --------------------------------------------------------

    if not tipo:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe seleccionar un tipo."
        )
        return

    # --------------------------------------------------------
    # Validar descripción
    # --------------------------------------------------------

    if not descripcion:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe ingresar una descripción."
        )
        return

    # --------------------------------------------------------
    # Guardar
    # --------------------------------------------------------

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO dias_no_laborables (
                anio,
                fecha,
                tipo,
                descripcion
            )
            VALUES (?, ?, ?, ?)
        """, (
            int(anio),
            fecha,
            tipo,
            descripcion
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        messagebox.showerror(
            "Error",
            f"No se pudo guardar el día no laborable.\n\n{e}"
        )

        conn.close()
        return

    conn.close()

    # --------------------------------------------------------
    # Actualizar listado
    # --------------------------------------------------------

    cargar_dias_no_laborables(
        tree,
        int(anio)
    )

    # --------------------------------------------------------
    # Limpiar campos
    # --------------------------------------------------------

    fecha_var.set("")
    tipo_var.set("")
    descripcion_var.set("")

    messagebox.showinfo(
        "Guardado",
        "El día no laborable fue registrado correctamente."
    )
# ---------------------------------------------------------------------------

# ==========================================================================
#                   Seleccionar día no laborable
# ==========================================================================
def seleccionar_dia_no_laborable(
        event,
        tree,
        fecha_var,
        tipo_var,
        descripcion_var
    ):

        seleccion = tree.selection()

        if not seleccion:
            return

        item = tree.item(seleccion[0])

        valores = item["values"]

        if not valores:
            return

        # valores:
        # 0 = id
        # 1 = fecha
        # 2 = tipo
        # 3 = descripcion

        fecha_var.set(valores[1])
        tipo_var.set(valores[2])
        descripcion_var.set(valores[3])
# ---------------------------------------------------------------------------

# ===========================================================================
#                       Modificar día no laborable
# ===========================================================================
def modificar_dia_no_laborable(
    anio_var,
    fecha_var,
    tipo_var,
    descripcion_var,
    tree
):

    seleccion = tree.selection()

    if not seleccion:
        messagebox.showwarning(
            "Modificar",
            "Debe seleccionar un día no laborable de la lista."
        )
        return

    item = tree.item(seleccion[0])

    valores = item["values"]

    id_dia = valores[0]

    anio = anio_var.get().strip()
    fecha = fecha_var.get().strip()
    tipo = tipo_var.get().strip()
    descripcion = descripcion_var.get().strip()

    # --------------------------------------------------------
    # Validar fecha
    # --------------------------------------------------------

    try:

        fecha_dt = datetime.strptime(
            fecha,
            "%d/%m/%Y"
        )

    except ValueError:

        messagebox.showerror(
            "Fecha incorrecta",
            "La fecha debe tener el formato DD/MM/AAAA."
        )
        return

    # --------------------------------------------------------
    # Verificar año
    # --------------------------------------------------------

    if fecha_dt.year != int(anio):

        messagebox.showerror(
            "Año incorrecto",
            "El año de la fecha no coincide con el año seleccionado."
        )
        return

    # --------------------------------------------------------
    # Validar tipo
    # --------------------------------------------------------

    if not tipo:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe seleccionar un tipo."
        )
        return

    # --------------------------------------------------------
    # Validar descripción
    # --------------------------------------------------------

    if not descripcion:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe ingresar una descripción."
        )
        return

    # --------------------------------------------------------
    # Actualizar
    # --------------------------------------------------------

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE dias_no_laborables
            SET
                anio = ?,
                fecha = ?,
                tipo = ?,
                descripcion = ?
            WHERE id = ?
        """, (
            int(anio),
            fecha,
            tipo,
            descripcion,
            id_dia
        ))

        conn.commit()

    except Exception as e:

        conn.rollback()

        messagebox.showerror(
            "Error",
            f"No se pudo modificar el registro.\n\n{e}"
        )

        conn.close()
        return

    conn.close()

    # --------------------------------------------------------
    # Actualizar Treeview
    # --------------------------------------------------------

    cargar_dias_no_laborables(
        tree,
        int(anio)
    )

    # --------------------------------------------------------
    # Limpiar formulario
    # --------------------------------------------------------

    fecha_var.set("")
    tipo_var.set("")
    descripcion_var.set("")

    messagebox.showinfo(
        "Modificado",
        "El día no laborable fue modificado correctamente."
    )
# ---------------------------------------------------------------------------

# ===========================================================================
#                          Eliminar día no laborable
# ===========================================================================
def eliminar_dia_no_laborable(
    fecha_var,
    tipo_var,
    descripcion_var,
    tree
):



    # --------------------------------------------------------
    # Verificar selección
    # --------------------------------------------------------

    seleccion = tree.selection()

    if not seleccion:

        messagebox.showwarning(
            "Eliminar",
            "Debe seleccionar un día no laborable de la lista."
        )

        return

    # --------------------------------------------------------
    # Obtener datos seleccionados
    # --------------------------------------------------------

    item = tree.item(seleccion[0])

    valores = item["values"]

    id_dia = valores[0]
    fecha = valores[1]
    tipo = valores[2]
    descripcion = valores[3]

    # --------------------------------------------------------
    # PRIMERA CONFIRMACIÓN
    # --------------------------------------------------------

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Está seguro de eliminar este día no laborable?\n\n"
        f"Fecha: {fecha}\n"
        f"Tipo: {tipo}\n"
        f"Descripción: {descripcion}"
    )

    if not confirmar:
        return

    # --------------------------------------------------------
    # Eliminar
    # --------------------------------------------------------

    conn = conectar()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM dias_no_laborables
            WHERE id = ?
        """, (id_dia,))

        conn.commit()

    except Exception as e:

        conn.rollback()
        conn.close()

        messagebox.showerror(
            "Error",
            f"No se pudo eliminar el registro.\n\n{e}"
        )

        return

    conn.close()

    # --------------------------------------------------------
    # SEGUNDA CONFIRMACIÓN
    # --------------------------------------------------------

    messagebox.showinfo(
        "Eliminado",
        f"El día no laborable del {fecha} "
        f"fue eliminado correctamente.")

    # --------------------------------------------------------
    # Actualizar listado
    # --------------------------------------------------------

    anio_actual = int(fecha[-4:])

    cargar_dias_no_laborables(
        tree,
        anio_actual
    )

    # --------------------------------------------------------
    # Limpiar formulario
    # --------------------------------------------------------

    fecha_var.set("")
    tipo_var.set("")
    descripcion_var.set("")
# ---------------------------------------------------------------------------


# ====================== Ventana de Días No Laborables ======================
def ventana_dias_no_laborables():

    ventana = tk.Toplevel()

    ventana.title("Días No Laborables")
    ventana.option_add("*TCombobox*Listbox.font", ("Arial", 12))

    #ventana.geometry("1300x700")
    ventana.state("zoomed")

    ventana.resizable(True, True)


    # ========================================================
    # FRAME DATOS
    # ========================================================

    frame_datos = ttk.LabelFrame(
        ventana,
        text="Datos del Día No Laborable"
    )

    frame_datos.pack(
        fill="x",
        padx=10,
        pady=10
    )


    # ========================================================
    # VARIABLES
    # ========================================================

    anio_actual = datetime.now().year

    anio_var = tk.StringVar(
        value=str(anio_actual)
    )

    fecha_var = tk.StringVar()

    tipo_var = tk.StringVar()

    descripcion_var = tk.StringVar()


    # ========================================================
    # AÑO
    # ========================================================
    style = ttk.Style()

    style.configure("Valido.TEntry", foreground="black")
    style.configure("Error.TEntry", foreground="black")
    style.map("Error.TEntry",
            fieldbackground=[("!disabled", "#ffcccc")])  # rojo claro
    
    ttk.Label(
        frame_datos,
        text="Año:"
    ).grid(
        row=0,
        column=0,
        padx=5,
        pady=8,
        sticky="e"
    )

    anio_actual = datetime.now().year
    anio_var = tk.StringVar()

    combo_anio = ttk.Combobox(
        frame_datos,
        textvariable=anio_var,
        width=10,
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
        padx=5,
        pady=8,
        sticky="w"
    )
    combo_anio["values"] = ("2025", "2026", "2027")
    combo_anio.current(1)

    # ========================================================
    # FECHA
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Fecha:"
    ).grid(
        row=0,
        column=2,
        padx=15,
        pady=8,
        sticky="e"
    )

    ttk.Entry(
        frame_datos,
        textvariable=fecha_var,
        width=15,
        font=("Arial",12)
    ).grid(
        row=0,
        column=3,
        padx=5,
        pady=8,
        sticky="w"
    )


    # ========================================================
    # TIPO
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Tipo:"
    ).grid(
        row=1,
        column=0,
        padx=5,
        pady=8,
        sticky="e"
    )

    combo_tipo = ttk.Combobox(
        frame_datos,
        textvariable=tipo_var,
        width=25,
        state="readonly",
        font=("Arial",12),
        values=[
            "Feriado",
            "Asueto",
            "Jornada institucional",
            "Capacitación",
            "Suspensión de actividades",
            "Otro"
        ]        
    )

    combo_tipo.grid(
        row=1,
        column=1,
        padx=5,
        pady=8,
        sticky="w"
    )


    # ========================================================
    # DESCRIPCIÓN
    # ========================================================

    ttk.Label(
        frame_datos,
        text="Descripción:"
    ).grid(
        row=1,
        column=2,
        padx=15,
        pady=8,
        sticky="e"
    )

    ttk.Entry(
        frame_datos,
        textvariable=descripcion_var,
        width=50, font=("Arial",12)
    ).grid(
        row=1,
        column=3,
        padx=5,
        pady=8,
        sticky="w"
    )


    # ========================================================
    # FRAME LISTADO
    # ========================================================

    frame_lista = ttk.LabelFrame(
        ventana,
        text="Días No Laborables Registrados"
    )

    frame_lista.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )


    # ========================================================
    # TREEVIEW
    # ========================================================

    columnas = ("id", "fecha", "tipo", "descripcion")

    tree = ttk.Treeview(frame_lista, columns=columnas, show="headings")

    tree.heading("id", text="ID")

    tree.heading("fecha", text="Fecha" )

    tree.heading("tipo", text="Tipo")

    tree.heading("descripcion", text="Descripción" )

    tree.column("id", width=60, anchor="center")

    tree.column("fecha", width=120, anchor="center" )

    tree.column("tipo", width=220 )

    tree.column("descripcion", width=450 )

    tree.bind("<<TreeviewSelect>>", lambda event: seleccionar_dia_no_laborable(
            event,
            tree,
            fecha_var,
            tipo_var,
            descripcion_var
        )
    )

    # ========================================================
    # SCROLL VERTICAL
    # ========================================================

    scroll_vertical = ttk.Scrollbar(
        frame_lista,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scroll_vertical.set
    )


    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scroll_vertical.pack(
        side="right",
        fill="y"
    )


    # ========================================================
    # BOTONES
    # ========================================================

    frame_botones = ttk.Frame(
        ventana
    )

    frame_botones.pack(
        fill="x",
        padx=10,
        pady=10
    )


    ttk.Button(
        frame_botones,
        text="Nuevo"
    ).pack(
        side="left",
        padx=5
    )


    ttk.Button(
        frame_botones,
        text="Guardar",
        command=lambda: guardar_dia_no_laborable(
            anio_var,
            fecha_var,
            tipo_var,
            descripcion_var,
            tree )
    ).pack(
        side="left",
        padx=5
    )


    ttk.Button(
        frame_botones,
        text="Modificar",
        command=lambda: modificar_dia_no_laborable(
            anio_var,
            fecha_var,
            tipo_var,
            descripcion_var,
            tree
        )
    ).pack(
        side="left",
        padx=5
    )

    ttk.Button(
        frame_botones,
        text="Eliminar",
        command=lambda: eliminar_dia_no_laborable(
            fecha_var,
            tipo_var,
            descripcion_var,
            tree
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
    # CARGAR REGISTROS DEL AÑO ACTUAL
    # ========================================================

    cargar_dias_no_laborables(
        tree,
        int(anio_var.get())
    )
# -----------------------------------------------------------------------

