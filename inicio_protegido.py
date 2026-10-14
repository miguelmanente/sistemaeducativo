# ============================================================
# ARRANQUE PROTEGIDO DEL SGE
# No modifica index.py: valida la licencia y después lo ejecuta.
# ============================================================

import os
import runpy
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from Licenciamiento.licencia import analizar_licencia


CARPETA_PROGRAMA = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
CARPETA_DATOS = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "SGE"
ARCHIVO_LICENCIA = CARPETA_DATOS / "Licencia_SGE.lic"
ARCHIVO_ACTIVACION = CARPETA_PROGRAMA / "ActivacionSGE.exe"
if not ARCHIVO_ACTIVACION.exists() and CARPETA_PROGRAMA.parent != CARPETA_PROGRAMA:
    # Durante las pruebas, ActivacionSGE.exe se compila junto a la carpeta SGE.
    ARCHIVO_ACTIVACION = CARPETA_PROGRAMA.parent / "ActivacionSGE.exe"


def mostrar_error_y_ofrecer_activacion(mensaje):
    raiz = tk.Tk()
    raiz.withdraw()
    try:
        abrir = messagebox.askyesno(
            "SGE: activación requerida",
            mensaje + "\n\n¿Querés abrir la herramienta de activación?",
            parent=raiz,
        )
        if abrir:
            if ARCHIVO_ACTIVACION.exists():
                subprocess.Popen(
                    [str(ARCHIVO_ACTIVACION)],
                    cwd=str(CARPETA_PROGRAMA),
                )
            else:
                messagebox.showerror(
                    "SGE",
                    "No se encontró ActivacionSGE.exe. Ejecutá la activación "
                    "desde el menú Inicio o repará la instalación.",
                    parent=raiz,
                )
    finally:
        raiz.destroy()


def licencia_valida():
    if not ARCHIVO_LICENCIA.is_file():
        mostrar_error_y_ofrecer_activacion(
            "El SGE todavía no está activado."
        )
        return False

    try:
        valida, motivo = analizar_licencia(str(ARCHIVO_LICENCIA))
    except Exception as exc:
        mostrar_error_y_ofrecer_activacion(
            f"No se pudo comprobar la licencia.\n\n{exc}"
        )
        return False

    if not valida:
        mostrar_error_y_ofrecer_activacion(
            "La licencia no es válida, está vencida o no corresponde a este equipo.\n\n"
            f"Motivo: {motivo}"
        )
        return False

    return True


if __name__ == "__main__":
    if licencia_valida():
        # index se incluye explícitamente al compilar con --hidden-import index.
        # run_name='__main__' conserva el comportamiento del entrypoint original.
        runpy.run_module("index", run_name="__main__")
