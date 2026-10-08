# =====================================================
# INSTALADOR SGE
# INSTALACIÓN Y ACTIVACIÓN DEL SISTEMA
# =====================================================

import tkinter as tk
from tkinter import messagebox

import subprocess
import sys
import uuid
import traceback

from pathlib import Path
from datetime import datetime


# =====================================================
# CONFIGURACIÓN DE RUTAS
# =====================================================

#BASE_DIR = Path(__file__).resolve().parent.parent

#if str(BASE_DIR) not in sys.path:
    #sys.path.insert(0, str(BASE_DIR))


#CARPETA_ADMINISTRADOR = (
    #BASE_DIR / "AdministradorLicencias")

#if str(CARPETA_ADMINISTRADOR) not in sys.path:sys.path.insert(0, str(CARPETA_ADMINISTRADOR))

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# =====================================================
# IMPORTACIONES SGE
# =====================================================

from Licenciamiento.huella_equipo import (
    obtener_huella_equipo
)

from Licenciamiento.licencia import (
    analizar_licencia
)

from generar_licencia import (
    generar_licencia_desde_datos
)


# =====================================================
# RUTAS DEL SISTEMA
# =====================================================

#CARPETA_INSTALACION = Path("C:/SGE")
CARPETA_INSTALACION = BASE_DIR

ARCHIVO_SGE = (
    CARPETA_INSTALACION
    / "SGE.exe"
)

ARCHIVO_LICENCIA = (
    CARPETA_INSTALACION
    / "Licencia_SGE.lic"
)


# =====================================================
# DATOS DEL EQUIPO
# =====================================================

try:

    huella_equipo = obtener_huella_equipo()

except Exception as e:

    print("ERROR AL OBTENER HUELLA DEL EQUIPO:")
    print(e)

    huella_equipo = ""


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def verificar_sge_instalado():
    """
    Verifica que Inno Setup ya haya instalado SGE en C:\\SGE.
    El administrador de licencias no copia ni instala SGE.
    """

    if not CARPETA_INSTALACION.exists():
        raise FileNotFoundError(
            "No se encontró la carpeta de instalación de SGE:\n\n"
            f"{CARPETA_INSTALACION}\n\n"
            "El SGE debe ser instalado previamente por el instalador "
            "principal."
        )

    if not ARCHIVO_SGE.exists():
        raise FileNotFoundError(
            "No se encontró SGE.exe en:\n\n"
            f"{ARCHIVO_SGE}\n\n"
            "El SGE debe ser instalado previamente por el instalador "
            "principal."
        )

    return True


# =====================================================
# CONSTRUIR SOLICITUD DE LICENCIA
# =====================================================

def construir_solicitud():

    solicitud = {

        "producto": "SGE",

        "id_solicitud": str(
            uuid.uuid4()
        ),

        "institucion": (
            entrada_institucion
            .get()
            .strip()
        ),

        "localidad": (
            entrada_localidad
            .get()
            .strip()
        ),

        "provincia": (
            entrada_provincia
            .get()
            .strip()
        ),

        "fecha_solicitud": (
            datetime.now()
            .strftime("%Y-%m-%d %H:%M:%S")
        ),

        "huella_equipo": (
            huella_equipo
            .strip()
            .upper()
        )
    }

    return solicitud


# =====================================================
# GENERAR LICENCIA SGE
# =====================================================

def generar_licencia():

    solicitud = construir_solicitud()

    tipo = tipo_licencia.get()

    dias_prueba = None

    if tipo == "prueba":

        dias_prueba = 30


    datos_licencia, archivo_generado = (
        generar_licencia_desde_datos(

            solicitud=solicitud,

            tipo=tipo,

            version="1.0",

            dias_prueba=dias_prueba,

            ruta_salida=ARCHIVO_LICENCIA
        )
    )


    return datos_licencia, archivo_generado


# =====================================================
# VERIFICAR LICENCIA GENERADA
# =====================================================

def verificar_licencia_instalada():

    if not ARCHIVO_LICENCIA.exists():

        return (
            False,
            "No se encontró el archivo de licencia generado."
        )


    resultado, motivo = analizar_licencia(
        ARCHIVO_LICENCIA
    )


    if resultado:

        return (
            True,
            motivo
        )


    return (
        False,
        motivo
    )


# =====================================================
# INICIAR SGE
# =====================================================

def iniciar_sge():

    if not ARCHIVO_SGE.exists():

        messagebox.showerror(
            "ERROR",
            "No se encontró SGE.exe en:\n\n"
            f"{ARCHIVO_SGE}"
        )

        return


    try:

        subprocess.Popen(
            [str(ARCHIVO_SGE)],
            cwd=str(CARPETA_INSTALACION)
        )


        ventana.destroy()


    except Exception as e:

        traceback.print_exc()

        messagebox.showerror(
            "ERROR AL INICIAR SGE",
            str(e)
        )


# =====================================================
# INSTALAR Y ACTIVAR SGE
# =====================================================

def instalar_y_activar():

    print()
    print("=" * 60)
    print("BOTÓN INSTALAR Y ACTIVAR SGE PRESIONADO")
    print("=" * 60)


    try:

        # -------------------------------------------------
        # Obtener datos
        # -------------------------------------------------

        institucion = (
            entrada_institucion
            .get()
            .strip()
        )

        localidad = (
            entrada_localidad
            .get()
            .strip()
        )

        provincia = (
            entrada_provincia
            .get()
            .strip()
        )


        print("Institución:", institucion)
        print("Localidad:", localidad)
        print("Provincia:", provincia)
        print("Tipo:", tipo_licencia.get())
        print("Huella:", huella_equipo)


        # =================================================
        # VALIDAR DATOS
        # =================================================

        if not institucion:

            messagebox.showwarning(
                "DATOS INCOMPLETOS",
                "Ingrese el nombre de la institución.",
                parent=ventana
            )

            entrada_institucion.focus()

            return


        if not localidad:

            messagebox.showwarning(
                "DATOS INCOMPLETOS",
                "Ingrese la localidad.",
                parent=ventana
            )

            entrada_localidad.focus()

            return


        if not provincia:

            messagebox.showwarning(
                "DATOS INCOMPLETOS",
                "Ingrese la provincia.",
                parent=ventana
            )

            entrada_provincia.focus()

            return


        if not huella_equipo:

            messagebox.showerror(
                "ERROR",
                "No fue posible obtener la huella "
                "del equipo.",
                parent=ventana
            )

            return


        # =================================================
        # CONFIRMACIÓN
        # =================================================

        print("Mostrando cuadro de confirmación...")


        confirmacion = messagebox.askyesno(

            "CONFIRMAR INSTALACIÓN",

            "Se activará SGE en este equipo.\n\n"

            f"Institución:\n{institucion}\n\n"

            f"Localidad:\n{localidad}\n\n"

            f"Provincia:\n{provincia}\n\n"

            f"Tipo de licencia:\n"
            f"{tipo_licencia.get().capitalize()}\n\n"

            f"Equipo autorizado:\n"
            f"{huella_equipo}\n\n"

            "La licencia quedará vinculada "
            "a este equipo.\n\n"

            "¿Desea continuar?",

            parent=ventana
        )


        print(
            "Respuesta de confirmación:",
            confirmacion
        )


        if not confirmacion:

            print("Instalación cancelada.")

            return


        # =================================================
        # VERIFICAR SGE INSTALADO
        # =================================================

        print("Verificando instalación de SGE...")

        try:

            verificar_sge_instalado()

            print("SGE encontrado correctamente:")
            print(ARCHIVO_SGE)

        except Exception as e:

            print("ERROR: SGE NO ENCONTRADO:")
            traceback.print_exc()

            messagebox.showerror(

                "SGE NO ENCONTRADO",

                "No se encontró SGE.exe en la ubicación "
                "de instalación esperada.\n\n"

                f"{ARCHIVO_SGE}\n\n"

                "El SGE debe ser instalado previamente "
                "por el instalador principal.",

                parent=ventana
            )

            return


        # =================================================
        # GENERAR LICENCIA
        # =================================================

        print("Generando licencia...")


        try:

            datos_licencia, archivo_generado = (
                generar_licencia()
            )

            print(
                "Licencia generada:",
                archivo_generado
            )


        except Exception as e:

            print("ERROR AL GENERAR LICENCIA:")
            traceback.print_exc()

            messagebox.showerror(

                "ERROR DE ACTIVACIÓN",

                "No fue posible generar la licencia.\n\n"
                f"{e}",

                parent=ventana
            )

            return


        # =================================================
        # VERIFICAR LICENCIA
        # =================================================

        print("Verificando licencia...")


        try:

            licencia_valida, motivo = (
                verificar_licencia_instalada()
            )

            print(
                "Licencia válida:",
                licencia_valida
            )

            print(
                "Motivo:",
                motivo
            )


        except Exception as e:

            print("ERROR DE VERIFICACIÓN:")
            traceback.print_exc()

            messagebox.showerror(

                "ERROR DE VERIFICACIÓN",

                "La licencia fue generada pero "
                "no pudo ser verificada.\n\n"
                f"{e}",

                parent=ventana
            )

            return


        # =================================================
        # LICENCIA INVÁLIDA
        # =================================================

        if not licencia_valida:

            messagebox.showerror(

                "LICENCIA NO VÁLIDA",

                "La licencia fue generada pero "
                "la verificación no fue exitosa.\n\n"
                f"Motivo: {motivo}",

                parent=ventana
            )

            return


        # =================================================
        # ACTIVACIÓN COMPLETADA
        # =================================================

        print("LICENCIA VÁLIDA.")
        print("Mostrando pantalla de finalización...")


        mostrar_finalizacion(
            datos_licencia
        )


    except Exception as e:

        print()
        print("=" * 60)
        print("ERROR NO CONTROLADO EN INSTALAR_Y_ACTIVAR")
        print("=" * 60)

        traceback.print_exc()


        messagebox.showerror(

            "ERROR INESPERADO",

            "Se produjo un error inesperado en el instalador.\n\n"

            f"{type(e).__name__}: {e}",

            parent=ventana
        )


# =====================================================
# VENTANA / PANTALLA DE FINALIZACIÓN
# =====================================================

def mostrar_finalizacion(datos_licencia):

    print()
    print("=" * 60)
    print("ENTRANDO EN MOSTRAR_FINALIZACION")
    print("=" * 60)


    try:

        # =================================================
        # ELIMINAR CONTENIDO DE LA VENTANA PRINCIPAL
        # =================================================

        for widget in ventana.winfo_children():

            widget.destroy()


        # =================================================
        # CONFIGURAR VENTANA FINAL
        # =================================================

        ventana.title(
            "SGE - Instalación completada"
        )

        ventana.geometry(
            "650x600"
        )

        ventana.resizable(
            False,
            False
        )


        # =================================================
        # CENTRAR VENTANA
        # =================================================

        ventana.update_idletasks()

        ancho = 650
        alto = 600

        ancho_pantalla = (
            ventana.winfo_screenwidth()
        )

        alto_pantalla = (
            ventana.winfo_screenheight()
        )

        posicion_x = (
            ancho_pantalla - ancho
        ) // 2

        posicion_y = (
            alto_pantalla - alto
        ) // 2

        ventana.geometry(
            f"{ancho}x{alto}+"
            f"{posicion_x}+{posicion_y}"
        )


        # =================================================
        # FORZAR VENTANA AL FRENTE
        # =================================================

        ventana.deiconify()

        ventana.lift()

        ventana.attributes(
            "-topmost",
            True
        )

        ventana.after(
            800,
            lambda: ventana.attributes(
                "-topmost",
                False
            )
        )

        ventana.focus_force()


        # =================================================
        # ENCABEZADO
        # =================================================

        titulo = tk.Label(
            ventana,
            text="SGE",
            font=(
                "Segoe UI",
                30,
                "bold"
            )
        )

        titulo.pack(
            pady=(30, 5)
        )


        subtitulo = tk.Label(
            ventana,
            text="Sistema de Gestión Escolar",
            font=(
                "Segoe UI",
                15
            )
        )

        subtitulo.pack(
            pady=(0, 20)
        )


        # =================================================
        # MENSAJE PRINCIPAL
        # =================================================

        mensaje = tk.Label(
            ventana,
            text=(
                "SGE fue instalado y activado "
                "correctamente."
            ),
            font=(
                "Segoe UI",
                15,
                "bold"
            )
        )

        mensaje.pack(
            pady=10
        )


        # =================================================
        # INFORMACIÓN DE LA LICENCIA
        # =================================================

        informacion = (

            f"Institución: "
            f"{datos_licencia['institucion']}\n\n"

            f"Localidad: "
            f"{datos_licencia['localidad']}\n\n"

            f"Provincia: "
            f"{datos_licencia['provincia']}\n\n"

            f"Tipo de licencia: "
            f"{datos_licencia['tipo'].capitalize()}\n\n"

            f"Versión: "
            f"{datos_licencia['version']}\n\n"

            "Equipo autorizado: Sí"
        )


        etiqueta_informacion = tk.Label(
            ventana,
            text=informacion,
            font=(
                "Segoe UI",
                11
            ),
            justify="left"
        )

        etiqueta_informacion.pack(
            pady=15
        )


        # =================================================
        # MARCO DE BOTONES
        # =================================================

        marco_botones = tk.Frame(
            ventana
        )

        marco_botones.pack(
            pady=20
        )


        # =================================================
        # BOTÓN INICIAR SGE
        # =================================================

        boton_iniciar = tk.Button(
            marco_botones,
            text="INICIAR SGE",
            font=(
                "Segoe UI",
                12,
                "bold"
            ),
            width=20,
            height=2,
            command=iniciar_sge
        )

        boton_iniciar.pack(
            side="left",
            padx=10
        )


        # =================================================
        # BOTÓN CERRAR
        # =================================================

        boton_cerrar = tk.Button(
            marco_botones,
            text="CERRAR",
            font=(
                "Segoe UI",
                10,
                "bold"
            ),
            width=20,
            height=2,
            command=ventana.destroy
        )

        boton_cerrar.pack(
            side="left",
            padx=10
        )


        # =================================================
        # INFORMACIÓN FINAL
        # =================================================

        tk.Label(
            ventana,
            text=(
                "La licencia quedó vinculada "
                "a este equipo."
            ),
            font=(
                "Segoe UI",
                9
            )
        ).pack(
            side="bottom",
            pady=15
        )


        # =================================================
        # ACTUALIZAR PANTALLA
        # =================================================

        ventana.update_idletasks()

        ventana.lift()

        ventana.focus_force()


        print("PANTALLA DE FINALIZACIÓN MOSTRADA")
        print("=" * 60)


    except Exception as e:

        print()
        print("=" * 60)
        print("ERROR DENTRO DE MOSTRAR_FINALIZACION")
        print("=" * 60)

        traceback.print_exc()


        # En este caso NO ocultamos la ventana.
        # Mostramos el error directamente.

        messagebox.showerror(

            "ERROR EN PANTALLA FINAL",

            "La instalación terminó correctamente, "
            "pero ocurrió un error al mostrar "
            "la pantalla final.\n\n"

            f"{type(e).__name__}: {e}",

            parent=ventana
        )


# =====================================================
# INTERFAZ GRÁFICA
# =====================================================

ventana = tk.Tk()

ventana.title(
    "ACTIVACIÓN SGE"
)

ventana.geometry(
    "700x700"
)

ventana.resizable(
    False,
    False
)


# =====================================================
# TÍTULO
# =====================================================

titulo = tk.Label(
    ventana,
    text="ACTIVACIÓN SGE",
    font=(
        "Segoe UI",
        18,
        "bold"
    )
)

titulo.pack(
    pady=(10, 5)
)


subtitulo = tk.Label(
    ventana,
    text="Sistema de Gestión Escolar",
    font=(
        "Segoe UI",
        14
    )
)

subtitulo.pack(
    pady=(0, 10)
)


# =====================================================
# DATOS DE LA INSTITUCIÓN
# =====================================================

marco_datos = tk.LabelFrame(
    ventana,
    text="Datos de la institución",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    padx=20,
    pady=8
)

marco_datos.pack(
    padx=40,
    fill="x"
)


# -----------------------------------------------------
# Institución
# -----------------------------------------------------

tk.Label(
    marco_datos,
    text="Institución:",
    font=(
        "Segoe UI",
        10
    )
).grid(
    row=0,
    column=0,
    sticky="w",
    pady=8
)


entrada_institucion = tk.Entry(
    marco_datos,
    font=(
        "Segoe UI",
        10
    ),
    width=45
)

entrada_institucion.grid(
    row=0,
    column=1,
    padx=10,
    pady=8
)


# -----------------------------------------------------
# Localidad
# -----------------------------------------------------

tk.Label(
    marco_datos,
    text="Localidad:",
    font=(
        "Segoe UI",
        10
    )
).grid(
    row=1,
    column=0,
    sticky="w",
    pady=8
)


entrada_localidad = tk.Entry(
    marco_datos,
    font=(
        "Segoe UI",
        10
    ),
    width=45
)

entrada_localidad.grid(
    row=1,
    column=1,
    padx=10,
    pady=8
)


# -----------------------------------------------------
# Provincia
# -----------------------------------------------------

tk.Label(
    marco_datos,
    text="Provincia:",
    font=(
        "Segoe UI",
        10
    )
).grid(
    row=2,
    column=0,
    sticky="w",
    pady=8
)


entrada_provincia = tk.Entry(
    marco_datos,
    font=(
        "Segoe UI",
        10
    ),
    width=45
)

entrada_provincia.grid(
    row=2,
    column=1,
    padx=10,
    pady=8
)


# =====================================================
# TIPO DE LICENCIA
# =====================================================

marco_licencia = tk.LabelFrame(
    ventana,
    text="Tipo de licencia",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    padx=20,
    pady=10
)

marco_licencia.pack(
    padx=40,
    pady=20,
    fill="x"
)


tipo_licencia = tk.StringVar(
    value="permanente"
)


# -----------------------------------------------------
# Licencia de prueba
# -----------------------------------------------------

tk.Radiobutton(
    marco_licencia,
    text="Prueba (30 días)",
    variable=tipo_licencia,
    value="prueba",
    font=(
        "Segoe UI",
        10
    )
).pack(
    anchor="w"
)


# -----------------------------------------------------
# Licencia anual
# -----------------------------------------------------

tk.Radiobutton(
    marco_licencia,
    text="Anual",
    variable=tipo_licencia,
    value="anual",
    font=(
        "Segoe UI",
        10
    )
).pack(
    anchor="w"
)


# -----------------------------------------------------
# Licencia permanente
# -----------------------------------------------------

tk.Radiobutton(
    marco_licencia,
    text="Permanente",
    variable=tipo_licencia,
    value="permanente",
    font=(
        "Segoe UI",
        10
    )
).pack(
    anchor="w"
)


# =====================================================
# HUELLA DEL EQUIPO
# =====================================================

marco_huella = tk.LabelFrame(
    ventana,
    text="Equipo autorizado",
    font=(
        "Segoe UI",
        11,
        "bold"
    ),
    padx=20,
    pady=5
)

marco_huella.pack(
    padx=40,
    pady=5,
    fill="x"
)


tk.Label(
    marco_huella,
    text="Huella del equipo:",
    font=(
        "Segoe UI",
        10
    )
).pack(
    anchor="w"
)


entrada_huella = tk.Entry(
    marco_huella,
    font=(
        "Consolas",
        9
    ),
    width=75,
    state="readonly"
)

entrada_huella.pack(
    pady=8
)


entrada_huella.config(
    state="normal"
)

entrada_huella.insert(
    0,
    huella_equipo
)

entrada_huella.config(
    state="readonly"
)


# =====================================================
# INFORMACIÓN DE SEGURIDAD
# =====================================================

tk.Label(
    ventana,
    text=(
        "La licencia quedará vinculada automáticamente "
        "a este equipo.\n"
        "El SGE no podrá utilizar esta licencia en "
        "otro equipo."
    ),
    font=(
        "Segoe UI",
        10
    ),
    justify="center"
).pack(
    pady=10
)


# =====================================================
# BOTÓN INSTALAR
# =====================================================

boton_instalar = tk.Button(
    ventana,
    text="ACTIVAR SGE",
    font=(
        "Segoe UI",
        10,
        "bold"
    ),
    width=28,
    height=2,
    command=instalar_y_activar
)

boton_instalar.pack(
    pady=5
)


# =====================================================
# PIE DE VENTANA
# =====================================================

tk.Label(
    ventana,
    text="SGE - Sistema de Gestión Escolar",
    font=(
        "Segoe UI",
        9
    )
).pack(
    side="bottom",
    pady=10
)


# =====================================================
# INICIAR INSTALADOR
# =====================================================

print()
print("=" * 60)
print("INSTALADOR SGE INICIADO")
print("Esperando acción del usuario...")
print("=" * 60)
print()


ventana.mainloop()