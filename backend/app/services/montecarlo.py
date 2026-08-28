"""
Modelo matemático 2: Simulación de Montecarlo de llegadas de clientes

Modela la llegada de clientes al almacén como un proceso de Poisson:
los tiempos entre llegadas siguen una distribución exponencial con
tasa lambda (clientes por minuto). Esto permite generar un día
"sintético" de llegadas para alimentar los demás modelos (colas,
asignación de personal, etc.).

Entrada:
    lam            (λ) tasa promedio de llegada (clientes por minuto)
    duracion_min   duración de la simulación en minutos (ej. 480 = jornada de 8h)
    tiempo_servicio_prom  tiempo promedio de servicio por cliente (minutos)
    semilla        semilla aleatoria opcional, para resultados reproducibles

Salida:
    numero_clientes         total de clientes generados
    tiempos_llegada         lista de minutos (desde el inicio) en que llega cada cliente
    tiempos_entre_llegadas  lista de los intervalos entre llegadas consecutivas
    promedio_entre_llegadas promedio observado de los intervalos
    tasa_llegada_observada  clientes/minuto observados en la simulación
    clientes_por_hora       histograma de clientes agrupados por hora
"""

import math
import random
from typing import Dict, List, Optional


def _generar_intervalo_exponencial(lam: float) -> float:
    """Genera un intervalo de tiempo entre llegadas ~ Exponencial(lam)."""
    return -math.log(1.0 - random.random()) / lam


def simular_llegadas_montecarlo(
    lam: float,
    duracion_min: float,
    tiempo_servicio_prom: Optional[float] = None,
    semilla: Optional[int] = None,
) -> Dict:
    if lam <= 0:
        raise ValueError("La tasa de llegada (lam) debe ser mayor que 0.")
    if duracion_min <= 0:
        raise ValueError("La duración de la simulación debe ser mayor que 0.")

    if semilla is not None:
        random.seed(semilla)

    tiempos_llegada: List[float] = []
    tiempos_entre_llegadas: List[float] = []

    t = 0.0
    while True:
        intervalo = _generar_intervalo_exponencial(lam)
        t += intervalo
        if t > duracion_min:
            break
        tiempos_llegada.append(round(t, 3))
        tiempos_entre_llegadas.append(round(intervalo, 3))

    n = len(tiempos_llegada)
    promedio_entre_llegadas = (
        round(sum(tiempos_entre_llegadas) / n, 4) if n > 0 else 0.0
    )
    tasa_llegada_observada = round(n / duracion_min, 4)

    # Histograma de clientes por hora
    num_horas = math.ceil(duracion_min / 60)
    clientes_por_hora = [0] * num_horas
    for tiempo in tiempos_llegada:
        hora_idx = min(int(tiempo // 60), num_horas - 1)
        clientes_por_hora[hora_idx] += 1

    resultado = {
        "modelo": "montecarlo_llegadas",
        "numero_clientes": n,
        "tiempos_llegada": tiempos_llegada,
        "tiempos_entre_llegadas": tiempos_entre_llegadas,
        "promedio_entre_llegadas": promedio_entre_llegadas,
        "tasa_llegada_observada": tasa_llegada_observada,
        "clientes_por_hora": clientes_por_hora,
    }

    if tiempo_servicio_prom is not None and tiempo_servicio_prom > 0:
        # Genera también un tiempo de servicio simulado por cliente (~ Exponencial)
        tiempos_servicio = [
            round(_generar_intervalo_exponencial(1 / tiempo_servicio_prom), 3)
            for _ in range(n)
        ]
        resultado["tiempos_servicio_simulados"] = tiempos_servicio

    return resultado
