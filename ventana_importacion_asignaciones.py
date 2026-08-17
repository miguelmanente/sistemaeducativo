# ==========================================================
# SGE - VENTANA DE IMPORTACIÓN DE ASIGNACIONES
# Archivo: ventana_importacion_asignaciones.py
# ==========================================================

import os
import tkinter as tk
from tkinter import ttk, messagebox

from importador_asignaciones import (
    obtener_archivos_excel,
    analizar_archivo,
    importar_registros
)


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

COLOR_FONDO = "#f4f6f8"
COLOR_TITULO = "#1f4e78"
COLOR_VERDE = "#2e7d32"
COLOR_ROJO = "#c62828"
COLOR_NARANJA = "#ef6c00"
COLOR_AZUL = "#1565c0"


# ==========================================================
# VENTANA PRINCIPAL
# ==========================================================

def abrir_ventana_importacion_asignaciones(
    ventana_padre=None
):

    ventana = tk.Toplevel(
        ventana_padre
    )

    ventana.title(
        "Importación de Asignaciones Docentes"
    )

    ventana.geometry(
        "1100x700"
    )

    ventana.minsize(
        950,
        600
    )

    ventana.configure(
        bg=COLOR_FONDO
    )

    ventana.transient(
        ventana_padre
    )

    ventana.grab_set()

    # ======================================================
    # VARIABLES
    # ======================================================

    archivo_seleccionado = tk.StringVar()

    total_var = tk.StringVar(
        value="0"
    )

    nuevas_var = tk.StringVar(
        value="0"
    )

    existentes_var = tk.StringVar(
        value="0"
    )

    errores_var = tk.StringVar(
        value="0"
    )

    advertencias_var = tk.StringVar(
        value="0"
    )

    resultado_actual = {
        "datos": None
    }

    # ======================================================
    # FUNCIONES
    # ======================================================

    def invalidar_resultado():

        resultado_actual["datos"] = None

        total_var.set("0")
        nuevas_var.set("0")
        existentes_var.set("0")
        errores_var.set("0")
        advertencias_var.set("0")

        boton_importar.config(
            state=tk.DISABLED
        )

        texto_resultado.delete(
            "1.0",
            tk.END
        )

    # ------------------------------------------------------

    def actualizar_archivos():

        archivos = obtener_archivos_excel()

        combo_archivos["values"] = archivos

        if archivos:

            archivo_actual = archivo_seleccionado.get()

            if archivo_actual in archivos:

                archivo_seleccionado.set(
                    archivo_actual
                )

            else:

                archivo_seleccionado.set(
                    archivos[0]
                )

        else:

            archivo_seleccionado.set("")

        invalidar_resultado()

    # ------------------------------------------------------

    def abrir_excel():

        archivo = archivo_seleccionado.get()

        if not archivo:

            messagebox.showwarning(
                "Abrir Excel",
                "No hay ningún archivo Excel seleccionado.",
                parent=ventana
            )

            return

        if not os.path.isfile(
            archivo
        ):

            messagebox.showerror(
                "Archivo no encontrado",
                "El archivo seleccionado ya no existe.",
                parent=ventana
            )

            actualizar_archivos()

            return

        try:

            os.startfile(
                os.path.abspath(
                    archivo
                )
            )

        except AttributeError:

            messagebox.showerror(
                "Sistema no compatible",
                "La apertura directa del archivo Excel "
                "está configurada para Windows.",
                parent=ventana
            )

        except Exception as e:

            messagebox.showerror(
                "Error al abrir Excel",
                "No se pudo abrir el archivo Excel:\n\n"
                f"{e}",
                parent=ventana
            )

    # ------------------------------------------------------

    def mostrar_resultado(
        resultado
    ):

        resultado_actual["datos"] = resultado

        total_var.set(
            str(
                resultado.get(
                    "total",
                    0
                )
            )
        )

        nuevas_var.set(
            str(
                resultado.get(
                    "correctos",
                    0
                )
            )
        )

        existentes_var.set(
            str(
                resultado.get(
                    "existentes",
                    0
                )
            )
        )

        errores_var.set(
            str(
                resultado.get(
                    "errores",
                    0
                )
            )
        )

        advertencias_var.set(
            str(
                resultado.get(
                    "advertencias",
                    0
                )
            )
        )

        texto_resultado.delete(
            "1.0",
            tk.END
        )

        # ==================================================
        # RESUMEN
        # ==================================================

        texto_resultado.insert(
            tk.END,
            "RESULTADO DEL ANÁLISIS\n",
            "titulo"
        )

        texto_resultado.insert(
            tk.END,
            "\n"
        )

        texto_resultado.insert(
            tk.END,
            f"Total de registros: "
            f"{resultado.get('total', 0)}\n"
        )

        texto_resultado.insert(
            tk.END,
            f"Nuevas asignaciones: "
            f"{resultado.get('correctos', 0)}\n"
        )

        texto_resultado.insert(
            tk.END,
            f"Asignaciones ya existentes: "
            f"{resultado.get('existentes', 0)}\n"
        )

        texto_resultado.insert(
            tk.END,
            f"Errores: "
            f"{resultado.get('errores', 0)}\n"
        )

        texto_resultado.insert(
            tk.END,
            f"Advertencias: "
            f"{resultado.get('advertencias', 0)}\n"
        )

        texto_resultado.insert(
            tk.END,
            "\n"
        )

        # ==================================================
        # EXISTENTES
        # ==================================================

        existentes = resultado.get(
            "detalle_existentes",
            []
        )

        if existentes:

            texto_resultado.insert(
                tk.END,
                "ASIGNACIONES YA EXISTENTES\n",
                "existente"
            )

            texto_resultado.insert(
                tk.END,
                "\n"
            )

            for item in existentes:

                fila = item.get(
                    "fila",
                    ""
                )

                id_asignacion = item.get(
                    "id_asignacion",
                    ""
                )

                mensaje = item.get(
                    "mensaje",
                    ""
                )

                texto_resultado.insert(
                    tk.END,
                    f"Fila {fila}"
                )

                if id_asignacion:

                    texto_resultado.insert(
                        tk.END,
                        f" - ID {id_asignacion}"
                    )

                texto_resultado.insert(
                    tk.END,
                    f": {mensaje}\n"
                )

            texto_resultado.insert(
                tk.END,
                "\n"
            )

        # ==================================================
        # ERRORES
        # ==================================================

        errores = resultado.get(
            "detalle_errores",
            []
        )

        if errores:

            texto_resultado.insert(
                tk.END,
                "ERRORES QUE DEBEN CORREGIRSE EN EXCEL\n",
                "error"
            )

            texto_resultado.insert(
                tk.END,
                "\n"
            )

            for item in errores:

                fila = item.get(
                    "fila",
                    ""
                )

                texto_resultado.insert(
                    tk.END,
                    f"Fila {fila}:\n",
                    "error"
                )

                for mensaje in item.get(
                    "errores",
                    []
                ):

                    texto_resultado.insert(
                        tk.END,
                        f"   • {mensaje}\n"
                    )

                texto_resultado.insert(
                    tk.END,
                    "\n"
                )

        # ==================================================
        # ADVERTENCIAS
        # ==================================================

        advertencias = resultado.get(
            "detalle_advertencias",
            []
        )

        if advertencias:

            texto_resultado.insert(
                tk.END,
                "ADVERTENCIAS\n",
                "advertencia"
            )

            texto_resultado.insert(
                tk.END,
                "\n"
            )

            for item in advertencias:

                fila = item.get(
                    "fila",
                    ""
                )

                texto_resultado.insert(
                    tk.END,
                    f"Fila {fila}:\n"
                )

                for mensaje in item.get(
                    "advertencias",
                    []
                ):

                    texto_resultado.insert(
                        tk.END,
                        f"   • {mensaje}\n"
                    )

                texto_resultado.insert(
                    tk.END,
                    "\n"
                )

        # ==================================================
        # ESTADO FINAL
        # ==================================================

        texto_resultado.insert(
            tk.END,
            "\n"
        )

        if resultado.get(
            "errores",
            0
        ) > 0:

            texto_resultado.insert(
                tk.END,
                "IMPORTACIÓN BLOQUEADA.\n",
                "error"
            )

            texto_resultado.insert(
                tk.END,
                "Corregí los errores directamente "
                "en el archivo Excel y volvé a analizar."
            )

            boton_importar.config(
                state=tk.DISABLED
            )

        elif resultado.get(
            "correctos",
            0
        ) > 0:

            texto_resultado.insert(
                tk.END,
                "EL ARCHIVO ESTÁ LISTO PARA IMPORTAR.\n",
                "correcto"
            )

            boton_importar.config(
                state=tk.NORMAL
            )

        else:

            texto_resultado.insert(
                tk.END,
                "NO HAY ASIGNACIONES NUEVAS "
                "PARA IMPORTAR.",
                "existente"
            )

            boton_importar.config(
                state=tk.DISABLED
            )

    # ------------------------------------------------------

    def analizar():

        archivo = archivo_seleccionado.get()

        if not archivo:

            messagebox.showwarning(
                "Importación de asignaciones",
                "No hay ningún archivo Excel seleccionado.",
                parent=ventana
            )

            return

        if not os.path.isfile(
            archivo
        ):

            messagebox.showerror(
                "Archivo no encontrado",
                "El archivo seleccionado ya no existe.",
                parent=ventana
            )

            actualizar_archivos()

            return

        resultado_actual["datos"] = None

        boton_analizar.config(
            state=tk.DISABLED
        )

        boton_importar.config(
            state=tk.DISABLED
        )

        ventana.update_idletasks()

        try:

            resultado = analizar_archivo(
                archivo
            )

            mostrar_resultado(
                resultado
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                "Ocurrió un error durante el análisis:\n\n"
                f"{e}",
                parent=ventana
            )

        finally:

            boton_analizar.config(
                state=tk.NORMAL
            )

    # ------------------------------------------------------

    def importar():

        resultado = resultado_actual.get(
            "datos"
        )

        if not resultado:

            messagebox.showwarning(
                "Importación",
                "Primero debés analizar el archivo.",
                parent=ventana
            )

            return

        if resultado.get(
            "errores",
            0
        ) > 0:

            messagebox.showerror(
                "Importación bloqueada",
                "Hay errores que deben corregirse "
                "directamente en el Excel.",
                parent=ventana
            )

            return

        cantidad = resultado.get(
            "correctos",
            0
        )

        if cantidad <= 0:

            messagebox.showinfo(
                "Importación",
                "No hay asignaciones nuevas "
                "para importar.",
                parent=ventana
            )

            return

        respuesta = messagebox.askyesno(
            "Confirmar importación",
            (
                "Se encontraron "
                f"{cantidad} asignación(es) nuevas.\n\n"
                "Las asignaciones que ya existen "
                "no serán duplicadas.\n\n"
                "¿Deseás realizar la importación?"
            ),
            parent=ventana
        )

        if not respuesta:

            return

        boton_importar.config(
            state=tk.DISABLED
        )

        boton_analizar.config(
            state=tk.DISABLED
        )

        ventana.update_idletasks()

        try:

            ok, mensaje = importar_registros(
                resultado
            )

            if ok:

                messagebox.showinfo(
                    "Importación finalizada",
                    mensaje,
                    parent=ventana
                )

                analizar()

            else:

                messagebox.showerror(
                    "Error de importación",
                    mensaje,
                    parent=ventana
                )

                boton_analizar.config(
                    state=tk.NORMAL
                )

        except Exception as e:

            messagebox.showerror(
                "Error",
                "Ocurrió un error durante la importación:\n\n"
                f"{e}",
                parent=ventana
            )

            boton_analizar.config(
                state=tk.NORMAL
            )

    # ------------------------------------------------------

    def cerrar():

        try:

            ventana.grab_release()

        except Exception:

            pass

        ventana.destroy()

    # ======================================================
    # TÍTULO
    # ======================================================

    marco_titulo = tk.Frame(
        ventana,
        bg=COLOR_TITULO,
        height=65
    )

    marco_titulo.pack(
        fill="x",
        side="top"
    )

    marco_titulo.pack_propagate(
        False
    )

    tk.Label(
        marco_titulo,
        text="IMPORTACIÓN DE ASIGNACIONES DOCENTES",
        font=(
            "Segoe UI",
            18,
            "bold"
        ),
        fg="white",
        bg=COLOR_TITULO
    ).pack(
        pady=17
    )

    # ======================================================
    # MARCO ARCHIVO
    # ======================================================

    marco_archivo = tk.LabelFrame(
        ventana,
        text=" Archivo de importación ",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        bg=COLOR_FONDO,
        padx=15,
        pady=12
    )

    marco_archivo.pack(
        fill="x",
        side="top",
        padx=20,
        pady=(20, 10)
    )

    tk.Label(
        marco_archivo,
        text="Archivo Excel:",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 10)
    )

    combo_archivos = ttk.Combobox(
        marco_archivo,
        textvariable=archivo_seleccionado,
        state="readonly",
        width=65
    )

    combo_archivos.pack(
        side="left",
        fill="x",
        expand=True,
        padx=5
    )

    boton_actualizar = ttk.Button(
        marco_archivo,
        text="ACTUALIZAR",
        command=actualizar_archivos
    )

    boton_actualizar.pack(
        side="left",
        padx=(10, 5)
    )

    boton_abrir_excel = ttk.Button(
        marco_archivo,
        text="ABRIR EXCEL",
        command=abrir_excel
    )

    boton_abrir_excel.pack(
        side="left",
        padx=(5, 0)
    )

    # ======================================================
    # MARCO ANALIZAR
    # ======================================================

    marco_acciones = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    marco_acciones.pack(
        fill="x",
        side="top",
        padx=20,
        pady=10
    )

    boton_analizar = ttk.Button(
        marco_acciones,
        text="ANALIZAR ARCHIVO",
        command=analizar
    )

    boton_analizar.pack(
        side="left"
    )

    # ======================================================
    # MARCO RESUMEN
    # ======================================================

    marco_resumen = tk.LabelFrame(
        ventana,
        text=" Resultado del análisis ",
        font=(
            "Segoe UI",
            11,
            "bold"
        ),
        bg=COLOR_FONDO,
        padx=15,
        pady=12
    )

    marco_resumen.pack(
        fill="x",
        side="top",
        padx=20,
        pady=10
    )

    # ------------------------------------------------------
    # TOTAL
    # ------------------------------------------------------

    tk.Label(
        marco_resumen,
        text="Total:",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 5)
    )

    tk.Label(
        marco_resumen,
        textvariable=total_var,
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 25)
    )

    # ------------------------------------------------------
    # NUEVAS
    # ------------------------------------------------------

    tk.Label(
        marco_resumen,
        text="Nuevas:",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_VERDE,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 5)
    )

    tk.Label(
        marco_resumen,
        textvariable=nuevas_var,
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_VERDE,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 25)
    )

    # ------------------------------------------------------
    # EXISTENTES
    # ------------------------------------------------------

    tk.Label(
        marco_resumen,
        text="Ya existentes:",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_AZUL,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 5)
    )

    tk.Label(
        marco_resumen,
        textvariable=existentes_var,
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_AZUL,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 25)
    )

    # ------------------------------------------------------
    # ERRORES
    # ------------------------------------------------------

    tk.Label(
        marco_resumen,
        text="Errores:",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_ROJO,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 5)
    )

    tk.Label(
        marco_resumen,
        textvariable=errores_var,
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_ROJO,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 25)
    )

    # ------------------------------------------------------
    # ADVERTENCIAS
    # ------------------------------------------------------

    tk.Label(
        marco_resumen,
        text="Advertencias:",
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_NARANJA,
        bg=COLOR_FONDO
    ).pack(
        side="left",
        padx=(0, 5)
    )

    tk.Label(
        marco_resumen,
        textvariable=advertencias_var,
        font=(
            "Segoe UI",
            10,
            "bold"
        ),
        fg=COLOR_NARANJA,
        bg=COLOR_FONDO
    ).pack(
        side="left"
    )

    # ======================================================
    # BOTONES INFERIORES
    #
    # ESTE MARCO SE CREA ANTES DEL ÁREA DE RESULTADOS
    # PARA RESERVAR EL ESPACIO DE LOS BOTONES.
    # ======================================================

    marco_botones = tk.Frame(
        ventana,
        bg=COLOR_FONDO,
        height=55
    )

    marco_botones.pack(
        fill="x",
        side="bottom",
        padx=20,
        pady=(5, 15)
    )

    marco_botones.pack_propagate(
        False
    )

    boton_importar = ttk.Button(
        marco_botones,
        text="IMPORTAR",
        command=importar,
        state=tk.DISABLED
    )

    boton_importar.pack(
        side="left",
        padx=(0, 10)
    )

    boton_cerrar = ttk.Button(
        marco_botones,
        text="CERRAR",
        command=cerrar
    )

    boton_cerrar.pack(
        side="right"
    )

    # ======================================================
    # ÁREA DE RESULTADOS
    #
    # ESTA ÁREA OCUPA SOLAMENTE EL ESPACIO RESTANTE.
    # LOS BOTONES INFERIORES QUEDAN SIEMPRE VISIBLES.
    # ======================================================

    marco_detalle = tk.Frame(
        ventana,
        bg=COLOR_FONDO
    )

    marco_detalle.pack(
        fill="both",
        expand=True,
        side="top",
        padx=20,
        pady=(5, 5)
    )

    texto_resultado = tk.Text(
        marco_detalle,
        wrap="word",
        font=(
            "Consolas",
            10
        ),
        bg="white",
        relief="solid",
        borderwidth=1
    )

    texto_resultado.pack(
        side="left",
        fill="both",
        expand=True
    )

    scroll_resultado = ttk.Scrollbar(
        marco_detalle,
        orient="vertical",
        command=texto_resultado.yview
    )

    scroll_resultado.pack(
        side="right",
        fill="y"
    )

    texto_resultado.configure(
        yscrollcommand=scroll_resultado.set
    )

    # ======================================================
    # ESTILOS DEL TEXTO
    # ======================================================

    texto_resultado.tag_configure(
        "titulo",
        font=(
            "Segoe UI",
            12,
            "bold"
        )
    )

    texto_resultado.tag_configure(
        "correcto",
        foreground=COLOR_VERDE,
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )

    texto_resultado.tag_configure(
        "existente",
        foreground=COLOR_AZUL,
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )

    texto_resultado.tag_configure(
        "error",
        foreground=COLOR_ROJO,
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )

    texto_resultado.tag_configure(
        "advertencia",
        foreground=COLOR_NARANJA,
        font=(
            "Segoe UI",
            10,
            "bold"
        )
    )

    # ======================================================
    # CARGA INICIAL
    # ======================================================

    actualizar_archivos()

    # ======================================================
    # CERRAR CON X
    # ======================================================

    ventana.protocol(
        "WM_DELETE_WINDOW",
        cerrar
    )

    return ventana


# ==========================================================
# FIN DEL MÓDULO
# ==========================================================
