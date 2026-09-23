# =====================================================
#            MÓDULO SISTEMA EDUCATIVO - APP
# =====================================================

# ----------------------------- LIBRERÍAS -------------------------------

import sys
from pathlib import Path

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import font

from PIL import Image, ImageTk

from altaAsisgnacion import info_asignaciones
from database import crear_tablas
from centraVent import centrar_ventana
from datosDocentes import info_profesor
from altaMaterias import info_materias
from rankingInasistencia import RankingInasistenciasApp
import sesion
from estilos import configurar_estilos
from trayectoriaDocente import abrir_trayectoria_docente
from parteDiario import abrir_parte_diario
from inasistencia_v2 import InasistenciaDocente
from listadoSR import ModuloListados
from resumen_inasistencias import ventana_resumen
from ciclo_lectivo import ventana_ciclo_lectivo
from dias_no_laborables import ventana_dias_no_laborables
from ventana_importacion import VentanaImportacion
from ventana_importacion_asignaciones import abrir_ventana_importacion_asignaciones
from listadoTodo import VentanaReportesPDF
from ventana_manual import abrir_manual


# =====================================================
#             RUTA DE RECURSOS DEL SGE
# =====================================================
def obtener_carpeta_sge():

    """
    Devuelve la carpeta donde se encuentran
    los recursos de SGE.

    En desarrollo:
        carpeta del archivo app.py

    En versión compilada con PyInstaller:
        carpeta interna de recursos (_internal)
    """

    if getattr(sys, "frozen", False):

        return Path(
            sys._MEIPASS
        )

    return Path(
        __file__
    ).resolve().parent


def obtener_recurso(nombre_archivo):

    """
    Devuelve la ruta completa de un recurso
    de SGE.
    """

    return (
        obtener_carpeta_sge()
        / nombre_archivo
    )


# =====================================================
#       CREACIÓN DE VENTANA ABRIR SISTEMA
# =====================================================

def pPrincipal():

    crear_tablas()

    # =================================================
    #              PANTALLA ACERCA DE
    # =================================================

    def acerca_de():

        win = tk.Toplevel(ventana)

        win.title("Acerca de")
        win.geometry("400x250")
        win.resizable(False, False)

        try:

            ruta_logo = obtener_recurso(
                "logotipo.png"
            )

            imagen = Image.open(
                ruta_logo
            )

            imagen = imagen.resize(
                (120, 120)
            )

            logo = ImageTk.PhotoImage(
                imagen
            )

            lbl_logo = ttk.Label(
                win,
                image=logo
            )

            lbl_logo.image = logo

            lbl_logo.pack(
                pady=10
            )

        except Exception as e:

            print(
                f"No se pudo cargar el logotipo: {e}"
            )

            ttk.Label(
                win,
                text="[Logo no disponible]"
            ).pack(
                pady=10
            )

        ttk.Label(
            win,
            text="Sistema de Gestión Académica",
            font=("Arial", 16, "bold")
        ).pack(
            pady=15
        )

        ttk.Label(
            win,
            text="Versión 1.9",
            font=("Arial", 11)
        ).pack()

        ttk.Label(
            win,
            text="Desarrollado por:\nMiguel Ángel Manente",
            font=("Arial", 11)
        ).pack(
            pady=15
        )

        ttk.Label(
            win,
            text="© 2026",
            font=("Arial", 10)
        ).pack()

        ttk.Button(
            win,
            text="Cerrar",
            command=win.destroy
        ).pack(
            pady=20
        )

        centrar_ventana(win)

    # =================================================
    #                   SALIR
    # =================================================

    def salir():

        if messagebox.askyesno(
            "Salir",
            "¿Desea cerrar Sistema de Gestión Educativo?",
            parent=ventana
        ):

            ventana.destroy()

    # =================================================
    #              VENTANA PRINCIPAL
    # =================================================

    ventana = tk.Toplevel()

    ventana.title(
        "SISTEMA ACADÉMICO"
    )

    ventana.state(
        "zoomed"
    )

    ventana.rowconfigure(
        0,
        weight=1
    )

    ventana.rowconfigure(
        1,
        weight=0
    )

    ventana.columnconfigure(
        0,
        weight=1
    )

    # =================================================
    #                   TOP BAR
    # =================================================

    frame_top = tk.Frame(
        ventana,
        bg="#2c3e50",
        height=30
    )

    frame_top.pack(
        fill="x"
    )

    lbl_usuario = tk.Label(
        frame_top,
        text=f"Usuario: {sesion.usuario_actual}",
        bg="#2c3e50",
        fg="white",
        font=("Arial", 10, "bold")
    )

    lbl_usuario.pack(
        side="right",
        padx=10
    )

    # =================================================
    #                 BARRA DE MENÚ
    # =================================================

    barramenu = tk.Menu(
        ventana
    )

    ventana.config(
        menu=barramenu
    )

    # =================================================
    #                    ARCHIVO
    # =================================================

    mArchivo = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Archivo",
        menu=mArchivo
    )

    mArchivo.add_command(
        label="Importar datos Docentes a B.D.",
        command=lambda: VentanaImportacion(ventana)
    )

    mArchivo.add_command(
        label="Importar Asignación de Docentes",
        command=abrir_ventana_importacion_asignaciones
    )

    mArchivo.add_command(
        label="Salir",
        command=salir
    )

    # =================================================
    #                    PROFESOR
    # =================================================

    mProfesor = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Profesor",
        menu=mProfesor
    )

    mProfesor.add_command(
        label="Datos Docentes",
        command=info_profesor
    )

    mProfesor.add_command(
        label="Listados Situación Revista",
        command=lambda: ModuloListados(ventana)
    )

    # =================================================
    #                    MATERIAS
    # =================================================

    mMaterias = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Materias",
        menu=mMaterias
    )

    mMaterias.add_command(
        label="Agregar Materias",
        command=info_materias
    )

    # =================================================
    #              ASIGNACIONES DOCENTES
    # =================================================

    mAsignaciones = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Asignaciones Docentes",
        menu=mAsignaciones
    )

    mAsignaciones.add_command(
        label="Asignaciones Profesores",
        command=info_asignaciones
    )

    mAsignaciones.add_command(
        label="Listados Cursos, Cargos...",
        command=lambda: VentanaReportesPDF(ventana)
    )

    # =================================================
    #              HISTORIAL DOCENTE
    # =================================================

    mHistorial = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Historial Docente",
        menu=mHistorial
    )

    mHistorial.add_command(
        label="Visualizar Trayectoria",
        command=abrir_trayectoria_docente
    )

    # =================================================
    #                  PARTE DIARIO
    # =================================================

    mParteDiario = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Parte Diario",
        menu=mParteDiario
    )

    mParteDiario.add_command(
        label="Listado Planillas Diarias",
        command=abrir_parte_diario
    )

    # =================================================
    #             INASISTENCIAS DOCENTES
    # =================================================

    mAsistencias = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Inasistencias Docentes",
        menu=mAsistencias
    )

    mAsistencias.add_command(
        label="Altas Inasistencias",
        command=InasistenciaDocente
    )

    mAsistencias.add_command(
        label="Resumen Inasistencias Docente",
        command=ventana_resumen
    )

    mAsistencias.add_command(
        label="Ranking Inasistencias",
        command=lambda: RankingInasistenciasApp(ventana)
    )

    # =================================================
    #                 CONFIGURACIÓN
    # =================================================

    mConfiguracion = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Configuración",
        menu=mConfiguracion
    )

    mConfiguracion.add_command(
        label="Ciclo Lectivo",
        command=ventana_ciclo_lectivo
    )

    mConfiguracion.add_command(
        label="Días No Laborables",
        command=ventana_dias_no_laborables
    )

    # =================================================
    #                       AYUDA
    # =================================================

    mAcerca = tk.Menu(
        barramenu,
        tearoff=0
    )

    barramenu.add_cascade(
        label="Ayuda",
        menu=mAcerca
    )

    mAcerca.add_command(
        label="Acerca de la App",
        command=acerca_de
    )

    mAcerca.add_command(
        label="Manual de usuario",
        command=lambda: abrir_manual(ventana)
    )

    # =================================================
    #                  LOGO PRINCIPAL
    # =================================================

    logoP = tk.Frame(
        ventana
    )

    logoP.pack(
        expand=True
    )

    try:

        ruta_logo_principal = obtener_recurso(
            "logos.png"
        )

        logo = Image.open(
            ruta_logo_principal
        )

        logo = logo.resize(
            (600, 400)
        )

        logo_tk = ImageTk.PhotoImage(
            logo
        )

        label_logo = tk.Label(
            logoP,
            image=logo_tk
        )

        label_logo.image = logo_tk

        label_logo.pack(
            pady=(10, 5)
        )

    except Exception as e:

        print(
            f"No se pudo cargar el logo: {e}"
        )

        label_logo = tk.Label(
            logoP,
            text="[Logo no disponible]"
        )

        label_logo.pack(
            pady=(10, 5)
        )

    # =================================================
    #                 TEXTO BAJO LOGO
    # =================================================

    label_text = tk.Label(
        logoP,
        text="Sistema de Gestión Escolar",
        font=("Arial", 20, "bold")
    )

    label_text.pack(
        pady=(0, 10)
    )

    # =================================================
    #                      FOOTER
    # =================================================

    try:

        ruta_logo_footer = obtener_recurso(
            "logo2.png"
        )

        img = Image.open(
            ruta_logo_footer
        )

        img = img.resize(
            (120, 80)
        )

        logo = ImageTk.PhotoImage(
            img
        )

    except Exception as e:

        print(
            f"No se pudo cargar el logo del pie: {e}"
        )

        logo = None

    frame_footer = tk.Frame(
        ventana
    )

    frame_footer.pack(
        side="bottom",
        anchor="w",
        padx=10,
        pady=5
    )

    if logo is not None:

        lbl_logo = tk.Label(
            frame_footer,
            image=logo
        )

        lbl_logo.pack(
            anchor="w"
        )

    else:

        lbl_logo = tk.Label(
            frame_footer,
            text="[Logo no disponible]"
        )

        lbl_logo.pack(
            anchor="w"
        )

    lbl_texto = tk.Label(
        frame_footer,
        text="© 2026 Manente Miguel Ángel",
        font=("Arial", 12),
        fg="gray"
    )

    lbl_texto.pack(
        anchor="w"
    )

    lbl_logo.image = logo

    # =================================================
    #                  ESTILOS Y CENTRADO
    # =================================================

    configurar_estilos()

    centrar_ventana(
        ventana
    )