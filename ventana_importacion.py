"""
=========================================================
Sistema de Gestión Educativa (SGE)

Archivo: ventana_importacion.py

Descripción:
Interfaz gráfica para importar docentes desde Excel.

La ventana utiliza Toplevel() y depende de la ventana
principal del SGE.

Autor: Miguel Ángel Manente
=========================================================
"""

# ==========================================================
# IMPORTACIONES
# ==========================================================

import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from importador import (
    procesar_excel_docentes,
    generar_resumen_importacion,
    guardar_importacion_docentes,
)


# ==========================================================
# VENTANA DE IMPORTACIÓN
# ==========================================================

class VentanaImportacion:
    """
    Ventana secundaria para importar docentes.
    """

    def __init__(self, parent):

        self.parent = parent

        # ==================================================
        # CREAR TOPLEVEL
        # ==================================================

        self.ventana = tk.Toplevel(
            parent
        )

        self.ventana.title(
            "Importación de docentes"
        )

        self.ventana.geometry(
            "1300x680"
        )

        self.ventana.minsize(
            1300,
            680
        )

        # --------------------------------------------------
        # Relación con ventana principal
        # --------------------------------------------------

        self.ventana.transient(
            parent
        )

        self.ventana.grab_set()

        # --------------------------------------------------
        # Cerrar con X
        # --------------------------------------------------

        self.ventana.protocol(
            "WM_DELETE_WINDOW",
            self.cerrar
        )

        # ==================================================
        # VARIABLES
        # ==================================================

        self.ruta_archivo = tk.StringVar()

        self.resultados = []

        self.resumen = None

        self.importacion_procesada = False

        self.importacion_guardada = False

        # ==================================================
        # CREAR INTERFAZ
        # ==================================================

        self.crear_interfaz()

    # ======================================================
    # CREAR INTERFAZ
    # ======================================================

    def crear_interfaz(self):

        # ==================================================
        # CONTENEDOR PRINCIPAL
        # ==================================================

        frame_principal = ttk.Frame(
            self.ventana
        )

        frame_principal.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ==================================================
        # CONFIGURACIÓN DE FILAS
        #
        # Solamente la fila de la tabla puede expandirse.
        # ==================================================

        frame_principal.rowconfigure(
            0,
            weight=0
        )

        frame_principal.rowconfigure(
            1,
            weight=0
        )

        frame_principal.rowconfigure(
            2,
            weight=1
        )

        frame_principal.rowconfigure(
            3,
            weight=0
        )

        frame_principal.rowconfigure(
            4,
            weight=0
        )

        frame_principal.columnconfigure(
            0,
            weight=1
        )

        # ==================================================
        # FRAME SUPERIOR
        # ==================================================

        frame_superior = ttk.LabelFrame(
            frame_principal,
            text="Archivo de importación"
        )

        frame_superior.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        frame_superior.columnconfigure(
            1,
            weight=1
        )

        # --------------------------------------------------
        # Etiqueta
        # --------------------------------------------------

        ttk.Label(
            frame_superior,
            text="Archivo:"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=8,
            sticky="w"
        )

        # --------------------------------------------------
        # Ruta
        # --------------------------------------------------

        self.entry_archivo = ttk.Entry(
            frame_superior,
            textvariable=self.ruta_archivo,
            state="readonly"
        )

        self.entry_archivo.grid(
            row=0,
            column=1,
            padx=5,
            pady=8,
            sticky="ew"
        )

        # --------------------------------------------------
        # Seleccionar
        # --------------------------------------------------

        self.boton_seleccionar = ttk.Button(
            frame_superior,
            text="Seleccionar Excel",
            command=self.seleccionar_archivo
        )

        self.boton_seleccionar.grid(
            row=0,
            column=2,
            padx=5,
            pady=8
        )

        # --------------------------------------------------
        # Analizar
        # --------------------------------------------------

        self.boton_analizar = ttk.Button(
            frame_superior,
            text="Analizar archivo",
            command=self.analizar_archivo,
            state="disabled"
        )

        self.boton_analizar.grid(
            row=0,
            column=3,
            padx=5,
            pady=8
        )

        # ==================================================
        # FRAME RESUMEN
        # ==================================================

        frame_resumen = ttk.LabelFrame(
            frame_principal,
            text="Resumen"
        )

        frame_resumen.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        # --------------------------------------------------
        # Resumen
        # --------------------------------------------------

        self.lbl_total = ttk.Label(
            frame_resumen,
            text="Total: 0"
        )

        self.lbl_total.grid(
            row=0,
            column=0,
            padx=15,
            pady=7
        )

        self.lbl_nuevos = ttk.Label(
            frame_resumen,
            text="Nuevos: 0"
        )

        self.lbl_nuevos.grid(
            row=0,
            column=1,
            padx=15,
            pady=7
        )

        self.lbl_actualizar = ttk.Label(
            frame_resumen,
            text="Actualizar: 0"
        )

        self.lbl_actualizar.grid(
            row=0,
            column=2,
            padx=15,
            pady=7
        )

        self.lbl_sin_cambios = ttk.Label(
            frame_resumen,
            text="Sin cambios: 0"
        )

        self.lbl_sin_cambios.grid(
            row=0,
            column=3,
            padx=15,
            pady=7
        )

        self.lbl_errores = ttk.Label(
            frame_resumen,
            text="Errores: 0"
        )

        self.lbl_errores.grid(
            row=0,
            column=4,
            padx=15,
            pady=7
        )

        # ==================================================
        # FRAME TABLA
        #
        # ESTA ES LA ÚNICA ZONA QUE SE EXPANDE.
        # ==================================================

        frame_tabla = ttk.LabelFrame(
            frame_principal,
            text="Vista previa"
        )

        frame_tabla.grid(
            row=2,
            column=0,
            sticky="nsew",
            pady=(0, 8)
        )

        frame_tabla.rowconfigure(
            0,
            weight=1
        )

        frame_tabla.columnconfigure(
            0,
            weight=1
        )

        # --------------------------------------------------
        # Scroll vertical
        # --------------------------------------------------

        scrollbar_vertical = ttk.Scrollbar(
            frame_tabla,
            orient="vertical"
        )

        scrollbar_vertical.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        # --------------------------------------------------
        # Scroll horizontal
        # --------------------------------------------------

        scrollbar_horizontal = ttk.Scrollbar(
            frame_tabla,
            orient="horizontal"
        )

        scrollbar_horizontal.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        # --------------------------------------------------
        # Treeview
        # --------------------------------------------------

        columnas = (
            "fila",
            "docente",
            "dni",
            "estado",
            "detalle"
        )

        self.tree = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            yscrollcommand=scrollbar_vertical.set,
            xscrollcommand=scrollbar_horizontal.set,
            selectmode="browse"
        )

        scrollbar_vertical.config(
            command=self.tree.yview
        )

        scrollbar_horizontal.config(
            command=self.tree.xview
        )

        # --------------------------------------------------
        # Encabezados
        # --------------------------------------------------

        self.tree.heading(
            "fila",
            text="Fila"
        )

        self.tree.heading(
            "docente",
            text="Docente"
        )

        self.tree.heading(
            "dni",
            text="DNI"
        )

        self.tree.heading(
            "estado",
            text="Estado"
        )

        self.tree.heading(
            "detalle",
            text="Detalle"
        )

        # --------------------------------------------------
        # Columnas
        # --------------------------------------------------

        self.tree.column(
            "fila",
            width=60,
            anchor="center"
        )

        self.tree.column(
            "docente",
            width=220
        )

        self.tree.column(
            "dni",
            width=120,
            anchor="center"
        )

        self.tree.column(
            "estado",
            width=130,
            anchor="center"
        )

        self.tree.column(
            "detalle",
            width=500
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        # ==================================================
        # COLORES DE ESTADOS
        # ==================================================

        self.tree.tag_configure(
            "NUEVO",
            foreground="green"
        )

        self.tree.tag_configure(
            "ACTUALIZAR",
            foreground="orange"
        )

        self.tree.tag_configure(
            "SIN_CAMBIOS",
            foreground="gray"
        )

        self.tree.tag_configure(
            "ERROR",
            foreground="red"
        )

        # --------------------------------------------------
        # Selección
        # --------------------------------------------------

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.mostrar_detalle
        )

        # ==================================================
        # FRAME DETALLE
        #
        # Altura CONTROLADA.
        # No puede empujar los botones fuera de la pantalla.
        # ==================================================

        frame_detalle = ttk.LabelFrame(
            frame_principal,
            text="Detalle del registro seleccionado"
        )

        frame_detalle.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        frame_detalle.columnconfigure(
            0,
            weight=1
        )

        frame_detalle.rowconfigure(
            0,
            weight=1
        )

        # --------------------------------------------------
        # Contenedor del texto
        # --------------------------------------------------

        frame_texto_detalle = ttk.Frame(
            frame_detalle
        )

        frame_texto_detalle.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=5,
            pady=5
        )

        frame_texto_detalle.columnconfigure(
            0,
            weight=1
        )

        frame_texto_detalle.rowconfigure(
            0,
            weight=1
        )

        # --------------------------------------------------
        # Scroll del detalle
        # --------------------------------------------------

        scrollbar_detalle = ttk.Scrollbar(
            frame_texto_detalle,
            orient="vertical"
        )

        scrollbar_detalle.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        # --------------------------------------------------
        # Texto
        # --------------------------------------------------

        self.texto_detalle = tk.Text(
            frame_texto_detalle,
            height=5,
            wrap="word",
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar_detalle.set
        )

        self.texto_detalle.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        scrollbar_detalle.config(
            command=self.texto_detalle.yview
        )

        self.texto_detalle.config(
            state="disabled"
        )

        # ==================================================
        # FRAME BOTONES
        #
        # ESTE FRAME NUNCA SE EXPANDE.
        # ==================================================

        frame_botones = ttk.Frame(
            frame_principal
        )

        frame_botones.grid(
            row=4,
            column=0,
            sticky="ew"
        )

        # ==================================================
        # BOTÓN ABRIR ARCHIVO
        # ==================================================

        self.boton_abrir_archivo = ttk.Button(
            frame_botones,
            text="Abrir archivo para corregir",
            command=self.abrir_archivo_para_corregir,
            state="disabled"
        )

        self.boton_abrir_archivo.pack(
            side="left",
            padx=5
        )

        # ==================================================
        # BOTÓN CERRAR
        # ==================================================

        self.boton_cerrar = ttk.Button(
            frame_botones,
            text="Cerrar",
            command=self.cerrar
        )

        self.boton_cerrar.pack(
            side="right",
            padx=5
        )

        # ==================================================
        # BOTÓN CONFIRMAR
        # ==================================================

        self.boton_confirmar = ttk.Button(
            frame_botones,
            text="Confirmar importación",
            command=self.confirmar_importacion,
            state="disabled"
        )

        self.boton_confirmar.pack(
            side="right",
            padx=5
        )

    # ======================================================
    # SELECCIONAR ARCHIVO
    # ======================================================

    def seleccionar_archivo(self):

        ruta = filedialog.askopenfilename(
            parent=self.ventana,
            title="Seleccionar archivo Excel",
            filetypes=[
                (
                    "Archivos Excel",
                    "*.xlsx *.xlsm"
                ),
                (
                    "Todos los archivos",
                    "*.*"
                )
            ]
        )

        if not ruta:
            return

        self.ruta_archivo.set(
            ruta
        )

        self.boton_analizar.config(
            state="normal"
        )

        self.limpiar_resultados()

    # ======================================================
    # ANALIZAR ARCHIVO
    # ======================================================

    def analizar_archivo(self):

        ruta = self.ruta_archivo.get().strip()

        if not ruta:

            messagebox.showwarning(
                "Importación",
                "Seleccione un archivo Excel.",
                parent=self.ventana
            )

            return

        self.limpiar_resultados()

        try:

            resultado_importacion = (
                procesar_excel_docentes(
                    ruta
                )
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                "Ocurrió un error durante "
                "el análisis:\n\n"
                f"{e}",
                parent=self.ventana
            )

            return

        # --------------------------------------------------
        # Errores de lectura
        # --------------------------------------------------

        errores_archivo = (
            resultado_importacion[
                "errores_archivo"
            ]
        )

        if errores_archivo:

            messagebox.showerror(
                "Error en el archivo",
                "\n".join(
                    errores_archivo
                ),
                parent=self.ventana
            )

            return

        # --------------------------------------------------
        # Guardar resultados
        # --------------------------------------------------

        self.resultados = (
            resultado_importacion[
                "resultados"
            ]
        )

        self.resumen = (
            generar_resumen_importacion(
                self.resultados
            )
        )

        self.importacion_procesada = True

        # --------------------------------------------------
        # Mostrar
        # --------------------------------------------------

        self.mostrar_resumen()

        self.mostrar_resultados()

        # --------------------------------------------------
        # Activar confirmar
        # --------------------------------------------------

        operaciones = (
            self.resumen["nuevos"]
            + self.resumen["actualizar"]
        )

        if operaciones > 0:

            self.boton_confirmar.config(
                state="normal"
            )

        else:

            self.boton_confirmar.config(
                state="disabled"
            )

        # --------------------------------------------------
        # Avisar errores
        # --------------------------------------------------

        if self.resumen["errores"] > 0:

            messagebox.showwarning(
                "Análisis terminado",
                "El archivo fue analizado.\n\n"
                f"Total: {self.resumen['total']}\n"
                f"Nuevos: {self.resumen['nuevos']}\n"
                f"Actualizar: {self.resumen['actualizar']}\n"
                f"Sin cambios: {self.resumen['sin_cambios']}\n"
                f"Errores: {self.resumen['errores']}",
                parent=self.ventana
            )

    # ======================================================
    # MOSTRAR RESUMEN
    # ======================================================

    def mostrar_resumen(self):

        self.lbl_total.config(
            text=(
                f"Total: "
                f"{self.resumen['total']}"
            )
        )

        self.lbl_nuevos.config(
            text=(
                f"Nuevos: "
                f"{self.resumen['nuevos']}"
            )
        )

        self.lbl_actualizar.config(
            text=(
                f"Actualizar: "
                f"{self.resumen['actualizar']}"
            )
        )

        self.lbl_sin_cambios.config(
            text=(
                f"Sin cambios: "
                f"{self.resumen['sin_cambios']}"
            )
        )

        self.lbl_errores.config(
            text=(
                f"Errores: "
                f"{self.resumen['errores']}"
            )
        )

    # ======================================================
    # MOSTRAR RESULTADOS
    # ======================================================

    def mostrar_resultados(self):

        for item in self.tree.get_children():

            self.tree.delete(
                item
            )

        for resultado in self.resultados:

            datos = resultado["datos"]

            fila = resultado["fila"]

            estado = resultado["estado"]

            apellido = datos.get(
                "apellido",
                ""
            )

            nombre = datos.get(
                "nombre",
                ""
            )

            dni = datos.get(
                "dni",
                ""
            )

            docente = (
                f"{apellido}, {nombre}"
            ).strip(
                ", "
            )

            detalle = self.obtener_detalle(
                resultado
            )

            self.tree.insert(
                "",
                "end",
                iid=str(fila),
                values=(
                    fila,
                    docente,
                    dni,
                    estado,
                    detalle
                ),
                tags=(estado,)
            )

    # ======================================================
    # OBTENER DETALLE
    # ======================================================

    def obtener_detalle(self, resultado):

        estado = resultado["estado"]

        if estado == "ERROR":

            return " | ".join(
                resultado["errores"]
            )

        if estado == "ACTUALIZAR":

            cambios = resultado["cambios"]

            detalles = []

            for campo, cambio in cambios.items():

                detalles.append(
                    f"{campo}: "
                    f"{cambio['anterior']} "
                    f"→ "
                    f"{cambio['nuevo']}"
                )

            return " | ".join(
                detalles
            )

        if estado == "NUEVO":

            return (
                "Se agregará a la base de datos."
            )

        if estado == "SIN_CAMBIOS":

            return (
                "No se realizará ninguna modificación."
            )

        return ""

    # ======================================================
    # MOSTRAR DETALLE DEL REGISTRO SELECCIONADO
    # ======================================================

    def mostrar_detalle(self, event=None):

        seleccion = self.tree.selection()

        # --------------------------------------------------
        # Deshabilitar botón inicialmente
        # --------------------------------------------------

        self.boton_abrir_archivo.config(
            state="disabled"
        )

        if not seleccion:

            self.limpiar_detalle()

            return

        fila = int(
            seleccion[0]
        )

        resultado_seleccionado = None

        for resultado in self.resultados:

            if resultado["fila"] == fila:

                resultado_seleccionado = resultado

                break

        if resultado_seleccionado is None:

            self.limpiar_detalle()

            return

        # ==================================================
        # DATOS
        # ==================================================

        datos = resultado_seleccionado.get(
            "datos",
            {}
        )

        estado = resultado_seleccionado.get(
            "estado",
            ""
        )

        texto = []

        # ==================================================
        # NOMBRES AMIGABLES
        # ==================================================

        nombres_campos = {
            "id_docente": "ID Docente",
            "apellido": "Apellido",
            "nombre": "Nombre",
            "dni": "DNI",
            "cuil": "CUIL",
            "telefono": "Teléfono",
            "email": "Email",
            "direccion": "Dirección",
            "fecha_nacimiento": "Fecha de nacimiento",
        }

        orden_campos = [
            "id_docente",
            "apellido",
            "nombre",
            "dni",
            "cuil",
            "telefono",
            "email",
            "direccion",
            "fecha_nacimiento",
        ]

        campos_mostrados = set()

        # ==================================================
        # DATOS DEL REGISTRO
        # ==================================================

        texto.append(
            "DATOS DEL REGISTRO"
        )

        texto.append(
            "─" * 55
        )

        texto.append(
            f"Fila Excel: "
            f"{resultado_seleccionado['fila']}"
        )

        texto.append("")

        # --------------------------------------------------
        # Campos en orden
        # --------------------------------------------------

        for campo in orden_campos:

            if campo not in datos:

                continue

            valor = datos.get(
                campo,
                ""
            )

            if valor is None:

                valor = ""

            nombre_campo = nombres_campos.get(
                campo,
                campo.replace(
                    "_",
                    " "
                ).capitalize()
            )

            texto.append(
                f"{nombre_campo}: {valor}"
            )

            campos_mostrados.add(
                campo
            )

        # --------------------------------------------------
        # Campos adicionales
        # --------------------------------------------------

        for campo, valor in datos.items():

            if campo in campos_mostrados:

                continue

            if valor is None:

                valor = ""

            nombre_campo = nombres_campos.get(
                campo,
                campo.replace(
                    "_",
                    " "
                ).capitalize()
            )

            texto.append(
                f"{nombre_campo}: {valor}"
            )

        # ==================================================
        # ESTADO
        # ==================================================

        texto.append("")

        texto.append(
            "ESTADO DE IMPORTACIÓN"
        )

        texto.append(
            "─" * 55
        )

        texto.append(
            f"Estado: {estado}"
        )

        # ==================================================
        # ERRORES
        # ==================================================

        errores = (
            resultado_seleccionado.get(
                "errores",
                []
            )
        )

        if errores:

            texto.append("")

            texto.append(
                "ERRORES:"
            )

            for error in errores:

                texto.append(
                    f"  • {error}"
                )

        # ==================================================
        # ADVERTENCIAS
        # ==================================================

        advertencias = (
            resultado_seleccionado.get(
                "advertencias",
                []
            )
        )

        if advertencias:

            texto.append("")

            texto.append(
                "ADVERTENCIAS:"
            )

            for advertencia in advertencias:

                texto.append(
                    f"  • {advertencia}"
                )

        # ==================================================
        # CAMBIOS
        # ==================================================

        cambios = (
            resultado_seleccionado.get(
                "cambios",
                {}
            )
        )

        if cambios:

            texto.append("")

            texto.append(
                "CAMBIOS DETECTADOS:"
            )

            for campo, cambio in cambios.items():

                nombre_campo = nombres_campos.get(
                    campo,
                    campo.replace(
                        "_",
                        " "
                    ).capitalize()
                )

                texto.append(
                    f"  • {nombre_campo}:"
                )

                texto.append(
                    f"      Anterior: "
                    f"{cambio['anterior']}"
                )

                texto.append(
                    f"      Nuevo: "
                    f"{cambio['nuevo']}"
                )

        # ==================================================
        # RESULTADO FINAL
        # ==================================================

        texto.append("")

        texto.append(
            "RESULTADO:"
        )

        if estado == "NUEVO":

            texto.append(
                "  El registro será agregado "
                "a la base de datos."
            )

        elif estado == "ACTUALIZAR":

            texto.append(
                "  El registro existente será "
                "actualizado."
            )

        elif estado == "SIN_CAMBIOS":

            texto.append(
                "  No se realizará ninguna modificación."
            )

        elif estado == "ERROR":

            texto.append(
                "  El registro será omitido "
                "de la importación."
            )

            # ----------------------------------------------
            # Habilitar apertura del archivo
            # ----------------------------------------------

            if self.ruta_archivo.get().strip():

                self.boton_abrir_archivo.config(
                    state="normal"
                )

        # ==================================================
        # MOSTRAR
        # ==================================================

        self.texto_detalle.config(
            state="normal"
        )

        self.texto_detalle.delete(
            "1.0",
            "end"
        )

        self.texto_detalle.insert(
            "1.0",
            "\n".join(
                texto
            )
        )

        self.texto_detalle.config(
            state="disabled"
        )

    # ======================================================
    # ABRIR ARCHIVO PARA CORREGIR
    # ======================================================

    def abrir_archivo_para_corregir(self):

        ruta = self.ruta_archivo.get().strip()

        if not ruta:

            messagebox.showwarning(
                "Archivo de importación",
                "No hay ningún archivo Excel seleccionado.",
                parent=self.ventana
            )

            return

        if not os.path.exists(ruta):

            messagebox.showerror(
                "Archivo de importación",
                "El archivo seleccionado ya no existe "
                "en la ubicación indicada.",
                parent=self.ventana
            )

            return

        try:

            os.startfile(
                ruta
            )

        except Exception as e:

            messagebox.showerror(
                "Abrir archivo",
                "No fue posible abrir el archivo "
                "con el programa asociado a Excel.\n\n"
                f"{e}",
                parent=self.ventana
            )

            return

        messagebox.showinfo(
            "Corregir archivo",
            "Se abrió el archivo de importación.\n\n"
            "Corrija los datos necesarios y guarde "
            "el archivo.\n\n"
            "Luego vuelva al SGE y pulse "
            "\"Analizar archivo\" para comprobar "
            "nuevamente los datos.",
            parent=self.ventana
        )

    # ======================================================
    # CONFIRMAR IMPORTACIÓN
    # ======================================================

    def confirmar_importacion(self):

        if not self.importacion_procesada:

            messagebox.showwarning(
                "Importación",
                "Primero debe analizar un archivo.",
                parent=self.ventana
            )

            return

        operaciones = (
            self.resumen["nuevos"]
            + self.resumen["actualizar"]
        )

        if operaciones == 0:

            messagebox.showinfo(
                "Importación",
                "No hay cambios para guardar.",
                parent=self.ventana
            )

            return

        mensaje = (
            "Se encontraron los siguientes "
            "cambios:\n\n"
            f"Nuevos: {self.resumen['nuevos']}\n"
            f"Actualizar: "
            f"{self.resumen['actualizar']}\n"
            f"Sin cambios: "
            f"{self.resumen['sin_cambios']}\n"
            f"Errores: "
            f"{self.resumen['errores']}\n\n"
            "¿Desea confirmar la importación?"
        )

        confirmar = messagebox.askyesno(
            "Confirmar importación",
            mensaje,
            parent=self.ventana
        )

        if not confirmar:

            return

        try:

            resultado_guardado = (
                guardar_importacion_docentes(
                    self.resultados
                )
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                "Ocurrió un error durante "
                "el guardado:\n\n"
                f"{e}",
                parent=self.ventana
            )

            return

        if not resultado_guardado["exito"]:

            messagebox.showerror(
                "Importación",
                "La importación NO fue completada.\n\n"
                + "\n".join(
                    resultado_guardado[
                        "errores"
                    ]
                ),
                parent=self.ventana
            )

            return

        self.importacion_guardada = True

        self.boton_confirmar.config(
            state="disabled"
        )

        messagebox.showinfo(
            "Importación completada",
            "La importación se realizó correctamente.\n\n"
            f"Insertados: "
            f"{resultado_guardado['insertados']}\n"
            f"Actualizados: "
            f"{resultado_guardado['actualizados']}\n"
            f"Omitidos: "
            f"{resultado_guardado['omitidos']}",
            parent=self.ventana
        )

    # ======================================================
    # LIMPIAR DETALLE
    # ======================================================

    def limpiar_detalle(self):

        self.texto_detalle.config(
            state="normal"
        )

        self.texto_detalle.delete(
            "1.0",
            "end"
        )

        self.texto_detalle.config(
            state="disabled"
        )

    # ======================================================
    # LIMPIAR RESULTADOS
    # ======================================================

    def limpiar_resultados(self):

        self.resultados = []

        self.resumen = None

        self.importacion_procesada = False

        self.importacion_guardada = False

        self.boton_confirmar.config(
            state="disabled"
        )

        self.boton_abrir_archivo.config(
            state="disabled"
        )

        for item in self.tree.get_children():

            self.tree.delete(
                item
            )

        self.lbl_total.config(
            text="Total: 0"
        )

        self.lbl_nuevos.config(
            text="Nuevos: 0"
        )

        self.lbl_actualizar.config(
            text="Actualizar: 0"
        )

        self.lbl_sin_cambios.config(
            text="Sin cambios: 0"
        )

        self.lbl_errores.config(
            text="Errores: 0"
        )

        self.limpiar_detalle()

    # ======================================================
    # CERRAR
    # ======================================================

    def cerrar(self):

        self.ventana.destroy()


# ==========================================================
# FUNCIÓN PÚBLICA
# ==========================================================

def abrir_ventana_importacion(parent):
    """
    Abre la ventana secundaria de importación.

    El parent debe ser la ventana principal
    del SGE.
    """

    VentanaImportacion(
        parent
    )