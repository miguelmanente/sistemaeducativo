# ========================================================================================
#                  MÓDULO PARA CARGAR DATOS PERSONALES DE LOS DOCENTES
# ========================================================================================

# --------------------- Área de declaración de librerías --------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import re
import time

from database import conectar
from centraVent import centrar_ventana
from estilos import configurar_estilos
from Backup import crear_backup
from validaciones import dni_existente, validar_cuil, validar_nombre
from utilidades import (
    formatear_cuil,
    normalizar_nombre,
    normalizar_telefono,
    formatear_telefono,
    normalizar_cuil,
    formatear_dni,
    formatear_fecha,
    generar_cuil,
    normalizar_fecha
)
from exportarPDF import exportar_ficha_docente


# ----------- Función que maneja toda la ventana datos personales del profesor ------------
def info_profesor():

    ventana = tk.Toplevel()
    configurar_estilos()

    ventana.title("Datos personales del profesor")
    ventana.geometry("1100x600")

    # Configuración del grid de la ventana principal
    ventana.rowconfigure(0, weight=1)
    ventana.rowconfigure(1, weight=2)
    ventana.columnconfigure(0, weight=1)

    # =========================
    # FRAME SUPERIOR (ENTRYS)
    # =========================
    frame_superior = ttk.LabelFrame(
        ventana,
        text="Datos del Profesor",
        padding=10
    )

    frame_superior.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=10,
        pady=10
    )

    frame_superior.columnconfigure(1, weight=1)
    frame_superior.columnconfigure(3, weight=1)

    # =========================
    # VARIABLES
    # =========================
    apellido = tk.StringVar()
    nombre = tk.StringVar()
    dni = tk.StringVar()
    cuil = tk.StringVar()
    telefono = tk.StringVar()
    email = tk.StringVar()
    direccion = tk.StringVar()
    fecha_nacimiento = tk.StringVar()

    # =========================
    # LABELS Y ENTRYS
    # =========================

    ttk.Label(
        frame_superior,
        text="Apellidos:"
    ).grid(row=0, column=0, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=apellido,
        font=("Arial", 12)
    ).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

    ttk.Label(
        frame_superior,
        text="Nombres:"
    ).grid(row=0, column=2, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=nombre,
        font=("Arial", 12)
    ).grid(row=0, column=3, sticky="ew", padx=5, pady=5)

    # =========================
    # ESTILOS DE VALIDACIÓN
    # =========================

    style = ttk.Style()

    style.configure(
        "Valido.TEntry",
        foreground="black"
    )

    style.configure(
        "Error.TEntry",
        foreground="black"
    )

    style.map(
        "Error.TEntry",
        fieldbackground=[
            ("!disabled", "#ffcccc")
        ]
    )

    # =========================
    # DNI
    # =========================

    ttk.Label(
        frame_superior,
        text="DNI:"
    ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

    def solo_numeros(P):
        return P.isdigit() or P == ""

    vcmd = (
        ventana.register(solo_numeros),
        "%P"
    )

    entry_dni = ttk.Entry(
        frame_superior,
        textvariable=dni,
        validate="key",
        validatecommand=vcmd,
        style="Valido.TEntry",
        font=("Arial", 12)
    )

    entry_dni.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=5,
        pady=5
    )

    # =========================
    # CUIL
    # =========================

    ttk.Label(
        frame_superior,
        text="CUIL:"
    ).grid(row=1, column=2, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=cuil,
        font=("Arial", 12)
    ).grid(row=1, column=3, sticky="ew", padx=5, pady=5)

    # =========================
    # TELÉFONO
    # =========================

    ttk.Label(
        frame_superior,
        text="Teléfono:"
    ).grid(row=2, column=0, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=telefono,
        font=("Arial", 12)
    ).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

    # =========================
    # EMAIL
    # =========================

    ttk.Label(
        frame_superior,
        text="Email:"
    ).grid(row=2, column=2, sticky="e", padx=5, pady=5)

    entry_email = ttk.Entry(
        frame_superior,
        textvariable=email,
        style="Valido.TEntry",
        font=("Arial", 12)
    )

    entry_email.grid(
        row=2,
        column=3,
        sticky="ew",
        padx=5,
        pady=5
    )

    # =========================
    # DIRECCIÓN
    # =========================

    ttk.Label(
        frame_superior,
        text="Dirección:"
    ).grid(row=3, column=0, sticky="e", padx=5, pady=5)

    ttk.Entry(
        frame_superior,
        textvariable=direccion,
        font=("Arial", 12)
    ).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

    # =========================
    # FECHA DE NACIMIENTO
    # =========================

    ttk.Label(
        frame_superior,
        text="Fecha de Nacimiento:"
    ).grid(row=3, column=2, sticky="e", padx=5, pady=5)

    entry_fecha = ttk.Entry(
        frame_superior,
        textvariable=fecha_nacimiento,
        font=("Arial", 12)
    )

    entry_fecha.grid(
        row=3,
        column=3,
        sticky="ew",
        padx=5,
        pady=5
    )

    # =========================
    # FRAME BOTONES
    # =========================

    frame_botones = ttk.Frame(frame_superior)

    frame_botones.grid(
        row=4,
        column=0,
        columnspan=4,
        pady=10
    )

    # =========================
    # FRAME INFERIOR
    # =========================

    frame_inferior = ttk.LabelFrame(
        ventana,
        text="Listado de Profesores",
        padding=10
    )

    frame_inferior.grid(
        row=1,
        column=0,
        sticky="nsew",
        padx=10,
        pady=(0, 10)
    )

    frame_inferior.rowconfigure(0, weight=1)
    frame_inferior.columnconfigure(0, weight=1)

    # =========================
    # TREEVIEW
    # =========================

    columnas = (
        "id_docente",
        "apellido",
        "nombre",
        "dni",
        "cuil",
        "telefono",
        "email",
        "direccion",
        "fecha_nacimiento"
    )

    tree = ttk.Treeview(
        frame_inferior,
        columns=columnas,
        show="headings"
    )

    tree.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    # =========================
    # ENCABEZADOS
    # =========================

    tree.heading("id_docente", text="ID")
    tree.heading("apellido", text="APELLIDO")
    tree.heading("nombre", text="NOMBRES")
    tree.heading("dni", text="DNI")
    tree.heading("cuil", text="CUIL")
    tree.heading("telefono", text="TELÉFONO")
    tree.heading("email", text="EMAIL")
    tree.heading("direccion", text="DIRECCIÓN")
    tree.heading("fecha_nacimiento", text="FECHA NACIMIENTO")

    # =========================
    # COLUMNAS
    # =========================

    tree.column(
        "id_docente",
        width=0,
        stretch=False
    )

    tree.column(
        "apellido",
        width=150,
        anchor="w"
    )

    tree.column(
        "nombre",
        width=150,
        anchor="w"
    )

    tree.column(
        "dni",
        width=80,
        anchor="center"
    )

    tree.column(
        "cuil",
        width=110,
        anchor="center"
    )

    tree.column(
        "telefono",
        width=110,
        anchor="center"
    )

    tree.column(
        "email",
        width=180,
        anchor="w"
    )

    tree.column(
        "direccion",
        width=180,
        anchor="w"
    )

    tree.column(
        "fecha_nacimiento",
        width=120,
        anchor="center"
    )

    # =========================
    # SCROLLBARS
    # =========================

    scrollbar_y = ttk.Scrollbar(
        frame_inferior,
        orient="vertical",
        command=tree.yview
    )

    scrollbar_x = ttk.Scrollbar(
        frame_inferior,
        orient="horizontal",
        command=tree.xview
    )

    tree.configure(
        yscrollcommand=scrollbar_y.set,
        xscrollcommand=scrollbar_x.set
    )

    scrollbar_y.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    scrollbar_x.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    # ================================================================================
    # FUNCIONES DE VALIDACIÓN
    # ================================================================================

    def marcar_error(entry):
        entry.config(style="Error.TEntry")

    def marcar_valido(entry):
        entry.config(style="Valido.TEntry")

    # =========================
    # VALIDACIÓN DNI
    # =========================

    def validar_dni(dni):
        return dni.isdigit() and len(dni) == 8

    def validar_dni_evento(event):
        valor = dni.get()

        if len(valor) == 8 and valor.isdigit():
            marcar_valido(entry_dni)
        else:
            marcar_error(entry_dni)

        entry_dni.bind(
            "<KeyRelease>",
            validar_dni_evento
        )

    # =========================
    # VALIDACIÓN EMAIL
    # =========================

    def validar_email(valor):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(patron, valor) is not None

    def validar_email_evento(event):
        valor = email.get()

        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'

        if re.match(patron, valor) or valor == "":
            marcar_valido(entry_email)
        else:
            marcar_error(entry_email)

    entry_email.bind(
        "<KeyRelease>",
        validar_email_evento
    )

    # ================================================================================
    # SELECCIÓN DE REGISTRO
    # ================================================================================

    id_seleccionado = None

    def seleccionar_registro(event=None):
        nonlocal id_seleccionado

        item = tree.selection()

        if not item:
            return

        valores = tree.item(item[0], "values")

        id_seleccionado = valores[0]

        apellido.set(valores[1])
        nombre.set(valores[2])
        dni.set(valores[3])
        cuil.set(valores[4])
        telefono.set(valores[5])
        email.set(valores[6])
        direccion.set(valores[7])
        fecha_nacimiento.set(valores[8])

    tree.bind("<<TreeviewSelect>>", seleccionar_registro )
    # -------------------------------------------------------------------------------

    # ================================================================================
    # CARGA DE DATOS
    # ================================================================================

    def cargar_datos_treeview():

        for item in tree.get_children():
            tree.delete(item)

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id_docente,
                apellido,
                nombre,
                dni,
                cuil,
                telefono,
                email,
                direccion,
                fecha_nacimiento
            FROM profesores
            ORDER BY apellido COLLATE NOCASE,
                     nombre COLLATE NOCASE
        """)

        registros = cursor.fetchall()

        conn.close()

        for fila in registros:

            fila = list(fila)

            fila[4] = formatear_cuil(fila[4])
            fila[5] = formatear_telefono(fila[5])
            fila[8] = formatear_fecha(fila[8])

            tree.insert(
                "",
                "end",
                values=fila
            )

    # ================================================================================
    # AGREGAR REGISTRO
    # ================================================================================

    def agregar_datos():

        if not apellido.get() or not dni.get() or not nombre.get():

            messagebox.showwarning(
                "Campos obligatorios",
                "Apellido y Nombres y DNI son obligatorios.",
                parent=ventana
            )

            return

        if not validar_dni(dni.get()):

            messagebox.showerror(
                "Error",
                "DNI inválido (solo números, 7 u 8 dígitos)",
                parent=ventana
            )

            return

        dni_texto = dni.get().strip()

        if dni_existente(dni_texto):

            messagebox.showwarning(
                "Error",
                "El DNI ya está registrado",
                parent=ventana
            )

            return

        if email.get() and not validar_email(email.get()):

            messagebox.showerror(
                "Error",
                "Email inválido",
                parent=ventana
            )

            return

        cuil_normalizado = normalizar_cuil(
            cuil.get().strip()
        )

        if cuil_normalizado is None:

            messagebox.showerror(
                "Error",
                "El CUIL debe tener 11 dígitos.",
                parent=ventana
            )

            return

        if not validar_cuil(cuil_normalizado):

            messagebox.showerror(
                "Error",
                "El CUIL ingresado no es válido.",
                parent=ventana
            )

            return

        telefono_normalizado = normalizar_telefono(
            telefono.get()
        )

        if telefono_normalizado is None:

            messagebox.showerror(
                "Error",
                "El teléfono ingresado no es válido.",
                parent=ventana
            )

            return

        fecha_normalizada = normalizar_fecha(
            fecha_nacimiento.get()
        )

        if fecha_normalizada is None:

            messagebox.showerror(
                "Error",
                "La fecha debe tener el formato DD/MM/AAAA.",
                parent=ventana
            )

            return

        apellido_normalizado = normalizar_nombre(
            apellido.get()
        )

        nombre_normalizado = normalizar_nombre(
            nombre.get()
        )

        if not validar_nombre(apellido_normalizado):

            messagebox.showerror(
                "Error",
                "Apellido inválido.",
                parent=ventana
            )

            return

        if not validar_nombre(nombre_normalizado):

            messagebox.showerror(
                "Error",
                "Nombre inválido.",
                parent=ventana
            )

            return

        try:

            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO profesores
                (
                    apellido,
                    nombre,
                    dni,
                    cuil,
                    telefono,
                    email,
                    direccion,
                    fecha_nacimiento
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                apellido_normalizado,
                nombre_normalizado,
                dni.get(),
                cuil_normalizado,
                telefono_normalizado,
                email.get(),
                direccion.get(),
                fecha_normalizada
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Éxito",
                "Datos guardados correctamente.",
                parent=ventana
            )

            cargar_datos_treeview()

        except Exception as e:

            messagebox.showerror(
                "Error",
                f"No se pudieron guardar los datos:\n{e}",
                parent=ventana
            )

    # ================================================================================
    # MODIFICAR REGISTRO
    # ================================================================================

    def modificar_registro():

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro",
                parent=ventana
            )

            return

        conn = conectar()
        cursor = conn.cursor()

        if not validar_dni(dni.get()):

            conn.close()

            messagebox.showerror(
                "Error",
                "DNI inválido (solo números, 7 u 8 dígitos)",
                parent=ventana
            )

            return

        dni_texto = dni.get().strip()

        if dni_existente(
            dni_texto,
            id_seleccionado
        ):

            conn.close()

            messagebox.showwarning(
                "Error",
                "El DNI ya está registrado",
                parent=ventana
            )

            return

        if email.get() and not validar_email(email.get()):

            conn.close()

            messagebox.showerror(
                "Error",
                "Email inválido",
                parent=ventana
            )

            return

        cuil_normalizado = normalizar_cuil(
            cuil.get().strip()
        )

        if cuil_normalizado is None:

            conn.close()

            messagebox.showerror(
                "Error",
                "El CUIL debe tener 11 dígitos.",
                parent=ventana
            )

            return

        if not validar_cuil(cuil_normalizado):

            conn.close()

            messagebox.showerror(
                "Error",
                "El CUIL ingresado no es válido.",
                parent=ventana
            )

            return

        telefono_normalizado = normalizar_telefono(
            telefono.get()
        )

        if telefono_normalizado is None:

            conn.close()

            messagebox.showerror(
                "Error",
                "El teléfono ingresado no es válido.",
                parent=ventana
            )

            return

        fecha_normalizada = normalizar_fecha(
            fecha_nacimiento.get()
        )

        if fecha_normalizada is None:

            conn.close()

            messagebox.showerror(
                "Error",
                "La fecha debe tener el formato DD/MM/AAAA.",
                parent=ventana
            )

            return

        apellido_normalizado = normalizar_nombre(
            apellido.get()
        )

        nombre_normalizado = normalizar_nombre(
            nombre.get()
        )

        if not validar_nombre(apellido_normalizado):

            conn.close()

            messagebox.showerror(
                "Error",
                "Apellido inválido.",
                parent=ventana
            )

            return

        if not validar_nombre(nombre_normalizado):

            conn.close()

            messagebox.showerror(
                "Error",
                "Nombre inválido.",
                parent=ventana
            )

            return

        cursor.execute("""
            UPDATE profesores
            SET
                apellido = ?,
                nombre = ?,
                dni = ?,
                cuil = ?,
                telefono = ?,
                email = ?,
                direccion = ?,
                fecha_nacimiento = ?
            WHERE id_docente = ?
        """, (
            apellido_normalizado,
            nombre_normalizado,
            dni.get(),
            cuil_normalizado,
            telefono_normalizado,
            email.get(),
            direccion.get(),
            fecha_normalizada,
            id_seleccionado
        ))

        conn.commit()
        conn.close()

        cargar_datos_treeview()
        limpiar_campos()

        messagebox.showinfo(
            "Éxito",
            "Registro actualizado",
            parent=ventana
        )

    # ================================================================================
    # GENERAR CUIL
    # ================================================================================

    def generar_cuil_desde_boton():

        dni_texto = dni.get().strip()

        if not validar_dni(dni_texto):

            messagebox.showerror(
                "Error",
                "Primero ingrese un DNI válido.",
                parent=ventana
            )

            return

        respuesta = messagebox.askyesno(
            "Generar CUIL",
            "¿El docente es masculino?\n\n"
            "Sí = Prefijo 20\n"
            "No = Prefijo 27",
            parent=ventana
        )

        prefijo = "20" if respuesta else "27"

        cuil_generado = generar_cuil(
            dni_texto,
            prefijo
        )

        cuil.set(cuil_generado)

    # ================================================================================
    # ELIMINAR REGISTRO
    # ================================================================================

    def eliminar_registro():

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro",
                parent=ventana
            )

            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Eliminar registro?",
            parent=ventana
        )

        if not confirmar:
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM profesores WHERE id_docente = ?",
            (id_seleccionado,)
        )

        conn.commit()
        conn.close()

        cargar_datos_treeview()
        limpiar_campos()

    # ================================================================================
    # BÚSQUEDA RÁPIDA EN TREEVIEW
    #
    # Una letra:
    #       M → primer apellido con M
    #
    # Misma letra nuevamente:
    #       M → siguiente apellido con M
    #
    # Varias letras:
    #       MA → busca apellidos que comiencen con MA
    # ================================================================================

    texto_busqueda = ""
    ultima_tecla = ""
    ultimo_tiempo_busqueda = 0

    def buscar_treeview(event):

        nonlocal texto_busqueda
        nonlocal ultima_tecla
        nonlocal ultimo_tiempo_busqueda

        # Solo procesar letras
        if not event.char or not event.char.isalpha():
            return

        letra = event.char.lower()
        ahora = time.time()

        # ------------------------------------------------------------
        # MISMA LETRA:
        # si se pulsa nuevamente la misma letra rápidamente,
        # se mantiene la búsqueda por esa letra y se avanza
        # al siguiente registro.
        # ------------------------------------------------------------
        if (
            letra == ultima_tecla
            and ahora - ultimo_tiempo_busqueda <= 1
        ):

            texto_busqueda = letra

        # ------------------------------------------------------------
        # NUEVA LETRA:
        # si se escribe otra letra rápidamente, permite búsqueda
        # por varias letras. Ejemplo: MA
        # ------------------------------------------------------------
        elif ahora - ultimo_tiempo_busqueda <= 1:

            texto_busqueda += letra

        else:

            texto_busqueda = letra

        ultima_tecla = letra
        ultimo_tiempo_busqueda = ahora

        items = tree.get_children()

        if not items:
            return

        # ------------------------------------------------------------
        # Determinar desde dónde comenzar.
        # ------------------------------------------------------------

        seleccion = tree.selection()

        start_index = 0

        if seleccion:

            try:

                start_index = (
                    items.index(seleccion[0]) + 1
                )

            except ValueError:

                start_index = 0

        # ------------------------------------------------------------
        # Buscar recorriendo toda la lista.
        # Se hace de manera circular.
        # ------------------------------------------------------------

        for i in range(len(items)):

            idx = (
                start_index + i
            ) % len(items)

            item = items[idx]

            valores = tree.item(
                item,
                "values"
            )

            if not valores:
                continue

            apellido_tree = str(
                valores[1]
            ).strip().lower()

            if apellido_tree.startswith(
                texto_busqueda
            ):

                tree.selection_set(item)
                tree.focus(item)
                tree.see(item)

                # Asegurar que el Treeview mantenga el foco
                tree.focus_set()

                break

    tree.bind(
        "<Key>",
        buscar_treeview
    )
    # -------------------------------------------------------------------------------

    # ================================================================================
    # MOSTRAR FICHA DEL PROFESOR
    # ================================================================================

    def mostrar_ficha():

        if not id_seleccionado:

            messagebox.showwarning(
                "Atención",
                "Seleccione un registro para ver la ficha",
                parent=ventana
            )

            return

        ficha = tk.Toplevel(ventana)
        ficha.title("Ficha del Profesor")
        ficha.state("zoomed")
        ficha.resizable(False, False)
        ficha.configure(bg="#f4f4f4")

        # =========================
        # ENCABEZADO
        # =========================

        frame_header = tk.Frame(ficha, bg="#2c3e50", height=70)
        frame_header.pack(fill="x")
        frame_header.pack_propagate(False)

        tk.Label(
            frame_header,
            text=f"{apellido.get()}, {nombre.get()}",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=15)

        # =========================
        # CUERPO - GRID DE DATOS
        # =========================

        frame_ficha = tk.Frame(ficha, bg="#f4f4f4", padx=20, pady=20)
        frame_ficha.pack(fill="both", expand=True)

        frame_ficha.columnconfigure(1, weight=1)
        frame_ficha.columnconfigure(3, weight=1)

        def campo(fila, col_label, col_valor, etiqueta, valor):

            tk.Label(
                frame_ficha,
                text=etiqueta,
                font=("Arial", 12, "bold"),
                bg="#f4f4f4",
                fg="#555555",
                anchor="w"
            ).grid(row=fila, column=col_label, sticky="w", padx=(0, 5), pady=10)

            tk.Label(
                frame_ficha,
                text=valor if valor else "-",
                font=("Arial", 12),
                bg="#f4f4f4",
                fg="#1a1a1a",
                anchor="w",
                wraplength=180,
                justify="left"
            ).grid(row=fila, column=col_valor, sticky="w", padx=(0, 20), pady=10)

        # Fila 0: DNI - CUIL
        campo(0, 0, 1, "DNI:", dni.get())
        campo(0, 2, 3, "CUIL:", cuil.get())

        # Fila 1: Teléfono - Email
        campo(1, 0, 1, "Teléfono:", telefono.get())
        campo(1, 2, 3, "Email:", email.get())

        # Fila 2: Dirección - Fecha Nacimiento
        campo(2, 0, 1, "Dirección:", direccion.get())
        campo(2, 2, 3, "Fecha Nac.:", fecha_nacimiento.get())

        # =========================
        # SEPARADOR
        # =========================

        ttk.Separator(ficha, orient="horizontal").pack(fill="x", padx=20)

        def exportar_pdf():
            exportar_ficha_docente(
            apellido=apellido.get(),
            nombre=nombre.get(),
            dni=dni.get(),
            cuil=cuil.get(),
            telefono=telefono.get(),
            email=email.get(),
            direccion=direccion.get(),
            fecha_nacimiento=fecha_nacimiento.get(),
            parent=ficha
        )

        # =========================
        # BOTONES
        # =========================

        frame_botones = tk.Frame(
            ficha,
            bg="#f4f4f4"
        )

        frame_botones.pack(pady=15)

        tk.Button(
            frame_botones,
            text="📄 Exportar a PDF",
            font=("Segoe UI Emoji", 11, "bold"),
            bg="#2c3e50",
            fg="white",
            activebackground="#34495e",
            activeforeground="white",
            padx=15,
            pady=6,
            cursor="hand2",
            command=exportar_pdf
        ).pack(
            side="left",
            padx=8
        )

        tk.Button(
            frame_botones,
            text="❌ Cerrar",
            font=("Segoe UI Emoji", 11, "bold"),
            padx=15,
            pady=6,
            cursor="hand2",
            command=ficha.destroy
        ).pack(
            side="left",
            padx=8
        )

        
        centrar_ventana(ficha)
    # --------------------------------------------------------------------------------

    # ================================================================================
    # LIMPIAR CAMPOS
    # ================================================================================

    def limpiar_campos():

        nonlocal id_seleccionado

        id_seleccionado = None

        apellido.set("")
        nombre.set("")
        dni.set("")
        cuil.set("")
        telefono.set("")
        email.set("")
        direccion.set("")
        fecha_nacimiento.set("")

        # También quitamos cualquier selección del Treeview
        tree.selection_remove(
            tree.selection()
        )

    # ================================================================================
    # INICIALIZACIÓN
    # ================================================================================

    crear_backup()

    centrar_ventana(
        ventana
    )

    cargar_datos_treeview()

    # Dejamos preparado el Treeview para la búsqueda por teclado
    tree.focus_set()

    # ================================================================================
    # BOTONES
    # ================================================================================

    tk.Button(
        frame_botones,
        text="💾 Agregar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=agregar_datos
    ).grid(
        row=0,
        column=0,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="✏ Modificar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=modificar_registro
    ).grid(
        row=0,
        column=1,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="🗑 Eliminar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=eliminar_registro
    ).grid(
        row=0,
        column=2,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="🧹 Limpiar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=limpiar_campos
    ).grid(
        row=0,
        column=3,
        padx=5
    )

    
    tk.Button(
        frame_botones,
        text="🪪 Ver Ficha",
        font=("Segoe UI Emoji", 12, "bold"),
        command=mostrar_ficha
    ).grid(
        row=0,
        column=4,
        padx=5
    )

    tk.Button(
        frame_botones,
        text="❌ Cerrar",
        font=("Segoe UI Emoji", 12, "bold"),
        command=ventana.destroy
    ).grid(
        row=0,
        column=5,
        padx=5
    )

    tk.Button(
        frame_superior,
        text="🔄 Generar CUIL",
        font=("Segoe UI Emoji", 12, "bold"),
        command=generar_cuil_desde_boton
    ).grid(
        row=1,
        column=4,
        padx=5
    )
