
# =====================================================
#              MÓDULO MANUAL DE USUARIO
# =====================================================

import os
import sys
from pathlib import Path
from tkinter import messagebox


# =====================================================
#              DETERMINAR CARPETA DE RECURSOS
# =====================================================

def obtener_carpeta_sge():

    """
    Devuelve la carpeta donde se encuentran
    los recursos de SGE.

    En desarrollo:
        utiliza la carpeta del archivo .py.

    En versión compilada con PyInstaller:
        utiliza la carpeta interna _internal.
    """

    if getattr(sys, "frozen", False):

        return Path(
            sys._MEIPASS
        )

    return Path(
        __file__
    ).resolve().parent


# =====================================================
#                  ABRIR MANUAL
# =====================================================

def abrir_manual(parent=None):

    try:

        carpeta_sge = obtener_carpeta_sge()

        archivo_manual = (
            carpeta_sge
            / "manual"
            / "Manual Usuario SGE.docx"
        )

        if not archivo_manual.exists():

            messagebox.showerror(
                "Manual de Usuario",
                "No se encontró el Manual de Usuario.\n\n"
                f"Ubicación buscada:\n{archivo_manual}",
                parent=parent
            )

            return

        os.startfile(
            str(archivo_manual)
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            "No fue posible abrir el Manual de Usuario.\n\n"
            f"{e}",
            parent=parent
        )


# =====================================================
#                    FIN DEL MÓDULO
# =====================================================
