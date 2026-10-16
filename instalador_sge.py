# ============================================================
# ACTIVACIÓN DEL SGE
# Herramienta para uso del técnico que instala el sistema.
# NO contiene ni utiliza la clave privada de firma.
# ============================================================

import json
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from Licenciamiento.huella_equipo import obtener_huella_equipo
from Licenciamiento.licencia import analizar_licencia

NOMBRE_APLICACION = "Activación SGE"

if getattr(sys, "frozen", False):
    CARPETA_INSTALACION = Path(sys.executable).resolve().parent
else:
    CARPETA_INSTALACION = Path(__file__).resolve().parent

ARCHIVO_SGE = CARPETA_INSTALACION / "SGE.exe"
ARCHIVO_LICENCIA = CARPETA_INSTALACION / "Licencia_SGE.lic"

try:
    HUELLA_EQUIPO = str(obtener_huella_equipo()).strip().upper()
    if not re.fullmatch(r"[A-F0-9]{64}", HUELLA_EQUIPO):
        raise ValueError("La huella obtenida no tiene 64 caracteres hexadecimales.")
    ERROR_HUELLA = None
except Exception as exc:
    HUELLA_EQUIPO = ""
    ERROR_HUELLA = str(exc)


def construir_solicitud():
    institucion = entrada_institucion.get().strip()
    localidad = entrada_localidad.get().strip()
    provincia = entrada_provincia.get().strip()

    if not institucion or not localidad or not provincia:
        raise ValueError("Completá institución, localidad y provincia.")
    if not HUELLA_EQUIPO:
        raise ValueError("No se pudo obtener la huella de este equipo.\n\n" + (ERROR_HUELLA or ""))

    return {
        "producto": "SGE",
        "id_solicitud": str(uuid.uuid4()),
        "institucion": institucion,
        "localidad": localidad,
        "provincia": provincia,
        "fecha_solicitud": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "huella_equipo": HUELLA_EQUIPO,
    }


def guardar_solicitud():
    try:
        solicitud = construir_solicitud()
    except Exception as exc:
        messagebox.showerror(NOMBRE_APLICACION, str(exc), parent=ventana)
        return

    destino = filedialog.asksaveasfilename(
        parent=ventana,
        title="Guardar solicitud para emitir la licencia",
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
            "Solicitud creada correctamente.\n\n"
            f"Archivo:\n{destino}\n\n"
            "Llevá el archivo al equipo donde está tu Administrador de Licencias. "
            "Importalo allí y emití la licencia. Después traé el archivo .lic "
            "emitido e importalo en esta ventana.\n\n"
            "Esta herramienta no firma licencias y no contiene la clave privada.",
            parent=ventana,
        )
        actualizar_estado()
    except Exception as exc:
        messagebox.showerror(NOMBRE_APLICACION, f"No se pudo guardar la solicitud.\n\n{exc}", parent=ventana)


def importar_licencia():
    origen = filedialog.askopenfilename(
        parent=ventana,
        title="Seleccionar licencia emitida por el Administrador de Licencias",
        filetypes=[("Licencia SGE", "*.lic"), ("Todos los archivos", "*.*")],
    )
    if not origen:
        return

    try:
        valida, motivo = analizar_licencia(str(origen))
    except Exception as exc:
        messagebox.showerror(NOMBRE_APLICACION, f"No se pudo analizar la licencia.\n\n{exc}", parent=ventana)
        return

    if not valida:
        messagebox.showerror(
            NOMBRE_APLICACION,
            "La licencia no es válida para este equipo.\n\n"
            f"Motivo: {motivo}\n\n"
            "No se reemplazó ninguna licencia instalada.",
            parent=ventana,
        )
        return

    respaldo = CARPETA_INSTALACION / "Licencia_SGE.lic.bak"
    habia_anterior = ARCHIVO_LICENCIA.exists()

    if habia_anterior:
        confirmar = messagebox.askyesno(
            NOMBRE_APLICACION,
            "Ya existe una licencia en la carpeta del SGE.\n\n"
            "¿Querés reemplazarla por la licencia seleccionada?",
            parent=ventana,
        )
        if not confirmar:
            return

    try:
        if habia_anterior:
            shutil.copy2(ARCHIVO_LICENCIA, respaldo)
        shutil.copy2(origen, ARCHIVO_LICENCIA)

        valida_copia, motivo_copia = analizar_licencia(str(ARCHIVO_LICENCIA))
        if not valida_copia:
            if habia_anterior and respaldo.exists():
                shutil.copy2(respaldo, ARCHIVO_LICENCIA)
            else:
                ARCHIVO_LICENCIA.unlink(missing_ok=True)
            messagebox.showerror(
                NOMBRE_APLICACION,
                "La licencia copiada no superó la verificación final.\n\n"
                f"Motivo: {motivo_copia}\n\n"
                "Se restauró la licencia anterior, si existía.",
                parent=ventana,
            )
            return

        messagebox.showinfo(
            NOMBRE_APLICACION,
            "¡SGE activado correctamente!\n\n"
            f"Licencia instalada en:\n{ARCHIVO_LICENCIA}\n\n"
            "Ya podés iniciar SGE.",
            parent=ventana,
        )
        actualizar_estado()
    except PermissionError:
        messagebox.showerror(
            NOMBRE_APLICACION,
            "Windows no permitió guardar la licencia en la carpeta del SGE.\n\n"
            "Volvé a abrir esta herramienta como administrador y repetí la importación.",
            parent=ventana,
        )
    except Exception as exc:
        messagebox.showerror(NOMBRE_APLICACION, f"No se pudo instalar la licencia.\n\n{exc}", parent=ventana)


def licencia_instalada_valida():
    if not ARCHIVO_LICENCIA.is_file():
        return False, "No hay una licencia instalada junto a SGE.exe."
    try:
        return analizar_licencia(str(ARCHIVO_LICENCIA))
    except Exception as exc:
        return False, str(exc)


def iniciar_sge():
    valida, motivo = licencia_instalada_valida()
    if not valida:
        messagebox.showwarning(
            NOMBRE_APLICACION,
            "Primero importá una licencia válida.\n\n" + str(motivo),
            parent=ventana,
        )
        return
    if not ARCHIVO_SGE.is_file():
        messagebox.showerror(
            NOMBRE_APLICACION,
            f"No se encontró SGE.exe en:\n{ARCHIVO_SGE}",
            parent=ventana,
        )
        return
    try:
        subprocess.Popen([str(ARCHIVO_SGE)], cwd=str(CARPETA_INSTALACION))
    except Exception as exc:
        messagebox.showerror(NOMBRE_APLICACION, f"No se pudo iniciar SGE.\n\n{exc}", parent=ventana)


def actualizar_estado():
    valida, motivo = licencia_instalada_valida()
    if valida:
        etiqueta_estado.config(text="Estado: ACTIVADO", fg="#176534")
    else:
        etiqueta_estado.config(text="Estado: PENDIENTE DE ACTIVACIÓN", fg="#8A4B08")


ventana = tk.Tk()
ventana.title("SGE - Activación")
ventana.geometry("680x570")
ventana.minsize(620, 520)
ventana.resizable(True, True)

contenedor = tk.Frame(ventana, padx=24, pady=18)
contenedor.pack(fill="both", expand=True)

tk.Label(
    contenedor,
    text="ACTIVACIÓN DEL SGE",
    font=("Segoe UI", 18, "bold"),
).pack(pady=(0, 4))

tk.Label(
    contenedor,
    text=(
        "Herramienta para el técnico instalador. Generá la solicitud del equipo; "
        "emití la licencia con el Administrador de Licencias en tu equipo emisor "
        "y luego importá el archivo .lic aquí."
    ),
    font=("Segoe UI", 10),
    wraplength=600,
    justify="center",
).pack(fill="x", pady=(0, 18))

formulario = tk.LabelFrame(contenedor, text="Datos de la institución", padx=16, pady=12, font=("Segoe UI", 10, "bold"))
formulario.pack(fill="x")

for fila, (etiqueta, nombre) in enumerate([
    ("Institución:", "institucion"),
    ("Localidad:", "localidad"),
    ("Provincia:", "provincia"),
]):
    tk.Label(formulario, text=etiqueta, font=("Segoe UI", 10)).grid(row=fila, column=0, sticky="w", padx=(0, 12), pady=7)
    campo = tk.Entry(formulario, font=("Segoe UI", 10))
    campo.grid(row=fila, column=1, sticky="ew", pady=7)
    formulario.grid_columnconfigure(1, weight=1)
    if nombre == "institucion":
        entrada_institucion = campo
    elif nombre == "localidad":
        entrada_localidad = campo
    else:
        entrada_provincia = campo

huella_marco = tk.LabelFrame(contenedor, text="Equipo autorizado", padx=12, pady=8, font=("Segoe UI", 10, "bold"))
huella_marco.pack(fill="x", pady=(14, 0))
tk.Label(huella_marco, text="Huella del equipo:", font=("Segoe UI", 9)).pack(anchor="w")
entrada_huella = tk.Entry(huella_marco, font=("Consolas", 9), state="readonly")
entrada_huella.pack(fill="x", pady=(5, 0))
entrada_huella.config(state="normal")
entrada_huella.insert(0, HUELLA_EQUIPO or ("No disponible: " + (ERROR_HUELLA or "error")))
entrada_huella.config(state="readonly")

botones = tk.Frame(contenedor)
botones.pack(fill="x", pady=(18, 10))

tk.Button(botones, text="1. GUARDAR SOLICITUD", command=guardar_solicitud, font=("Segoe UI", 10, "bold"), padx=10, pady=9).pack(fill="x", pady=4)
tk.Button(botones, text="2. IMPORTAR LICENCIA EMITIDA", command=importar_licencia, font=("Segoe UI", 10, "bold"), padx=10, pady=9).pack(fill="x", pady=4)
tk.Button(botones, text="INICIAR SGE", command=iniciar_sge, font=("Segoe UI", 10, "bold"), padx=10, pady=9).pack(fill="x", pady=4)

etiqueta_estado = tk.Label(contenedor, text="", font=("Segoe UI", 10, "bold"))
etiqueta_estado.pack(anchor="w", pady=(8, 0))
tk.Label(contenedor, text="SGE - Sistema de Gestión Educativa", font=("Segoe UI", 9)).pack(side="bottom", pady=(10, 0))

actualizar_estado()
ventana.mainloop()
