
# =====================================================
#            MÓDULO REGISTRACIÓN DE USUARIOS
# =====================================================

import tkinter as tk
from tkinter import messagebox

from database import (
    registrar_usuario,
    validar_administrador
)

from centraVent import centrar_ventana


# =====================================================
#            VENTANA DE REGISTRACIÓN
# =====================================================

def ventana_registro():

    registro = tk.Toplevel()
    registro.title("REGISTRO DE USUARIO")
    registro.configure(bg="#ecf0f1")
    registro.resizable(False, False)
    registro.grab_set()

    # -------------------------------------------------
    # Tamaño de la ventana
    # -------------------------------------------------

    ancho = 450
    alto = 520

    pantalla_ancho = registro.winfo_screenwidth()
    pantalla_alto = registro.winfo_screenheight()

    pos_x = (pantalla_ancho - ancho) // 2
    pos_y = (pantalla_alto - alto) // 2

    registro.geometry(f"{ancho}x{alto}+{pos_x}+{pos_y}")

    # =================================================
    # ENCABEZADO
    # =================================================

    tk.Label(
        registro,
        text="REGISTRO DE USUARIO",
        bg="#ecf0f1",
        fg="#2c3e50",
        font=("Arial", 18, "bold")
    ).pack(pady=(20, 10))

    tk.Label(
        registro,
        text="Solo el administrador puede registrar nuevos usuarios",
        bg="#ecf0f1",
        fg="#7f8c8d",
        font=("Arial", 10)
    ).pack(pady=(0, 15))

    # =================================================
    # DATOS DEL ADMINISTRADOR
    # =================================================

    frame_admin = tk.Frame(
        registro,
        bg="#ecf0f1"
    )
    frame_admin.pack(fill="x", padx=40)

    tk.Label(
        frame_admin,
        text="Administrador",
        bg="#ecf0f1",
        fg="#2c3e50",
        font=("Arial", 11, "bold")
    ).pack(anchor="w")

    entry_admin = tk.Entry(
        frame_admin,
        font=("Arial", 12)
    )
    entry_admin.pack(fill="x", pady=(5, 10))

    tk.Label(
        frame_admin,
        text="Contraseña",
        bg="#ecf0f1",
        fg="#2c3e50",
        font=("Arial", 11, "bold")
    ).pack(anchor="w")

    entry_password_admin = tk.Entry(
        frame_admin,
        show="*",
        font=("Arial", 12)
    )
    entry_password_admin.pack(fill="x", pady=(5, 10))

    # =================================================
    # FUNCIÓN DE VERIFICACIÓN DEL ADMINISTRADOR
    # =================================================

    def habilitar_registro():

        usuario_admin = entry_admin.get().strip()
        password_admin = entry_password_admin.get()

        if not usuario_admin or not password_admin:

            messagebox.showwarning(
                "Advertencia",
                "Ingrese el usuario y la contraseña del administrador.",
                parent=registro
            )

            return

        administrador = validar_administrador(
            usuario_admin,
            password_admin
        )

        if not administrador:

            messagebox.showerror(
                "Acceso denegado",
                "Los datos del administrador son incorrectos.",
                parent=registro
            )

            entry_password_admin.delete(0, tk.END)
            entry_password_admin.focus()

            return

        # -------------------------------------------------
        # Administrador validado
        # -------------------------------------------------

        entry_admin.config(state="disabled")
        entry_password_admin.config(state="disabled")
        btn_verificar.config(state="disabled")

        frame_nuevo_usuario.pack(
            fill="x",
            padx=40,
            pady=(15, 0)
        )

        btn_registrar.pack(
            pady=(15, 5)
        )

        messagebox.showinfo(
            "Administrador validado",
            "Acceso autorizado.\n\nAhora puede registrar un nuevo usuario.",
            parent=registro
        )

        entry_usuario.focus()

    # =================================================
    # BOTÓN VERIFICAR ADMINISTRADOR
    # =================================================

    btn_verificar = tk.Button(
        registro,
        text="VERIFICAR ADMINISTRADOR",
        bg="#3498db",
        fg="white",
        activebackground="#2980b9",
        activeforeground="white",
        font=("Arial", 11, "bold"),
        width=25,
        command=habilitar_registro
    )

    btn_verificar.pack(pady=(5, 0))

    # =================================================
    # FORMULARIO NUEVO USUARIO
    # =================================================
    # Comienza oculto. Solo aparece cuando el
    # administrador fue correctamente validado.
    # =================================================

    frame_nuevo_usuario = tk.Frame(
        registro,
        bg="#ecf0f1"
    )

    tk.Label(
        frame_nuevo_usuario,
        text="NUEVO USUARIO",
        bg="#ecf0f1",
        fg="#2c3e50",
        font=("Arial", 12, "bold")
    ).pack(pady=(0, 10))

    tk.Label(
        frame_nuevo_usuario,
        text="Usuario",
        bg="#ecf0f1",
        fg="#2c3e50",
        font=("Arial", 11, "bold")
    ).pack(anchor="w")

    entry_usuario = tk.Entry(
        frame_nuevo_usuario,
        font=("Arial", 12)
    )
    entry_usuario.pack(fill="x", pady=(5, 10))

    tk.Label(
        frame_nuevo_usuario,
        text="Contraseña",
        bg="#ecf0f1",
        fg="#2c3e50",
        font=("Arial", 11, "bold")
    ).pack(anchor="w")

    entry_password = tk.Entry(
        frame_nuevo_usuario,
        show="*",
        font=("Arial", 12)
    )
    entry_password.pack(fill="x", pady=(5, 0))

    # =================================================
    # REGISTRAR NUEVO USUARIO
    # =================================================

    def registrar():

        usuario = entry_usuario.get().strip()
        password = entry_password.get()

        if not usuario or not password:

            messagebox.showwarning(
                "Advertencia",
                "Complete todos los campos del nuevo usuario.",
                parent=registro
            )

            return

        if registrar_usuario(usuario, password):

            messagebox.showinfo(
                "Éxito",
                "Usuario registrado correctamente.",
                parent=registro
            )

            registro.destroy()

        else:

            messagebox.showerror(
                "Error",
                "El nombre de usuario ya existe.",
                parent=registro
            )

            entry_usuario.focus()

    # =================================================
    # BOTÓN REGISTRAR
    # =================================================

    btn_registrar = tk.Button(
        registro,
        text="REGISTRAR USUARIO",
        bg="#27ae60",
        fg="white",
        activebackground="#219150",
        activeforeground="white",
        font=("Arial", 11, "bold"),
        width=25,
        command=registrar
    )

    # =================================================
    # SALIR
    # =================================================

    def salir():

        if messagebox.askyesno(
            "Salir",
            "¿Desea salir de registración?",
            parent=registro
        ):
            registro.destroy()

    tk.Button(
        registro,
        text="SALIR",
        bg="#7f8c8d",
        fg="white",
        activebackground="#616a6b",
        activeforeground="white",
        font=("Arial", 11, "bold"),
        width=25,
        command=salir
    ).pack(pady=(15, 10))

    # =================================================
    # ENTER PARA VALIDAR ADMINISTRADOR
    # =================================================

    entry_password_admin.bind(
        "<Return>",
        lambda event: habilitar_registro()
    )

    # =================================================
    # CENTRAR VENTANA
    # =================================================

    centrar_ventana(registro, ancho=450, alto=550)

