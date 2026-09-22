# =====================================================
#                 MÓDULO DE SESIÓN
# =====================================================

# Usuario actualmente conectado
usuario_actual = None

# Rol del usuario actualmente conectado
# Valores esperados:
#     ADMIN
#     USUARIO
rol_actual = None


# =====================================================
#              VERIFICAR SI ES ADMINISTRADOR
# =====================================================

def es_admin():

    return rol_actual == "ADMIN"


# =====================================================
#                    CERRAR SESIÓN
# =====================================================

def cerrar_sesion():

    global usuario_actual
    global rol_actual

    usuario_actual = None
    rol_actual = None


# =====================================================
#                    FIN DEL MÓDULO
# =====================================================

