# ============================================================
# ACTIVACIÓN SGE PARA LA ESCUELA
# Genera una solicitud y permite importar la licencia recibida.
# No contiene ni utiliza la clave privada.
# ============================================================

import json
import os
import re
import shutil
import sys
import uuid
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from Licenciamiento.huella_equipo import obtener_huella_equipo
from Licenciamiento.licencia import analizar_licencia


NOMBRE_APLICACION = "Activación del SGE"
CARPETA_PROGRAMA = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent
)
CARPETA_DATOS = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "SGE"
ARCHIVO_LICENCIA_INSTALADA = CARPETA_DATOS / "Licencia_SGE.lic"


def construir_solicitud(institucion, localidad, provincia):
    """Construye la solicitud con la huella real del equipo actual."""
    institucion = institucion.strip()
    localidad = localidad.strip()
    provincia = provincia.strip()

    if not institucion or not localidad or not provincia:
        raise ValueError("Completá institución, localidad y provincia.")

    huella = str(obtener_huella_equipo()).strip()
    if not re.fullmatch(r"[A-Fa-f0-9]{64}", huella):
        raise ValueError(
            "La huella calculada no tiene el formato esperado. "
            "No se generó la solicitud."
        )

    return {
        "producto": "SGE",
        "id_solicitud": str(uuid.uuid4()),
        "institucion": institucion,
        "localidad": localidad,
        "provincia": provincia,
        "fecha_solicitud": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "huella_equipo": huella,
    }


def guardar_solicitud():
    try:
        solicitud = construir_solicitud(
            entrada_institucion.get(),
            entrada_localidad.get(),
            entrada_provincia.get(),
        )
    except Exception as exc:
        messagebox.showerror(NOMBRE_APLICACION, str(exc), parent=ventana)
        return

    destino = filedialog.asksaveasfilename(
        parent=ventana,
        title="Guardar solicitud de licencia",
        initialfile="Solicitud_SGE.dat",
        defaultextension=".dat",
        filetypes=[("Solicitud SGE", "*.dat"), ("Todos los archivos", "*.*")],
    )
    if not destino:
        return

    try:
        with open(destino, "w", encoding="utf-8") as archivo:
            json.dump(solicitud, archivo, ensure_ascii=False, indent=4)
        messagebox.showinfo(
            NOMBRE_APLICACION,
            "Solicitud guardada correctamente.\n\n"
            f"Archivo:\n{destino}\n\n"
            "Enviá ese archivo al responsable del SGE para que emita tu licencia.",
            parent=ventana,
        )
    except Exception as exc:
        messagebox.showerror(
            NOMBRE_APLICACION,
            f"No se pudo guardar la solicitud.\n\n{exc}",
            parent=ventana,
        )


def importar_licencia():
    origen = filedialog.askopenfilename(
        parent=ventana,
        title="Seleccionar licencia SGE recibida",
        filetypes=[("Licencia SGE", "*.lic"), ("Todos los archivos", "*.*")],
    )
    if not origen:
        return

    # Validar la licencia antes de instalarla. La validación incluye firma,
    # estructura, vencimiento y huella del equipo según el módulo existente.
    try:
        valida, motivo = analizar_licencia(origen)
    except Exception as exc:
        messagebox.showerror(
            NOMBRE_APLICACION,
            f"No se pudo verificar el archivo de licencia.\n\n{exc}",
            parent=ventana,
        )
        return

    if not valida:
        messagebox.showerror(
            NOMBRE_APLICACION,
            "La licencia no es válida para este equipo.\n\n"
            f"Motivo: {motivo}",
            parent=ventana,
        )
        return

    try:
        CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, ARCHIVO_LICENCIA_INSTALADA)

        # Verificar también la copia ya instalada.
        valida_copia, motivo_copia = analizar_licencia(
            str(ARCHIVO_LICENCIA_INSTALADA)
        )
        if not valida_copia:
            try:
                ARCHIVO_LICENCIA_INSTALADA.unlink(missing_ok=True)
            except OSError:
                pass
            messagebox.showerror(
                NOMBRE_APLICACION,
                "La licencia copiada no superó la verificación final.\n\n"
                f"Motivo: {motivo_copia}",
                parent=ventana,
            )
            return

        messagebox.showinfo(
            NOMBRE_APLICACION,
            "¡El SGE quedó activado correctamente!\n\n"
            "Ya podés cerrar esta ventana y abrir el acceso directo SGE.",
            parent=ventana,
        )
    except Exception as exc:
        messagebox.showerror(
            NOMBRE_APLICACION,
            "No se pudo instalar la licencia.\n\n"
            f"Comprobá que la carpeta de datos tenga permisos de escritura.\n\n{exc}",
            parent=ventana,
        )


ventana = tk.Tk()
ventana.title(NOMBRE_APLICACION)
ventana.geometry("600x430")
ventana.minsize(560, 400)
ventana.resizable(True, True)

contenedor = tk.Frame(ventana, padx=24, pady=20)
contenedor.pack(fill="both", expand=True)

tk.Label(
    contenedor,
    text="Activación del Sistema de Gestión Educativa",
    font=("Segoe UI", 15, "bold"),
    wraplength=540,
    justify="center",
).pack(fill="x", pady=(0, 8))

tk.Label(
    contenedor,
    text=(
        "Primero guardá la solicitud y enviala al responsable del SGE. "
        "Cuando recibas tu archivo de licencia, volvé a esta ventana e importalo."
    ),
    font=("Segoe UI", 10),
    wraplength=540,
    justify="left",
).pack(fill="x", pady=(0, 16))

formulario = tk.Frame(contenedor)
formulario.pack(fill="x")

for fila, (etiqueta, variable_name) in enumerate(
    [
        ("Institución:", "institucion"),
        ("Localidad:", "localidad"),
        ("Provincia:", "provincia"),
    ]
):
    tk.Label(formulario, text=etiqueta, font=("Segoe UI", 10)).grid(
        row=fila, column=0, sticky="w", padx=(0, 12), pady=6
    )
    campo = tk.Entry(formulario, font=("Segoe UI", 10))
    campo.grid(row=fila, column=1, sticky="ew", pady=6)
    formulario.grid_columnconfigure(1, weight=1)
    if variable_name == "institucion":
        entrada_institucion = campo
    elif variable_name == "localidad":
        entrada_localidad = campo
    else:
        entrada_provincia = campo

botones = tk.Frame(contenedor)
botones.pack(fill="x", pady=(20, 12))

tk.Button(
    botones,
    text="Guardar solicitud",
    command=guardar_solicitud,
    font=("Segoe UI", 10, "bold"),
    padx=12,
    pady=7,
).pack(side="left", expand=True, fill="x", padx=(0, 6))

tk.Button(
    botones,
    text="Importar licencia recibida",
    command=importar_licencia,
    font=("Segoe UI", 10, "bold"),
    padx=12,
    pady=7,
).pack(side="left", expand=True, fill="x", padx=(6, 0))

estado = "Activado" if ARCHIVO_LICENCIA_INSTALADA.exists() else "Pendiente de activación"
tk.Label(
    contenedor,
    text=f"Estado local: {estado}",
    font=("Segoe UI", 9),
    fg="#444444",
).pack(anchor="w", pady=(4, 0))

ventana.mainloop()
