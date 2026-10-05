
# =====================================================
#          ADMINISTRADOR DE LICENCIAS SGE
# =====================================================

import tkinter as tk
from tkinter import messagebox

import json
import sys
import shutil

from pathlib import Path


# =====================================================
#             RUTA DEL PROYECTO
# =====================================================

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent

if str(CARPETA_PROYECTO) not in sys.path:
    sys.path.insert(0, str(CARPETA_PROYECTO))


# =====================================================
#          IMPORTAR VERIFICADOR DE LICENCIAS
# =====================================================

from Licenciamiento.licencia import (
    analizar_licencia,
    obtener_datos_licencia
)


# =====================================================
#          IMPORTAR GENERADOR DE LICENCIAS
# =====================================================

from generar_licencia import (
    generar_licencia_desde_datos
)


# =====================================================
#                 CONFIGURACIÓN
# =====================================================

NOMBRE_APLICACION = "Administrador de Licencias SGE"
VERSION = "1.0"


# =====================================================
#                    RUTAS
# =====================================================

CARPETA_BASE = Path(__file__).resolve().parent

ARCHIVO_SOLICITUD = (
    CARPETA_BASE / "Solicitud_SGE.dat"
)

ARCHIVO_LICENCIA = (
    CARPETA_BASE / "Licencia_SGE.lic"
)

CARPETA_LICENCIAS_EMITIDAS = (
    CARPETA_BASE / "LicenciasEmitidas"
)


# =====================================================
#       PREPARAR CARPETA DE LICENCIAS EMITIDAS
# =====================================================

def preparar_carpeta_licencias_emitidas():

    CARPETA_LICENCIAS_EMITIDAS.mkdir(
        parents=True,
        exist_ok=True
    )


# =====================================================
#             ARCHIVAR LICENCIA EMITIDA
# =====================================================

def archivar_licencia(ruta_licencia=None):

    if ruta_licencia is None:
        ruta_licencia = ARCHIVO_LICENCIA

    ruta_licencia = Path(ruta_licencia)

    if not ruta_licencia.exists():

        return (
            False,
            "No existe el archivo de licencia."
        )

    try:

        preparar_carpeta_licencias_emitidas()

        datos = obtener_datos_licencia(
            str(ruta_licencia)
        )

        if not datos:

            return (
                False,
                "No se pudieron obtener los datos "
                "de la licencia."
            )

        id_licencia = datos.get(
            "id_licencia"
        )

        if not id_licencia:

            return (
                False,
                "La licencia no contiene "
                "un ID de licencia."
            )

        archivo_destino = (
            CARPETA_LICENCIAS_EMITIDAS
            / f"{id_licencia}.lic"
        )

        if archivo_destino.exists():

            return (
                False,
                "Ya existe una licencia archivada "
                f"con el ID {id_licencia}."
            )

        shutil.copy2(
            ruta_licencia,
            archivo_destino
        )

        return (
            True,
            archivo_destino
        )

    except Exception as e:

        return (
            False,
            str(e)
        )


# =====================================================
#              NUEVA SOLICITUD
# =====================================================

def nueva_solicitud():

    ventana = tk.Toplevel(root)

    ventana.title(
        "Nueva solicitud de licencia"
    )

    ventana.geometry(
        "500x400"
    )

    ventana.resizable(
        False,
        False
    )

    tk.Label(
        ventana,
        text="NUEVA SOLICITUD DE LICENCIA SGE",
        font=("Arial", 14, "bold")
    ).pack(
        pady=20
    )

    marco = tk.Frame(
        ventana
    )

    marco.pack(
        padx=30,
        pady=10,
        fill="x"
    )

    tk.Label(
        marco,
        text="Institución:"
    ).grid(
        row=0,
        column=0,
        sticky="w",
        pady=8
    )

    entry_institucion = tk.Entry(
        marco,
        width=45
    )

    entry_institucion.grid(
        row=0,
        column=1,
        pady=8
    )

    tk.Label(
        marco,
        text="Localidad:"
    ).grid(
        row=1,
        column=0,
        sticky="w",
        pady=8
    )

    entry_localidad = tk.Entry(
        marco,
        width=45
    )

    entry_localidad.grid(
        row=1,
        column=1,
        pady=8
    )

    tk.Label(
        marco,
        text="Provincia:"
    ).grid(
        row=2,
        column=0,
        sticky="w",
        pady=8
    )

    entry_provincia = tk.Entry(
        marco,
        width=45
    )

    entry_provincia.grid(
        row=2,
        column=1,
        pady=8
    )

    def guardar():

        institucion = (
            entry_institucion
            .get()
            .strip()
        )

        localidad = (
            entry_localidad
            .get()
            .strip()
        )

        provincia = (
            entry_provincia
            .get()
            .strip()
        )

        if not institucion:

            messagebox.showwarning(
                "Dato faltante",
                "Ingrese la institución.",
                parent=ventana
            )

            return

        if not localidad:

            messagebox.showwarning(
                "Dato faltante",
                "Ingrese la localidad.",
                parent=ventana
            )

            return

        if not provincia:

            messagebox.showwarning(
                "Dato faltante",
                "Ingrese la provincia.",
                parent=ventana
            )

            return

        import uuid
        from datetime import datetime

        solicitud = {

            "producto": "SGE",

            "id_solicitud":
                str(uuid.uuid4()),

            "institucion":
                institucion,

            "localidad":
                localidad,

            "provincia":
                provincia,

            "fecha_solicitud":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        }

        try:

            with open(
                ARCHIVO_SOLICITUD,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    solicitud,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

            messagebox.showinfo(
                "Solicitud creada",
                "La solicitud de licencia fue "
                "creada correctamente.",
                parent=ventana
            )

            ventana.destroy()

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo guardar la solicitud:\n\n{e}",
                parent=ventana
            )

    tk.Button(
        ventana,
        text="Guardar solicitud",
        width=25,
        command=guardar
    ).pack(
        pady=25
    )


# =====================================================
#                ABRIR SOLICITUD
# =====================================================

def abrir_solicitud():

    if not ARCHIVO_SOLICITUD.exists():

        messagebox.showwarning(
            "Solicitud",
            "No existe ninguna solicitud."
        )

        return

    try:

        with open(
            ARCHIVO_SOLICITUD,
            "r",
            encoding="utf-8"
        ) as archivo:

            solicitud = json.load(
                archivo
            )

        campos_requeridos = (
            "producto",
            "id_solicitud",
            "institucion",
            "localidad",
            "provincia",
            "fecha_solicitud"
        )

        for campo in campos_requeridos:

            if campo not in solicitud:

                raise ValueError(
                    f"Falta el campo '{campo}'."
                )

        if solicitud.get("producto") != "SGE":

            raise ValueError(
                "La solicitud no corresponde al SGE."
            )

        texto = (
            "SOLICITUD DE LICENCIA SGE\n"
            "\n"
            f"Institución:\n"
            f"{solicitud.get('institucion')}\n\n"
            f"Localidad:\n"
            f"{solicitud.get('localidad')}\n\n"
            f"Provincia:\n"
            f"{solicitud.get('provincia')}\n\n"
            f"ID solicitud:\n"
            f"{solicitud.get('id_solicitud')}\n\n"
            f"Fecha:\n"
            f"{solicitud.get('fecha_solicitud')}"
        )

        messagebox.showinfo(
            "Solicitud de licencia",
            texto
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No se pudo abrir la solicitud:\n\n{e}"
        )


# =====================================================
#              EMITIR LICENCIA
# =====================================================

def emitir_licencia():

    # -------------------------------------------------
    # Verificar solicitud
    # -------------------------------------------------

    if not ARCHIVO_SOLICITUD.exists():

        messagebox.showwarning(
            "Emitir licencia",
            "No existe una solicitud de licencia.\n\n"
            "Primero debe crear una solicitud."
        )

        return

    # -------------------------------------------------
    # Cargar solicitud
    # -------------------------------------------------

    try:

        with open(
            ARCHIVO_SOLICITUD,
            "r",
            encoding="utf-8"
        ) as archivo:

            solicitud = json.load(
                archivo
            )

    except Exception as e:

        messagebox.showerror(
            "Error",
            "No se pudo leer la solicitud:\n\n"
            f"{e}"
        )

        return

    # -------------------------------------------------
    # Validar solicitud
    # -------------------------------------------------

    campos_requeridos = (
        "producto",
        "id_solicitud",
        "institucion",
        "localidad",
        "provincia",
        "fecha_solicitud"
    )

    for campo in campos_requeridos:

        if campo not in solicitud:

            messagebox.showerror(
                "Solicitud inválida",
                f"Falta el campo '{campo}' "
                "en la solicitud."
            )

            return

    if solicitud.get("producto") != "SGE":

        messagebox.showerror(
            "Solicitud inválida",
            "La solicitud no corresponde al SGE."
        )

        return

    # -------------------------------------------------
    # Ventana de emisión
    # -------------------------------------------------

    ventana = tk.Toplevel(root)

    ventana.title(
        "Emitir licencia SGE"
    )

    ventana.geometry(
        "560x570"
    )

    ventana.resizable(
        False,
        False
    )

    # -------------------------------------------------
    # Título
    # -------------------------------------------------

    tk.Label(
        ventana,
        text="EMISIÓN DE LICENCIA SGE",
        font=("Arial", 15, "bold")
    ).pack(
        pady=15
    )

    # -------------------------------------------------
    # Datos de solicitud
    # -------------------------------------------------

    marco_datos = tk.LabelFrame(
        ventana,
        text="Datos de la solicitud",
        padx=15,
        pady=10
    )

    marco_datos.pack(
        padx=25,
        pady=5,
        fill="x"
    )

    tk.Label(
        marco_datos,
        text=f"Institución: {solicitud.get('institucion')}",
        anchor="w"
    ).pack(
        anchor="w"
    )

    tk.Label(
        marco_datos,
        text=f"Localidad: {solicitud.get('localidad')}",
        anchor="w"
    ).pack(
        anchor="w"
    )

    tk.Label(
        marco_datos,
        text=f"Provincia: {solicitud.get('provincia')}",
        anchor="w"
    ).pack(
        anchor="w"
    )

    tk.Label(
        marco_datos,
        text=f"ID solicitud: {solicitud.get('id_solicitud')}",
        anchor="w"
    ).pack(
        anchor="w"
    )

    # -------------------------------------------------
    # Tipo de licencia
    # -------------------------------------------------

    marco_tipo = tk.LabelFrame(
        ventana,
        text="Tipo de licencia",
        padx=15,
        pady=10
    )

    marco_tipo.pack(
        padx=25,
        pady=15,
        fill="x"
    )

    tipo_var = tk.StringVar(
        value="permanente"
    )

    tk.Radiobutton(
        marco_tipo,
        text="Permanente",
        variable=tipo_var,
        value="permanente"
    ).pack(
        anchor="w"
    )

    tk.Radiobutton(
        marco_tipo,
        text="Anual",
        variable=tipo_var,
        value="anual"
    ).pack(
        anchor="w"
    )

    tk.Radiobutton(
        marco_tipo,
        text="Prueba",
        variable=tipo_var,
        value="prueba"
    ).pack(
        anchor="w"
    )

    # -------------------------------------------------
    # Días de prueba
    # -------------------------------------------------

    marco_prueba = tk.Frame(
        ventana
    )

    marco_prueba.pack(
        pady=5
    )

    tk.Label(
        marco_prueba,
        text="Días de prueba:"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    entry_dias = tk.Entry(
        marco_prueba,
        width=10
    )

    entry_dias.grid(
        row=0,
        column=1,
        padx=5
    )

    entry_dias.insert(
        0,
        "30"
    )

    # -------------------------------------------------
    # Versión
    # -------------------------------------------------

    marco_version = tk.Frame(
        ventana
    )

    marco_version.pack(
        pady=10
    )

    tk.Label(
        marco_version,
        text="Versión SGE:"
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    entry_version = tk.Entry(
        marco_version,
        width=10
    )

    entry_version.grid(
        row=0,
        column=1,
        padx=5
    )

    entry_version.insert(
        0,
        VERSION
    )

    # -------------------------------------------------
    # Función generar
    # -------------------------------------------------

    def generar():

        tipo = tipo_var.get()

        version = (
            entry_version
            .get()
            .strip()
        )

        if not version:

            version = VERSION

        dias_prueba = None

        # ---------------------------------------------
        # Validar días si es prueba
        # ---------------------------------------------

        if tipo == "prueba":

            texto_dias = (
                entry_dias
                .get()
                .strip()
            )

            try:

                dias_prueba = int(
                    texto_dias
                )

            except ValueError:

                messagebox.showwarning(
                    "Cantidad inválida",
                    "Ingrese una cantidad válida "
                    "de días de prueba.",
                    parent=ventana
                )

                return

            if dias_prueba <= 0:

                messagebox.showwarning(
                    "Cantidad inválida",
                    "La cantidad de días debe ser "
                    "mayor que cero.",
                    parent=ventana
                )

                return

        # ---------------------------------------------
        # Confirmación
        # ---------------------------------------------

        tipo_mostrar = {

            "permanente":
                "PERMANENTE",

            "anual":
                "ANUAL",

            "prueba":
                f"PRUEBA ({dias_prueba} días)"
        }

        mensaje_confirmacion = (
            "Se generará una nueva licencia SGE.\n\n"
            f"Institución:\n"
            f"{solicitud.get('institucion')}\n\n"
            f"Tipo:\n"
            f"{tipo_mostrar.get(tipo)}\n\n"
            f"Versión:\n"
            f"{version}\n\n"
            "¿Desea continuar?"
        )

        confirmar = messagebox.askyesno(
            "Confirmar emisión",
            mensaje_confirmacion,
            parent=ventana
        )

        if not confirmar:

            return

        # ---------------------------------------------
        # Generar licencia
        # ---------------------------------------------

        try:

            datos_licencia, archivo_salida = (
                generar_licencia_desde_datos(
                    solicitud=solicitud,
                    tipo=tipo,
                    version=version,
                    dias_prueba=dias_prueba,
                    ruta_salida=ARCHIVO_LICENCIA
                )
            )

        except Exception as e:

            messagebox.showerror(
                "Error al emitir licencia",
                "No se pudo generar la licencia.\n\n"
                f"{e}",
                parent=ventana
            )

            return

        # ---------------------------------------------
        # Archivar licencia
        # ---------------------------------------------

        exito_archivo, resultado_archivo = (
            archivar_licencia(
                ARCHIVO_LICENCIA
            )
        )

        if not exito_archivo:

            messagebox.showerror(
                "Error al archivar",
                "La licencia fue generada, pero "
                "no se pudo guardar en el archivo "
                "histórico.\n\n"
                f"{resultado_archivo}",
                parent=ventana
            )

            return

        # ---------------------------------------------
        # Datos para mostrar
        # ---------------------------------------------

        fecha_vencimiento = (
            datos_licencia.get(
                "fecha_vencimiento"
            )
        )

        if not fecha_vencimiento:

            fecha_vencimiento = (
                "Sin vencimiento"
            )

        id_licencia = (
            datos_licencia.get(
                "id_licencia",
                ""
            )
        )

        # ---------------------------------------------
        # Resultado
        # ---------------------------------------------

        mensaje = (
            "LICENCIA EMITIDA CORRECTAMENTE\n"
            "\n"
            f"ID de licencia:\n"
            f"{id_licencia}\n\n"
            f"Institución:\n"
            f"{datos_licencia.get('institucion')}\n\n"
            f"Tipo:\n"
            f"{datos_licencia.get('tipo')}\n\n"
            f"Versión:\n"
            f"{datos_licencia.get('version')}\n\n"
            f"Fecha de emisión:\n"
            f"{datos_licencia.get('fecha_emision')}\n\n"
            f"Vencimiento:\n"
            f"{fecha_vencimiento}\n\n"
            "Licencia actual:\n"
            f"{ARCHIVO_LICENCIA}\n\n"
            "Archivo histórico:\n"
            f"{resultado_archivo}"
        )

        messagebox.showinfo(
            "Licencia emitida",
            mensaje,
            parent=ventana
        )

        ventana.destroy()

    # -------------------------------------------------
    # Botón emitir
    # -------------------------------------------------

    tk.Button(
        ventana,
        text="GENERAR LICENCIA",
        width=25,
        height=2,
        command=generar
    ).pack(
        pady=20
    )

    # -------------------------------------------------
    # Botón cancelar
    # -------------------------------------------------

    tk.Button(
        ventana,
        text="Cancelar",
        width=15,
        command=ventana.destroy
    ).pack()


# =====================================================
#             VERIFICAR LICENCIA
# =====================================================

def verificar_licencia():

    if not ARCHIVO_LICENCIA.exists():

        messagebox.showwarning(
            "Verificar licencia",
            "No existe una licencia SGE."
        )

        return

    try:

        valida, motivo = analizar_licencia(
            str(ARCHIVO_LICENCIA)
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No se pudo analizar la licencia:\n\n{e}"
        )

        return

    if not valida:

        mensajes = {

            "LICENCIA_NO_ENCONTRADA":
                "No se encontró la licencia.",

            "ARCHIVO_INVALIDO":
                "El archivo de licencia no es válido.",

            "ESTRUCTURA_INVALIDA":
                "La estructura de la licencia es inválida.",

            "PRODUCTO_INVALIDO":
                "La licencia no corresponde al SGE.",

            "ERROR_CLAVE_PUBLICA":
                "No se pudo cargar la clave pública.",

            "FIRMA_INVALIDA":
                "La firma digital de la licencia no es válida.",

            "VERSION_NO_COMPATIBLE":
                "La licencia no es compatible con esta versión del SGE.",

            "FECHA_INVALIDA":
                "La fecha de vencimiento de la licencia no es válida.",

            "LICENCIA_VENCIDA":
                "La licencia está vencida."
        }

        mensaje = mensajes.get(
            motivo,
            f"La licencia no es válida.\n\nMotivo: {motivo}"
        )

        messagebox.showerror(
            "Licencia no válida",
            mensaje
        )

        return

    try:

        datos = obtener_datos_licencia(
            str(ARCHIVO_LICENCIA)
        )

    except Exception as e:

        messagebox.showerror(
            "Error",
            f"No se pudieron obtener los datos:\n\n{e}"
        )

        return

    if not datos:

        messagebox.showerror(
            "Error",
            "No se pudieron obtener los datos "
            "de la licencia."
        )

        return

    fecha_vencimiento = (
        datos.get(
            "fecha_vencimiento"
        )
    )

    if not fecha_vencimiento:

        fecha_vencimiento = (
            "Sin vencimiento"
        )

    ventana = tk.Toplevel(root)

    ventana.title(
        "Licencia SGE"
    )

    ventana.geometry(
        "520x500"
    )

    ventana.resizable(
        False,
        False
    )

    tk.Label(
        ventana,
        text="LICENCIA SGE VÁLIDA",
        font=("Arial", 16, "bold")
    ).pack(
        pady=20
    )

    texto = (
        f"Producto:\n"
        f"{datos.get('producto')}\n\n"

        f"ID licencia:\n"
        f"{datos.get('id_licencia')}\n\n"

        f"ID solicitud:\n"
        f"{datos.get('id_solicitud')}\n\n"

        f"Institución:\n"
        f"{datos.get('institucion')}\n\n"

        f"Localidad:\n"
        f"{datos.get('localidad')}\n\n"

        f"Provincia:\n"
        f"{datos.get('provincia')}\n\n"

        f"Tipo:\n"
        f"{datos.get('tipo')}\n\n"

        f"Versión:\n"
        f"{datos.get('version')}\n\n"

        f"Fecha emisión:\n"
        f"{datos.get('fecha_emision')}\n\n"

        f"Fecha vencimiento:\n"
        f"{fecha_vencimiento}"
    )

    tk.Label(
        ventana,
        text=texto,
        justify="left",
        anchor="w",
        font=("Arial", 10)
    ).pack(
        padx=30,
        anchor="w"
    )

    tk.Button(
        ventana,
        text="Cerrar",
        width=15,
        command=ventana.destroy
    ).pack(
        pady=25
    )


# =====================================================
#           VER LICENCIAS EMITIDAS
# =====================================================

def ver_licencias_emitidas():

    preparar_carpeta_licencias_emitidas()

    archivos = sorted(
        CARPETA_LICENCIAS_EMITIDAS.glob(
            "*.lic"
        )
    )

    if not archivos:

        messagebox.showinfo(
            "Licencias emitidas",
            "No existen licencias archivadas todavía."
        )

        return

    ventana = tk.Toplevel(root)

    ventana.title(
        "Licencias emitidas"
    )

    ventana.geometry(
        "700x450"
    )

    ventana.resizable(
        False,
        False
    )

    tk.Label(
        ventana,
        text="LICENCIAS EMITIDAS",
        font=("Arial", 15, "bold")
    ).pack(
        pady=15
    )

    marco_lista = tk.Frame(
        ventana
    )

    marco_lista.pack(
        padx=20,
        pady=10,
        fill="both",
        expand=True
    )

    scrollbar = tk.Scrollbar(
        marco_lista
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    lista = tk.Listbox(
        marco_lista,
        width=75,
        height=17,
        yscrollcommand=scrollbar.set
    )

    lista.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.config(
        command=lista.yview
    )

    for archivo in archivos:

        lista.insert(
            tk.END,
            archivo.name
        )

    def mostrar_detalle(event=None):

        seleccion = lista.curselection()

        if not seleccion:

            return

        archivo = archivos[
            seleccion[0]
        ]

        try:

            valida, motivo = analizar_licencia(
                str(archivo)
            )

            datos = obtener_datos_licencia(
                str(archivo)
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudo leer la licencia:\n\n{e}",
                parent=ventana
            )

            return

        if not datos:

            messagebox.showerror(
                "Error",
                "No se pudieron obtener los datos "
                "de la licencia.",
                parent=ventana
            )

            return

        fecha_vencimiento = (
            datos.get(
                "fecha_vencimiento"
            )
        )

        if not fecha_vencimiento:

            fecha_vencimiento = (
                "Sin vencimiento"
            )

        estado = (
            "VÁLIDA"
            if valida
            else f"NO VÁLIDA ({motivo})"
        )

        texto = (
            f"Estado:\n"
            f"{estado}\n\n"

            f"ID licencia:\n"
            f"{datos.get('id_licencia')}\n\n"

            f"Institución:\n"
            f"{datos.get('institucion')}\n\n"

            f"Localidad:\n"
            f"{datos.get('localidad')}\n\n"

            f"Provincia:\n"
            f"{datos.get('provincia')}\n\n"

            f"Tipo:\n"
            f"{datos.get('tipo')}\n\n"

            f"Versión:\n"
            f"{datos.get('version')}\n\n"

            f"Fecha emisión:\n"
            f"{datos.get('fecha_emision')}\n\n"

            f"Fecha vencimiento:\n"
            f"{fecha_vencimiento}"
        )

        messagebox.showinfo(
            "Detalle de licencia",
            texto,
            parent=ventana
        )

    lista.bind(
        "<Double-Button-1>",
        mostrar_detalle
    )

    tk.Label(
        ventana,
        text="Haga doble clic sobre una licencia para ver sus datos."
    ).pack(
        pady=5
    )

    tk.Button(
        ventana,
        text="Cerrar",
        width=15,
        command=ventana.destroy
    ).pack(
        pady=15
    )


# =====================================================
#                       SALIR
# =====================================================

def salir():

    root.destroy()


# =====================================================
#                 VENTANA PRINCIPAL
# =====================================================

root = tk.Tk()

root.title(
    NOMBRE_APLICACION
)

root.geometry(
    "520x500"
)

root.resizable(
    False,
    False
)


# =====================================================
#                      TÍTULO
# =====================================================

tk.Label(
    root,
    text="ADMINISTRADOR DE LICENCIAS SGE",
    font=("Arial", 17, "bold")
).pack(
    pady=25
)

tk.Label(
    root,
    text=f"Versión {VERSION}",
    font=("Arial", 10)
).pack(
    pady=2
)


# =====================================================
#                    BOTONES
# =====================================================

tk.Button(
    root,
    text="Nueva solicitud",
    width=30,
    height=2,
    command=nueva_solicitud
).pack(
    pady=7
)

tk.Button(
    root,
    text="Abrir solicitud",
    width=30,
    height=2,
    command=abrir_solicitud
).pack(
    pady=7
)

tk.Button(
    root,
    text="Emitir licencia",
    width=30,
    height=2,
    command=emitir_licencia
).pack(
    pady=7
)

tk.Button(
    root,
    text="Verificar licencia",
    width=30,
    height=2,
    command=verificar_licencia
).pack(
    pady=7
)

tk.Button(
    root,
    text="Licencias emitidas",
    width=30,
    height=2,
    command=ver_licencias_emitidas
).pack(
    pady=7
)

tk.Button(
    root,
    text="Salir",
    width=30,
    height=2,
    command=salir
).pack(
    pady=15
)


# =====================================================
#                    EJECUTAR
# =====================================================

root.mainloop()

