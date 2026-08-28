"""
Modelo matemático 5: Asignación de personal (algoritmo húngaro)

Asigna cajeros/empleados a cajas o secciones del almacén minimizando
el costo total (por ejemplo, tiempo de atención esperado, o una
combinación de habilidad/costo). Se resuelve el problema de
asignación clásico usando el algoritmo húngaro (implementado en
scipy como linear_sum_assignment).

Entrada:
    empleados          lista de nombres de empleados
    puestos            lista de nombres de puestos/cajas a cubrir
    matriz_costos      matriz de tamaño len(empleados) x len(puestos),
                        donde costos[i][j] = costo (o tiempo) de asignar
                        al empleado i al puesto j. Un costo más alto puede
                        representar, por ejemplo, menor habilidad o mayor
                        tiempo de atención esperado en ese puesto.

Salida:
    asignaciones        lista de pares {empleado, puesto, costo}
    costo_total         suma de los costos de la asignación óptima
"""

from typing import Dict, List

import numpy as np
from scipy.optimize import linear_sum_assignment


def calcular_asignacion(
    empleados: List[str],
    puestos: List[str],
    matriz_costos: List[List[float]],
) -> Dict:
    n_empleados = len(empleados)
    n_puestos = len(puestos)

    if n_empleados == 0 or n_puestos == 0:
        raise ValueError("Debe haber al menos un empleado y un puesto.")

    costos = np.array(matriz_costos, dtype=float)

    if costos.shape != (n_empleados, n_puestos):
        raise ValueError(
            f"La matriz de costos debe ser de tamaño {n_empleados}x{n_puestos} "
            f"(empleados x puestos), pero se recibió {costos.shape[0]}x{costos.shape[1]}."
        )

    # El algoritmo húngaro (linear_sum_assignment) soporta matrices rectangulares:
    # empareja min(n_empleados, n_puestos) pares minimizando el costo total.
    filas_idx, columnas_idx = linear_sum_assignment(costos)

    asignaciones = [
        {
            "empleado": empleados[i],
            "puesto": puestos[j],
            "costo": round(float(costos[i, j]), 4),
        }
        for i, j in zip(filas_idx, columnas_idx)
    ]

    costo_total = round(float(costos[filas_idx, columnas_idx].sum()), 4)

    empleados_sin_asignar = [e for idx, e in enumerate(empleados) if idx not in filas_idx]
    puestos_sin_cubrir = [p for idx, p in enumerate(puestos) if idx not in columnas_idx]

    return {
        "modelo": "asignacion_personal",
        "asignaciones": asignaciones,
        "costo_total": costo_total,
        "empleados_sin_asignar": empleados_sin_asignar,
        "puestos_sin_cubrir": puestos_sin_cubrir,
    }
