import os
from pathlib import Path
from tkinter import messagebox


def abrir_manual(parent=None):

    try:

        carpeta_sge = Path(__file__).resolve().parent

        archivo_manual = carpeta_sge / "manual" / "Manual Usuario SGE.docx"

        if not archivo_manual.exists():

            messagebox.showerror(
                "Manual de Usuario",
                "No se encontró el Manual de Usuario.\n\n"
                f"Ubicación buscada:\n{archivo_manual}",
                parent=parent
            )

            return

        os.startfile(archivo_manual)

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No fue posible abrir el Manual de Usuario.\n\n{e}",
            parent=parent
        )