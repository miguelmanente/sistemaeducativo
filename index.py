# =====================================================
#        MÓDULO LOGIN DE USUARIO Y REGISTRACIÓN
# =====================================================

# -----------------------------------------  LIBRERÍAS ---------------------------------------------------

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk

from database import (
    registrar_usuario,
    validar_usuario,
    crear_tablas
)

from app import pPrincipal

from centraVent import (
    centrar_ventana,
    cventana
)

from registrar import ventana_registro

import sesion

from Backup import crear_backup

from estilos import configurar_estilos

from negocio.calendario_escolar import generar_calendario

# NUEVO:
# Ventana de Seguridad y Copias del SGE
from seguridad_sge import ventana_seguridad


# ------------------------------------------------ VARIABLE GLOBAL ----------------------------------------

usuario_logueado = None

# ---------------------------------------------------------------------------------------------------------


# ------------------------------------------- VENTANA PRINCIPAL -------------------------------------------

root = tk.Tk()

# Ocultar hasta que se realice el login
root.withdraw()

root.title("SISTEMA ACADÉMICO")

# ---------------------------------------------------------------------------------------------------------


# --------------------------------------------- LOGIN -----------------------------------------------------

def ventana_login(root, barramenu, lbl_usuario):

    global usuario_logueado

    # Aseguramos que las tablas existan
    # antes de validar usuarios
    crear_tablas()

    login = tk.Toplevel(
        root,
        bg="#ecf0f1",
        pady=30
    )

    configurar_estilos()

    login.title("LOGIN DE USUARIOS")
    login.geometry("500x400")

    # ---------------------------------------------------------------------------------------------
    # USUARIO
    # ---------------------------------------------------------------------------------------------

    tk.Label(
        login,
        text="Usuario",
        bg="#ecf0f1",
        font=("Arial", 12, "bold")
    ).pack(
        pady=15
    )

    entry_usuario = tk.Entry(
        login,
        font=("Arial", 12)
    )

    entry_usuario.pack()

    # ---------------------------------------------------------------------------------------------
    # CONTRASEÑA
    # ---------------------------------------------------------------------------------------------

    tk.Label(
        login,
        text="Contraseña",
        bg="#ecf0f1",
        font=("Arial", 12, "bold")
    ).pack(
        pady=15
    )

    entry_password = tk.Entry(
        login,
        show="*",
        font=("Arial", 12)
    )

    entry_password.pack()

    # ---------------------------------------------------------------------------------------------
    # INICIAR SESIÓN
    # ---------------------------------------------------------------------------------------------

    def iniciar_sesion():

        global usuario_logueado

        usuario = entry_usuario.get()
        password = entry_password.get()

        # -------------------------------------------------
        # VALIDAR USUARIO
        # -------------------------------------------------

        if not usuario.strip():

            messagebox.showwarning(
                "Advertencia",
                "Por favor, ingrese un nombre de usuario.",
                parent=login
            )

            return

        # -------------------------------------------------
        # VALIDAR CONTRASEÑA
        # -------------------------------------------------

        if not password:

            messagebox.showwarning(
                "Advertencia",
                "Por favor, ingrese una contraseña.",
                parent=login
            )

            return

        # -------------------------------------------------
        # VALIDACIÓN EN BASE DE DATOS
        # -------------------------------------------------

        if validar_usuario(
            usuario,
            password
        ):

            usuario_logueado = usuario

            sesion.usuario_actual = usuario

            lbl_usuario.config(
                text=f"Usuario: {usuario}"
            )

            # -------------------------------------------------
            # HABILITAR MENÚ
            # -------------------------------------------------

            for i in range(
                barramenu.index("end") + 1
            ):

                barramenu.entryconfig(
                    i,
                    state="normal"
                )

            messagebox.showinfo(
                "Bienvenido",
                f"Bienvenido, {usuario} ha ingresado "
                "al Sistema de Gestión Educativa"
            )

            login.destroy()

            # Mostrar sistema principal
            root.deiconify()

            root.state("zoomed")

        else:

            messagebox.showerror(
                "Error de Acceso",
                "Usuario o contraseña incorrectos.",
                parent=login
            )

            # Limpiar campos
            entry_usuario.delete(
                0,
                tk.END
            )

            entry_password.delete(
                0,
                tk.END
            )

            entry_usuario.focus()

    # ---------------------------------------------------------------------------------------------
    # ENTER PARA INICIAR SESIÓN
    # ---------------------------------------------------------------------------------------------

    entry_password.bind(
        "<Return>",
        lambda e: iniciar_sesion()
    )

    # ---------------------------------------------------------------------------------------------
    # SALIR
    # ---------------------------------------------------------------------------------------------

    def salir():

        root.destroy()

    # ---------------------------------------------------------------------------------------------
    # BOTONES
    # ---------------------------------------------------------------------------------------------

    tk.Button(
        login,
        text="Ingresar",
        bg="#3498db",
        fg="white",
        font=("Arial", 12, "bold"),
        command=iniciar_sesion
    ).pack(
        pady=15
    )

    tk.Button(
        login,
        text="Salir",
        bg="#3498db",
        fg="white",
        font=("Arial", 12, "bold"),
        command=salir
    ).pack(
        pady=15
    )

    # ---------------------------------------------------------------------------------------------

    cventana(login)


# =========================================================================================================
#                               FUNCIÓN CREAR BACKUP DESDE EL MENÚ
# =========================================================================================================

def ejecutar_backup():

    try:

        ruta_backup = crear_backup()

        messagebox.showinfo(
            "Backup del SGE",
            "El backup cifrado se creó correctamente.\n\n"
            f"Archivo:\n{ruta_backup}"
        )

    except Exception as error:

        messagebox.showerror(
            "Error de backup",
            "No fue posible crear el backup del SGE.\n\n"
            f"{error}"
        )


# =========================================================================================================
#                         ABRIR VENTANA DE SEGURIDAD
# =========================================================================================================

def abrir_seguridad():

    ventana_seguridad(root)


# ---------------- BARRA INDICADORA DE USUARIO LOGUEADO ------------------------------------------------

frame_top = tk.Frame(
    root,
    bg="#2c3e50",
    height=30
)

frame_top.pack(
    fill="x"
)


lbl_usuario = tk.Label(
    frame_top,
    text="Usuario: ---",
    bg="#2c3e50",
    fg="white",
    font=("Arial", 10, "bold")
)

lbl_usuario.pack(
    side="right",
    padx=10
)

# --------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------ BARRA DE MENÚES ---------------------------------------------

barramenu = tk.Menu(
    root
)

root.config(
    menu=barramenu
)


# =========================================================================================================
#                                             ARCHIVO
# =========================================================================================================

mArchivo = tk.Menu(
    barramenu,
    tearoff=0
)

barramenu.add_cascade(
    label="Archivo",
    menu=mArchivo
)


mArchivo.add_command(
    label="Abrir Sistema",
    command=pPrincipal
)


mArchivo.add_separator()


mArchivo.add_command(
    label="Salir",
    command=root.destroy
)


# =========================================================================================================
#                                            SEGURIDAD
# =========================================================================================================

mSeguridad = tk.Menu(
    barramenu,
    tearoff=0
)

barramenu.add_cascade(
    label="Seguridad",
    menu=mSeguridad
)


# -----------------------------------------------------------------------------------------
# REGISTRAR NUEVO USUARIO
# -----------------------------------------------------------------------------------------

mSeguridad.add_command(
    label="Registrar Nuevo Usuario",
    command=ventana_registro
)


mSeguridad.add_separator()


# -----------------------------------------------------------------------------------------
# SEGURIDAD Y COPIAS DEL SGE
# -----------------------------------------------------------------------------------------

mSeguridad.add_command(
    label="Seguridad y Copias del SGE",
    command=abrir_seguridad
)


# -----------------------------------------------------------------------------------------
# CREAR BACKUP DIRECTAMENTE
# -----------------------------------------------------------------------------------------

mSeguridad.add_separator()

mSeguridad.add_command(
    label="Crear backup cifrado",
    command=ejecutar_backup
)


# --------------------------------------------------------------------------------------------------------------------
# DESHABILITAR MENÚ HASTA EL LOGIN
# --------------------------------------------------------------------------------------------------------------------

for i in range(
    barramenu.index("end") + 1
):

    barramenu.entryconfig(
        i,
        state="disabled"
    )

# --------------------------------------------------------------------------------------------------------------------


# ---------------------------------- LOGO PRINCIPAL ------------------------------------------------------------------

logoP = tk.Frame(
    root
)

logoP.pack(
    expand=True
)


# Cargar logo

try:

    logo = Image.open(
        "logo.png"
    )

    logo = logo.resize(
        (500, 400)
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


# Texto debajo del logo

label_text = tk.Label(
    logoP,
    text="Sistema Educativo - Gestión Escolar",
    font=("Arial", 20, "bold")
)

label_text.pack(
    pady=(0, 10)
)

# ----------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------ FOOTER -------------------------------------------------------------

img = Image.open(
    "logo2.png"
)

img = img.resize(
    (120, 80)
)

logo = ImageTk.PhotoImage(
    img
)


frame_footer = tk.Frame(
    root
)

frame_footer.pack(
    side="bottom",
    anchor="w",
    padx=10,
    pady=5
)


lbl_logo = tk.Label(
    frame_footer,
    image=logo
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

# ----------------------------------------------------------------------------------------------------------------------


# ---------------- INICIAR LOGIN AUTOMÁTICO ---------------------------------------------------------------------------

ventana_login(
    root,
    barramenu,
    lbl_usuario
)


# Generar calendario del año actual

generar_calendario(
    2026
)


centrar_ventana(
    root
)


# IMPORTANTE:
#
# Ya NO se crea un backup automáticamente al iniciar.
#
# Los backups pueden crearse desde:
#
# Seguridad
#     ├── Seguridad y Copias del SGE
#     └── Crear backup cifrado
#
# ---------------------------------------------------------------------------------------------------------------------


root.mainloop()