# ============================================================
# SISTEMA DE GESTIÓN EDUCATIVA
# Resumen Anual de Inasistencias
# ============================================================

from logging import root
import tkinter as tk
from tkinter import ttk


# ============================================================
# VENTANA
# ============================================================

def ventana_resumen():

    ventana = tk.Toplevel()

    ventana.title("Resumen Anual de Inasistencias")

    ventana.geometry("1200x750")

    ventana.resizable(True, True)

    # ========================================================
    # FRAME SUPERIOR
    # ========================================================

    frame_superior = ttk.LabelFrame(
        ventana,
        text="Resumen del Docente"
    )

    frame_superior.pack(
        fill="x",
        padx=10,
        pady=10
    )

    # ========================================================
    # FRAME DATOS DOCENTE
    # ========================================================

    frame_docente = ttk.LabelFrame(
        ventana,
        text="Datos del Docente"
    )

    frame_docente.pack(
        fill="x",
        padx=10,
        pady=5
    )

    # ========================================================
    # FRAME CARGOS
    # ========================================================

    frame_cargos = ttk.LabelFrame(
        ventana,
        text="Cargos"
    )

    frame_cargos.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    # ========================================================
    # FRAME MODULOS
    # ========================================================

    frame_modulos = ttk.LabelFrame(
        ventana,
        text="Materias"
    )

    frame_modulos.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    # ========================================================
    # FRAME LICENCIAS
    # ========================================================

    frame_licencias = ttk.LabelFrame(
        ventana,
        text="Detalle de Inasistencias"
    )

    frame_licencias.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    # ========================================================
    # BOTON CERRAR
    # ========================================================

    ttk.Button(
        ventana,
        text="Cerrar",
        command=ventana.destroy
    ).pack(
        pady=10
    )

    if __name__ == "__main__":
        root = tk.Tk()
        root.withdraw()
        ventana_resumen()

root.mainloop()