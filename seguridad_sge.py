# ============================================================
# seguridad_sge.py
# Sistema de Gestión Educativa (SGE)
#
# Ventana de Seguridad y Copias del SGE
#
# Responsabilidad:
#   - Mostrar el estado de protección.
#   - Mostrar el último backup cifrado.
#   - Crear backups cifrados.
#   - Restaurar un backup cifrado.
#   - Realizar recuperación de emergencia.
#
# IMPORTANTE:
#   - La administración de la clave pertenece a seguridad.py.
#   - La creación de backups pertenece a Backup.py.
#   - La restauración pertenece a restauracion_nueva.py.
#   - La recuperación de emergencia utiliza recuperacion.py.
#
# ============================================================

import os
import sys
import tkinter as tk

from tkinter import (
    messagebox,
    filedialog,
    simpledialog
)

from datetime import datetime

from seguridad import verificar_clave_datos

from Backup import crear_backup

from restauracion_nueva import (
    descifrar_backup,
    verificar_base_sqlite
)

from recuperacion import (
    recuperar_clave_datos
)


# ============================================================
# RUTAS
# ============================================================

if getattr(sys, "frozen", False):

    BASE_DIR = os.path.dirname(
        sys.executable
    )

else:

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


CARPETA_BACKUPS = os.path.join(
    BASE_DIR,
    "backups"
)


RUTA_BASE_DATOS = os.path.join(
    BASE_DIR,
    "bdescuela.db"
)


# ============================================================
# OBTENER ÚLTIMO BACKUP
# ============================================================

def obtener_ultimo_backup():

    if not os.path.isdir(
        CARPETA_BACKUPS
    ):

        return None

    archivos = []

    for archivo in os.listdir(
        CARPETA_BACKUPS
    ):

        if archivo.lower().endswith(".enc"):

            ruta = os.path.join(
                CARPETA_BACKUPS,
                archivo
            )

            if os.path.isfile(ruta):

                archivos.append(ruta)

    if not archivos:

        return None

    archivos.sort(
        key=os.path.getmtime,
        reverse=True
    )

    return archivos[0]


# ============================================================
# CENTRAR VENTANA
# ============================================================

def centrar_ventana(ventana):

    ventana.update_idletasks()

    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()

    pantalla_ancho = (
        ventana.winfo_screenwidth()
    )

    pantalla_alto = (
        ventana.winfo_screenheight()
    )

    x = (
        pantalla_ancho // 2
        - ancho // 2
    )

    y = (
        pantalla_alto // 2
        - alto // 2
    )

    ventana.geometry(
        f"{ancho}x{alto}+{x}+{y}"
    )


# ============================================================
# VENTANA DE SEGURIDAD
# ============================================================

def ventana_seguridad(root=None):

    if root is not None:

        ventana = tk.Toplevel(root)

        ventana.transient(root)

    else:

        ventana = tk.Tk()

    ventana.title(
        "Seguridad y Copias del SGE"
    )

    ventana.geometry(
        "650x760"
    )

    ventana.resizable(
        False,
        False
    )


    # ========================================================
    # TÍTULO
    # ========================================================

    frame_titulo = tk.Frame(
        ventana,
        bg="#2c3e50",
        height=75
    )

    frame_titulo.pack(
        fill="x"
    )


    tk.Label(
        frame_titulo,
        text="SEGURIDAD Y COPIAS DEL SGE",
        bg="#2c3e50",
        fg="white",
        font=("Arial", 18, "bold")
    ).pack(
        pady=22
    )


    # ========================================================
    # PROTECCIÓN DE DATOS
    # ========================================================

    frame_proteccion = tk.LabelFrame(
        ventana,
        text=" Protección de datos ",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=15
    )

    frame_proteccion.pack(
        fill="x",
        padx=30,
        pady=(20, 10)
    )


    lbl_proteccion = tk.Label(
        frame_proteccion,
        text="Verificando...",
        font=("Arial", 13, "bold")
    )

    lbl_proteccion.pack()


    # ========================================================
    # ÚLTIMO BACKUP
    # ========================================================

    frame_backup = tk.LabelFrame(
        ventana,
        text=" Último backup cifrado ",
        font=("Arial", 11, "bold"),
        padx=20,
        pady=15
    )

    frame_backup.pack(
        fill="x",
        padx=30,
        pady=10
    )


    lbl_backup = tk.Label(
        frame_backup,
        text="Consultando...",
        font=("Arial", 11),
        justify="left",
        anchor="w"
    )

    lbl_backup.pack(
        fill="x"
    )


    # ========================================================
    # ACTUALIZAR PROTECCIÓN
    # ========================================================

    def actualizar_proteccion():

        try:

            protegido = (
                verificar_clave_datos()
            )

            if protegido:

                lbl_proteccion.config(
                    text="🛡️ Protección de datos: OK",
                    fg="green"
                )

            else:

                lbl_proteccion.config(
                    text="⚠️ Protección de datos: ERROR",
                    fg="red"
                )

        except Exception as error:

            lbl_proteccion.config(
                text="⚠️ Error al verificar protección",
                fg="red"
            )

            print(
                "Error al verificar protección:",
                error
            )


    # ========================================================
    # ACTUALIZAR INFORMACIÓN DEL BACKUP
    # ========================================================

    def actualizar_backup():

        try:

            ruta_backup = (
                obtener_ultimo_backup()
            )

            if ruta_backup is None:

                lbl_backup.config(
                    text="No existe ningún backup cifrado."
                )

                return


            nombre = os.path.basename(
                ruta_backup
            )


            tamaño = os.path.getsize(
                ruta_backup
            )


            fecha_archivo = (
                os.path.getmtime(
                    ruta_backup
                )
            )


            fecha = datetime.fromtimestamp(
                fecha_archivo
            ).strftime(
                "%d/%m/%Y %H:%M:%S"
            )


            lbl_backup.config(
                text=(
                    f"Archivo: {nombre}\n\n"
                    f"Fecha: {fecha}\n\n"
                    f"Tamaño: {tamaño:,} bytes\n\n"
                    "Estado: ✅ Backup cifrado disponible"
                )
            )


        except Exception as error:

            lbl_backup.config(
                text=(
                    "No fue posible "
                    "consultar el backup."
                )
            )

            print(
                "Error al consultar backup:",
                error
            )


    # ========================================================
    # CREAR BACKUP
    # ========================================================

    def ejecutar_backup():

        respuesta = messagebox.askyesno(
            "Crear backup",
            "¿Desea crear ahora un backup cifrado "
            "de la base de datos del SGE?",
            parent=ventana
        )


        if not respuesta:

            return


        try:

            ruta_backup = crear_backup()


            actualizar_backup()


            messagebox.showinfo(
                "Backup creado",
                "El backup cifrado se creó correctamente.\n\n"
                f"Archivo:\n{ruta_backup}",
                parent=ventana
            )


        except Exception as error:

            messagebox.showerror(
                "Error de backup",
                "No fue posible crear el backup.\n\n"
                f"{error}",
                parent=ventana
            )


    # ========================================================
    # RESTAURAR BACKUP NORMAL
    # ========================================================

    def ejecutar_restauracion():

        if not os.path.isfile(
            RUTA_BASE_DATOS
        ):

            messagebox.showerror(
                "Error",
                "No se encontró la base de datos "
                "actual del SGE.",
                parent=ventana
            )

            return


        # ----------------------------------------------------
        # Seleccionar backup
        # ----------------------------------------------------

        ruta_backup = (
            filedialog.askopenfilename(
                parent=ventana,
                title="Seleccionar backup del SGE",
                initialdir=CARPETA_BACKUPS,
                filetypes=[
                    (
                        "Backups cifrados",
                        "*.enc"
                    ),
                    (
                        "Todos los archivos",
                        "*.*"
                    )
                ]
            )
        )


        if not ruta_backup:

            return


        nombre_backup = os.path.basename(
            ruta_backup
        )


        # ----------------------------------------------------
        # Confirmación
        # ----------------------------------------------------

        respuesta = messagebox.askyesno(
            "Confirmar restauración",
            "ATENCIÓN\n\n"
            "Se restaurará el siguiente backup:\n\n"
            f"{nombre_backup}\n\n"
            "Antes de reemplazar la base actual, "
            "el SGE creará un backup de seguridad.\n\n"
            "¿Desea continuar?",
            parent=ventana
        )


        if not respuesta:

            return


        ruta_temporal = (
            RUTA_BASE_DATOS
            + ".restauracion_tmp"
        )


        try:

            # ------------------------------------------------
            # 1. Backup de seguridad
            # ------------------------------------------------

            ruta_backup_seguridad = (
                crear_backup()
            )


            # ------------------------------------------------
            # 2. Eliminar temporal anterior
            # ------------------------------------------------

            if os.path.exists(
                ruta_temporal
            ):

                os.remove(
                    ruta_temporal
                )


            # ------------------------------------------------
            # 3. Descifrar
            # ------------------------------------------------

            descifrar_backup(
                ruta_backup,
                ruta_temporal
            )


            # ------------------------------------------------
            # 4. Verificar SQLite
            # ------------------------------------------------

            verificar_base_sqlite(
                ruta_temporal
            )


            # ------------------------------------------------
            # 5. Reemplazar base
            # ------------------------------------------------

            os.replace(
                ruta_temporal,
                RUTA_BASE_DATOS
            )


            actualizar_backup()


            messagebox.showinfo(
                "Restauración completada",
                "La base de datos del SGE "
                "fue restaurada correctamente.\n\n"
                "Se verificó la integridad de SQLite "
                "antes de reemplazar la base actual.\n\n"
                "También se creó un backup de seguridad "
                "antes de la restauración.\n\n"
                f"Backup de seguridad:\n"
                f"{os.path.basename(ruta_backup_seguridad)}",
                parent=ventana
            )


        except Exception as error:

            if os.path.exists(
                ruta_temporal
            ):

                try:

                    os.remove(
                        ruta_temporal
                    )

                except OSError:

                    pass


            messagebox.showerror(
                "Error de restauración",
                "No fue posible restaurar "
                "el backup seleccionado.\n\n"
                "La base de datos actual "
                "no fue reemplazada.\n\n"
                f"Detalle:\n{error}",
                parent=ventana
            )


    # ========================================================
    # RECUPERACIÓN DE EMERGENCIA
    # ========================================================

    def ejecutar_recuperacion_emergencia():

        # ----------------------------------------------------
        # Advertencia inicial
        # ----------------------------------------------------

        respuesta = messagebox.askyesno(
            "Recuperación de emergencia",
            "Esta función está destinada a situaciones "
            "en las que Windows no puede recuperar "
            "la clave de datos del SGE.\n\n"
            "Necesitará:\n\n"
            "• El archivo de recuperación "
            "recuperacion_sge.json\n"
            "• La frase de recuperación\n"
            "• Un backup cifrado (.enc)\n\n"
            "¿Desea continuar?",
            parent=ventana
        )


        if not respuesta:

            return


        # ----------------------------------------------------
        # Seleccionar archivo de recuperación
        # ----------------------------------------------------

        ruta_recuperacion = (
            filedialog.askopenfilename(
                parent=ventana,
                title=(
                    "Seleccionar archivo "
                    "de recuperación"
                ),
                filetypes=[
                    (
                        "Archivo de recuperación",
                        "*.json"
                    ),
                    (
                        "Todos los archivos",
                        "*.*"
                    )
                ]
            )
        )


        if not ruta_recuperacion:

            return


        # ----------------------------------------------------
        # Introducir frase de recuperación
        # ----------------------------------------------------

        frase_recuperacion = (
            simpledialog.askstring(
                "Frase de recuperación",
                "Ingrese la frase de recuperación:",
                parent=ventana,
                show="*"
            )
        )


        if frase_recuperacion is None:

            return


        if not frase_recuperacion.strip():

            messagebox.showwarning(
                "Frase inválida",
                "La frase de recuperación "
                "no puede estar vacía.",
                parent=ventana
            )

            return


        # ----------------------------------------------------
        # Seleccionar backup
        # ----------------------------------------------------

        ruta_backup = (
            filedialog.askopenfilename(
                parent=ventana,
                title=(
                    "Seleccionar backup cifrado "
                    "para recuperar"
                ),
                initialdir=CARPETA_BACKUPS,
                filetypes=[
                    (
                        "Backups cifrados",
                        "*.enc"
                    ),
                    (
                        "Todos los archivos",
                        "*.*"
                    )
                ]
            )
        )


        if not ruta_backup:

            return


        nombre_backup = os.path.basename(
            ruta_backup
        )


        # ----------------------------------------------------
        # Confirmación final
        # ----------------------------------------------------

        respuesta = messagebox.askyesno(
            "Confirmar recuperación",
            "ATENCIÓN\n\n"
            "Se utilizará el archivo de recuperación "
            "para obtener la clave de datos del SGE.\n\n"
            f"Backup seleccionado:\n"
            f"{nombre_backup}\n\n"
            "La base de datos actual será reemplazada "
            "solamente después de comprobar que el backup "
            "puede descifrarse y que SQLite es válida.\n\n"
            "¿Desea continuar?",
            parent=ventana
        )


        if not respuesta:

            return


        ruta_temporal = (
            RUTA_BASE_DATOS
            + ".emergencia_tmp"
        )


        try:

            # ------------------------------------------------
            # 1. Recuperar la clave mediante la frase
            # ------------------------------------------------

            clave_datos = (
                recuperar_clave_datos(
                    frase_recuperacion,
                    ruta_recuperacion
                )
            )


            # ------------------------------------------------
            # 2. Eliminar temporal anterior
            # ------------------------------------------------

            if os.path.exists(
                ruta_temporal
            ):

                os.remove(
                    ruta_temporal
                )


            # ------------------------------------------------
            # 3. Descifrar el backup
            #
            # Se utiliza la clave recuperada mediante
            # el archivo externo y la frase.
            # ------------------------------------------------

            descifrar_backup(
                ruta_backup,
                ruta_temporal,
                clave_datos
            )


            # ------------------------------------------------
            # 4. Verificar SQLite
            # ------------------------------------------------

            verificar_base_sqlite(
                ruta_temporal
            )


            # ------------------------------------------------
            # 5. Reemplazar base actual
            # ------------------------------------------------

            os.replace(
                ruta_temporal,
                RUTA_BASE_DATOS
            )


            # ------------------------------------------------
            # 6. Actualizar pantalla
            # ------------------------------------------------

            actualizar_proteccion()
            actualizar_backup()


            messagebox.showinfo(
                "Recuperación completada",
                "La recuperación de emergencia "
                "se completó correctamente.\n\n"
                "La clave de datos fue recuperada "
                "mediante el archivo externo.\n\n"
                "El backup fue descifrado y la base SQLite "
                "superó la comprobación de integridad.\n\n"
                "La base de datos del SGE fue restaurada "
                "correctamente.",
                parent=ventana
            )


        except Exception as error:

            # ------------------------------------------------
            # Si algo falla, eliminar temporal.
            #
            # La base actual solamente se reemplaza después
            # de superar la recuperación y la verificación.
            # ------------------------------------------------

            if os.path.exists(
                ruta_temporal
            ):

                try:

                    os.remove(
                        ruta_temporal
                    )

                except OSError:

                    pass


            messagebox.showerror(
                "Error de recuperación",
                "No fue posible completar "
                "la recuperación de emergencia.\n\n"
                "La base de datos actual "
                "no fue reemplazada.\n\n"
                f"Detalle:\n{error}",
                parent=ventana
            )


    # ========================================================
    # ACTUALIZAR TODO
    # ========================================================

    def actualizar_todo():

        actualizar_proteccion()
        actualizar_backup()


    # ========================================================
    # BOTONES
    # ========================================================

    frame_botones = tk.Frame(
        ventana
    )

    frame_botones.pack(
        pady=15
    )


    # --------------------------------------------------------
    # Crear backup
    # --------------------------------------------------------

    tk.Button(
        frame_botones,
        text="💾 Crear backup ahora",
        font=("Arial", 12, "bold"),
        width=28,
        height=2,
        command=ejecutar_backup
    ).pack(
        pady=4
    )


    # --------------------------------------------------------
    # Restaurar backup
    # --------------------------------------------------------

    tk.Button(
        frame_botones,
        text="🔄 Restaurar backup",
        font=("Arial", 12, "bold"),
        width=28,
        height=2,
        command=ejecutar_restauracion
    ).pack(
        pady=4
    )


    # --------------------------------------------------------
    # Recuperación de emergencia
    # --------------------------------------------------------

    tk.Button(
        frame_botones,
        text="🆘 Recuperación de emergencia",
        font=("Arial", 12, "bold"),
        width=28,
        height=2,
        command=ejecutar_recuperacion_emergencia
    ).pack(
        pady=4
    )


    # --------------------------------------------------------
    # Actualizar estado
    # --------------------------------------------------------

    tk.Button(
        frame_botones,
        text="🔃 Actualizar estado",
        font=("Arial", 11),
        width=28,
        command=actualizar_todo
    ).pack(
        pady=4
    )


    # --------------------------------------------------------
    # Cerrar
    # --------------------------------------------------------

    tk.Button(
        frame_botones,
        text="Cerrar",
        font=("Arial", 11),
        width=28,
        command=ventana.destroy
    ).pack(
        pady=4
    )


    # ========================================================
    # FINALIZAR VENTANA
    # ========================================================

    centrar_ventana(
        ventana
    )


    ventana.lift()

    ventana.focus_force()


    ventana.after(
        100,
        actualizar_todo
    )


    return ventana


# ============================================================
# PRUEBA DIRECTA
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PRUEBA DE seguridad_sge.py")
    print("=" * 60)

    ventana_seguridad()

    print(
        "Ventana de seguridad creada correctamente."
    )

    tk.mainloop()