from negocio.motor_inasistencias import analizar_cargo, obtener_asignaciones_docente
from negocio.motor_inasistencias import (
    obtener_asignaciones_docente,
    separar_asignaciones
)
asignaciones = obtener_asignaciones_docente(2)

cargos, modulos = separar_asignaciones(asignaciones)

print("CARGOS")
print(cargos)

print()

print("MODULOS")
print(modulos)