# ============================================================
# SISTEMA DE GESTIÓN EDUCATIVA
# Gestión de Días No Laborables
# ============================================================

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from negocio.motor_inasistencias import obtener_dias_no_laborables


# ============================================================
# VENTANA
# ============================================================

def ventana_dias_no_laborables():

    ventana = tk.Toplevel()

    ventana.title("Días No Laborables")

    ventana.geometry("1000x650")

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

    combo_anio = ttk.Combobox(
        frame_datos,
        textvariable=anio_var,
        width=10,
        state="readonly",
        values=[
            str(anio_actual - 1),
            str(anio_actual),
            str(anio_actual + 1)
        ]
    )

    combo_anio.grid(
        row=0,
        column=1,
        padx=5,
        pady=8,
        sticky="w"
    )


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
        width=15
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
        width=50
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

    columnas = (
        "id",
        "fecha",
        "tipo",
        "descripcion"
    )

    tree = ttk.Treeview(
        frame_lista,
        columns=columnas,
        show="headings"
    )

    tree.heading(
        "id",
        text="ID"
    )

    tree.heading(
        "fecha",
        text="Fecha"
    )

    tree.heading(
        "tipo",
        text="Tipo"
    )

    tree.heading(
        "descripcion",
        text="Descripción"
    )


    tree.column(
        "id",
        width=60,
        anchor="center"
    )

    tree.column(
        "fecha",
        width=120,
        anchor="center"
    )

    tree.column(
        "tipo",
        width=220
    )

    tree.column(
        "descripcion",
        width=450
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
        text="Guardar"
    ).pack(
        side="left",
        padx=5
    )


    ttk.Button(
        frame_botones,
        text="Modificar"
    ).pack(
        side="left",
        padx=5
    )


    ttk.Button(
        frame_botones,
        text="Eliminar"
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

    datos = obtener_dias_no_laborables(
        int(anio_var.get())
    )

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