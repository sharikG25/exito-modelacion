"""
Modelo matemático 3: Cadenas de Markov (recorrido del cliente)

Modela el movimiento del cliente entre zonas del almacén (por ejemplo:
Entrada -> Pasillo A -> Pasillo B -> Caja -> Salida) como una cadena
de Markov: en cada paso, el cliente se mueve a otra zona (o permanece)
según una matriz de probabilidades de transición que solo depende de
la zona actual (propiedad de Markov).

Entrada:
    estados               lista de nombres de las zonas, ej. ["Entrada", "Lacteos", "Cajas", "Salida"]
    matriz_transicion     matriz NxN de probabilidades (fila i = probabilidades de pasar de estado i a cada estado j)
    estado_inicial        nombre del estado donde empieza el cliente
    n_pasos               número de pasos a simular/proyectar
    estados_absorbentes   opcional, lista de estados donde el cliente "sale" del sistema (ej. "Salida")

Salida:
    distribucion_por_paso     probabilidad de estar en cada zona, para cada paso (0..n_pasos)
    recorrido_simulado        una trayectoria concreta simulada paso a paso (ej. para la vista icónica/analógica)
    pasos_hasta_absorcion     número esperado de pasos hasta llegar a un estado absorbente (si aplica)
"""

import random
from typing import Dict, List, Optional

import numpy as np


def _validar_matriz(estados: List[str], matriz: List[List[float]]) -> np.ndarray:
    n = len(estados)
    m = np.array(matriz, dtype=float)

    if m.shape != (n, n):
        raise ValueError(
            f"La matriz de transición debe ser de tamaño {n}x{n} (una fila/columna por estado)."
        )

    for i, fila in enumerate(m):
        suma = fila.sum()
        if not np.isclose(suma, 1.0, atol=1e-3):
            raise ValueError(
                f"La fila {i} ({estados[i]}) de la matriz de transición debe sumar 1.0 "
                f"(suma actual: {round(float(suma), 4)})."
            )

    return m


def calcular_distribucion_por_paso(
    estados: List[str],
    matriz: np.ndarray,
    estado_inicial_idx: int,
    n_pasos: int,
) -> List[Dict[str, float]]:
    """Calcula la distribución de probabilidad sobre los estados en cada paso, vía potencias de la matriz."""
    vector = np.zeros(len(estados))
    vector[estado_inicial_idx] = 1.0

    distribucion_por_paso = [
        {estado: round(float(p), 4) for estado, p in zip(estados, vector)}
    ]

    for _ in range(n_pasos):
        vector = vector @ matriz
        distribucion_por_paso.append(
            {estado: round(float(p), 4) for estado, p in zip(estados, vector)}
        )

    return distribucion_por_paso


def simular_recorrido(
    estados: List[str],
    matriz: np.ndarray,
    estado_inicial_idx: int,
    n_pasos: int,
    estados_absorbentes_idx: Optional[List[int]] = None,
) -> List[str]:
    """Simula una trayectoria concreta del cliente, paso a paso, hasta n_pasos o hasta caer en un estado absorbente."""
    estados_absorbentes_idx = estados_absorbentes_idx or []
    idx_actual = estado_inicial_idx
    recorrido = [estados[idx_actual]]

    for _ in range(n_pasos):
        if idx_actual in estados_absorbentes_idx:
            break
        probabilidades = matriz[idx_actual]
        idx_actual = random.choices(range(len(estados)), weights=probabilidades, k=1)[0]
        recorrido.append(estados[idx_actual])

    return recorrido


def calcular_pasos_hasta_absorcion(
    estados: List[str],
    matriz: np.ndarray,
    estados_absorbentes_idx: List[int],
) -> Optional[Dict[str, float]]:
    """
    Calcula el número esperado de pasos hasta llegar a un estado absorbente,
    para cada estado transitorio, usando la teoría de cadenas de Markov absorbentes:
        t = (I - Q)^(-1) @ 1
    donde Q es la submatriz de transiciones entre estados transitorios.
    """
    if not estados_absorbentes_idx:
        return None

    n = len(estados)
    transitorios_idx = [i for i in range(n) if i not in estados_absorbentes_idx]

    if not transitorios_idx:
        return {}

    Q = matriz[np.ix_(transitorios_idx, transitorios_idx)]
    I = np.eye(len(transitorios_idx))

    try:
        N = np.linalg.inv(I - Q)  # matriz fundamental
    except np.linalg.LinAlgError:
        return None

    t = N @ np.ones(len(transitorios_idx))

    return {
        estados[idx]: round(float(pasos), 4)
        for idx, pasos in zip(transitorios_idx, t)
    }


def calcular_markov(
    estados: List[str],
    matriz_transicion: List[List[float]],
    estado_inicial: str,
    n_pasos: int = 10,
    estados_absorbentes: Optional[List[str]] = None,
    semilla: Optional[int] = None,
) -> Dict:
    if estado_inicial not in estados:
        raise ValueError(f"El estado inicial '{estado_inicial}' no está en la lista de estados.")

    if semilla is not None:
        random.seed(semilla)

    matriz = _validar_matriz(estados, matriz_transicion)
    estado_inicial_idx = estados.index(estado_inicial)

    estados_absorbentes = estados_absorbentes or []
    for e in estados_absorbentes:
        if e not in estados:
            raise ValueError(f"El estado absorbente '{e}' no está en la lista de estados.")
    estados_absorbentes_idx = [estados.index(e) for e in estados_absorbentes]

    distribucion_por_paso = calcular_distribucion_por_paso(
        estados, matriz, estado_inicial_idx, n_pasos
    )
    recorrido_simulado = simular_recorrido(
        estados, matriz, estado_inicial_idx, n_pasos, estados_absorbentes_idx
    )
    pasos_hasta_absorcion = calcular_pasos_hasta_absorcion(
        estados, matriz, estados_absorbentes_idx
    )

    return {
        "modelo": "cadena_markov",
        "estados": estados,
        "estado_inicial": estado_inicial,
        "distribucion_por_paso": distribucion_por_paso,
        "recorrido_simulado": recorrido_simulado,
        "pasos_hasta_absorcion": pasos_hasta_absorcion,
    }
