# =====================================================

# INSTALADOR SGE

# Sistema de Gestión Escolar

# =====================================================

import tkinter as tk
from tkinter import messagebox
import shutil
import sys
from pathlib import Path

# =====================================================

# RUTA PRINCIPAL DEL PROYECTO

# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================

# AGREGAR PROYECTO A PYTHON

# =====================================================

if str(BASE_DIR) not in sys.path:sys.path.insert(0, str(BASE_DIR))

# =====================================================

# IMPORTAR HUELLA DEL EQUIPO

# =====================================================

from Licenciamiento.huella_equipo import obtener_huella_equipo

# =====================================================

# RUTAS

# =====================================================

CARPETA_SGE_COMPILADO = BASE_DIR / "dist" / "SGE"

CARPETA_INSTALACION = Path("C:/SGE")

ARCHIVO_SGE = CARPETA_INSTALACION / "SGE.exe"

# =====================================================

# OBTENER HUELLA

# =====================================================

huella_equipo = obtener_huella_equipo()

# =====================================================

# FUNCIÓN INSTALAR SGE

# =====================================================

def instalar_y_activar():


    institucion = entrada_institucion.get().strip()

    localidad = entrada_localidad.get().strip()

    provincia = entrada_provincia.get().strip()

    tipo_licencia = tipo_var.get()


    # -------------------------------------------------
    # VALIDAR INSTITUCIÓN
    # -------------------------------------------------

    if not institucion:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe ingresar la institución."
        )

        entrada_institucion.focus()

        return


# -------------------------------------------------
# VALIDAR LOCALIDAD
# -------------------------------------------------

    if not localidad:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe ingresar la localidad."
        )

        entrada_localidad.focus()

        return


# -------------------------------------------------
# VALIDAR PROVINCIA
# -------------------------------------------------

    if not provincia:

        messagebox.showwarning(
            "Datos incompletos",
            "Debe ingresar la provincia."
        )

        entrada_provincia.focus()

        return


# -------------------------------------------------
# VERIFICAR CARPETA DEL SGE COMPILADO
# -------------------------------------------------

    if not CARPETA_SGE_COMPILADO.exists():

        messagebox.showerror(
            "SGE no encontrado",
            "No se encontró la versión compilada de SGE.\n\n"
            "Se esperaba encontrar:\n\n"
            f"{CARPETA_SGE_COMPILADO}"
        )

        return


# -------------------------------------------------
# VERIFICAR SGE.EXE
# -------------------------------------------------

    archivo_origen = (
        CARPETA_SGE_COMPILADO / "SGE.exe"
    )


    if not archivo_origen.exists():

        messagebox.showerror(
            "SGE no encontrado",
            "La carpeta de SGE existe, "
            "pero no se encontró SGE.exe.\n\n"
            f"{archivo_origen}"
        )

        return


# -------------------------------------------------
# MOSTRAR CONFIRMACIÓN
# -------------------------------------------------

    mensaje = (

        "Se instalará SGE en:\n\n"

        f"{CARPETA_INSTALACION}\n\n"

        "DATOS DE LA INSTALACIÓN\n\n"

        f"Institución: {institucion}\n"

        f"Localidad: {localidad}\n"

        f"Provincia: {provincia}\n"

        f"Tipo de licencia: "
        f"{tipo_licencia.capitalize()}\n\n"

        "EQUIPO AUTORIZADO\n\n"

        f"{huella_equipo}\n\n"

        "¿Desea continuar?"
    )


    confirmar = messagebox.askyesno(
        "Confirmar instalación",
        mensaje
    )


    if not confirmar:

        return


# -------------------------------------------------
# REALIZAR INSTALACIÓN
# -------------------------------------------------

try:

    # -------------------------------------------------
    # CREAR CARPETA C:\SGE
    # -------------------------------------------------

    CARPETA_INSTALACION.mkdir(
        parents=True,
        exist_ok=True
    )


    # -------------------------------------------------
    # ARCHIVOS QUE NO SE DEBEN COPIAR
    # -------------------------------------------------

    archivos_excluidos = {
        "Licencia_SGE.lic",
        "Licencia_SGE_Vencida.lic"
    }


    # -------------------------------------------------
    # COPIAR TODO EL CONTENIDO DE DIST\SGE
    # -------------------------------------------------

    for elemento in CARPETA_SGE_COMPILADO.iterdir():

        # ---------------------------------------------
        # OMITIR ARCHIVOS DE LICENCIA
        # ---------------------------------------------

        if elemento.name in archivos_excluidos:

            continue


        destino = (
            CARPETA_INSTALACION / elemento.name
        )


        # ---------------------------------------------
        # COPIAR CARPETAS
        # ---------------------------------------------

        if elemento.is_dir():

            shutil.copytree(
                elemento,
                destino,
                dirs_exist_ok=True
            )


        # ---------------------------------------------
        # COPIAR ARCHIVOS
        # ---------------------------------------------

        else:

            shutil.copy2(
                elemento,
                destino
            )


    # -------------------------------------------------
    # COMPROBAR QUE SGE.EXE FUE INSTALADO
    # -------------------------------------------------

    if not ARCHIVO_SGE.exists():

        raise RuntimeError(
            "La instalación terminó, "
            "pero SGE.exe no fue encontrado "
            "en C:\\SGE."
        )


    # -------------------------------------------------
    # INSTALACIÓN CORRECTA
    # -------------------------------------------------

    messagebox.showinfo(
        "Instalación realizada",

        "SGE fue instalado correctamente.\n\n"

        f"Ubicación:\n{CARPETA_INSTALACION}\n\n"

        "La licencia todavía no fue activada.\n\n"

        "La activación automática se incorporará "
        "en la siguiente etapa."
    )


# -------------------------------------------------
# ERROR DE PERMISOS
# -------------------------------------------------

except PermissionError:

    messagebox.showerror(
        "Permiso insuficiente",

        "Windows no permitió escribir en:\n\n"

        "C:\\SGE\n\n"

        "Ejecute el instalador como administrador."
    )


# -------------------------------------------------
# OTRO ERROR
# -------------------------------------------------

except Exception as e:

    messagebox.showerror(
        "Error de instalación",

        "No se pudo instalar SGE.\n\n"

        f"Detalle:\n{e}"
    )


# =====================================================

# VENTANA PRINCIPAL

# =====================================================

root = tk.Tk()

root.title(
"Instalación SGE"
)

root.geometry(
"650x650"
)

root.resizable(
False,
False
)

# =====================================================

# TÍTULO

# =====================================================

tk.Label(
root,

text="INSTALACIÓN SGE",

font=(
    "Arial",
    22,
    "bold"
)


).pack(
pady=(
30,
5
)
)

tk.Label(
root,


text="Sistema de Gestión Escolar",

font=(
    "Arial",
    12
)


).pack(
pady=(
0,
25
)
)

# =====================================================

# MARCO DE DATOS

# =====================================================

marco_datos = tk.Frame(
root
)

marco_datos.pack(
padx=40,


fill="x"


)

# =====================================================

# INSTITUCIÓN

# =====================================================

tk.Label(
marco_datos,


text="Institución:",

font=(
    "Arial",
    11,
    "bold"
)


).pack(
anchor="w"
)

entrada_institucion = tk.Entry(
marco_datos,


font=(
    "Arial",
    11
)


)

entrada_institucion.pack(
fill="x",


pady=(
    5,
    15
)


)

# =====================================================

# LOCALIDAD

# =====================================================

tk.Label(
marco_datos,


text="Localidad:",

font=(
    "Arial",
    11,
    "bold"
)


).pack(
anchor="w"
)

entrada_localidad = tk.Entry(
marco_datos,


font=(
    "Arial",
    11
)


)

entrada_localidad.pack(
fill="x",


pady=(
    5,
    15
)


)

# =====================================================

# PROVINCIA

# =====================================================

tk.Label(
marco_datos,


text="Provincia:",

font=(
    "Arial",
    11,
    "bold"
)


).pack(
anchor="w"
)

entrada_provincia = tk.Entry(
marco_datos,


font=(
    "Arial",
    11
)


)

entrada_provincia.pack(
fill="x",


pady=(
    5,
    20
)


)

# =====================================================

# TIPO DE LICENCIA

# =====================================================

tk.Label(
marco_datos,


text="Tipo de licencia:",

font=(
    "Arial",
    11,
    "bold"
)


).pack(
anchor="w"
)

tipo_var = tk.StringVar(
value="permanente"
)

marco_tipo = tk.Frame(
marco_datos
)

marco_tipo.pack(
anchor="w",


pady=(
    5,
    20
)


)

# -----------------------------------------------------

# PRUEBA

# -----------------------------------------------------

tk.Radiobutton(
marco_tipo,


text="Prueba",

variable=tipo_var,

value="prueba",

font=(
    "Arial",
    10
)


).pack(
side="left",


padx=(
    0,
    20
)


)

# -----------------------------------------------------

# ANUAL

# -----------------------------------------------------

tk.Radiobutton(
marco_tipo,


text="Anual",

variable=tipo_var,

value="anual",

font=(
    "Arial",
    10
)


).pack(
side="left",


padx=(
    0,
    20
)


)

# -----------------------------------------------------

# PERMANENTE

# -----------------------------------------------------

tk.Radiobutton(
marco_tipo,


text="Permanente",

variable=tipo_var,

value="permanente",

font=(
    "Arial",
    10
)


).pack(
side="left"
)

# =====================================================

# HUELLA DEL EQUIPO

# =====================================================

tk.Label(
marco_datos,

text="Huella del equipo:",

font=(
    "Arial",
    11,
    "bold"
)


).pack(
anchor="w"
)

huella_equipo = (
obtener_huella_equipo()
)

entrada_huella = tk.Entry(
marco_datos,


font=(
    "Consolas",
    9
)


)

entrada_huella.pack(
fill="x",

pady=(
    5,
    5
)


)

entrada_huella.insert(
0,


    huella_equipo


)

entrada_huella.config(
state="readonly"
)

tk.Label(
marco_datos,


text=(
    "La licencia quedará vinculada "
    "automáticamente a este equipo."
),

font=(
    "Arial",
    9
)


).pack(
anchor="w",

pady=(
    0,
    25
)


)

# =====================================================

# BOTÓN INSTALAR

# =====================================================

tk.Button(
root,


text="INSTALAR SGE",

font=(
    "Arial",
    12,
    "bold"
),

width=25,

height=2,

command=instalar_y_activar


).pack(
pady=10
)

# =====================================================

# INFORMACIÓN

# =====================================================

tk.Label(
root,


text="La instalación se realizará en C:\\SGE",

font=(
    "Arial",
    9
)


).pack(
pady=(
10,
5
)
)

# =====================================================

# INICIO DEL PROGRAMA

# =====================================================

root.mainloop()

