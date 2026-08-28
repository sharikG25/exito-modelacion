"""
Modelo matemático 7: Simulación de eventos discretos (DES)

Simula el flujo completo del cliente como una secuencia de eventos
(llegada, inicio de servicio, fin de servicio) sobre un sistema con
"c" cajas en paralelo. A diferencia del modelo analítico de teoría de
colas (que da promedios de largo plazo), aquí se simula cliente por
cliente, lo que permite observar la evolución del sistema en el
tiempo (por ejemplo, para animar la vista icónica/analógica) y medir
directamente tiempos de espera individuales.

Entrada:
    lam                    tasa de llegada (clientes/minuto), llegadas ~ Exponencial
    mu                     tasa de servicio por caja (clientes/minuto), servicio ~ Exponencial
    c                      número de cajas abiertas
    duracion_min           duración de la simulación (minutos)
    semilla                semilla aleatoria opcional

Salida:
    eventos                lista cronológica de eventos (llegada/inicio_servicio/fin_servicio)
    clientes                detalle por cliente: llegada, inicio, fin, espera, servicio, caja asignada
    metricas                promedios observados: espera promedio, tiempo en sistema promedio,
                            longitud promedio de la fila, utilización promedio de las cajas
"""

import math
import random
from typing import Dict, List, Optional


def _exponencial(tasa: float) -> float:
    return -math.log(1.0 - random.random()) / tasa


def simular_eventos_discretos(
    lam: float,
    mu: float,
    c: int,
    duracion_min: float,
    semilla: Optional[int] = None,
) -> Dict:
    if lam <= 0 or mu <= 0:
        raise ValueError("lam y mu deben ser mayores que 0.")
    if c < 1:
        raise ValueError("El número de cajas (c) debe ser al menos 1.")
    if duracion_min <= 0:
        raise ValueError("La duración de la simulación debe ser mayor que 0.")

    if semilla is not None:
        random.seed(semilla)

    # Generar llegadas dentro de la ventana de simulación
    llegadas = []
    t = 0.0
    while True:
        t += _exponencial(lam)
        if t > duracion_min:
            break
        llegadas.append(t)

    n_clientes = len(llegadas)

    # Estado de cada caja: momento en que queda libre
    cajas_libres_en = [0.0] * c

    clientes = []
    eventos = []

    for idx, hora_llegada in enumerate(llegadas):
        # Busca la caja libre más pronto disponible
        idx_caja = min(range(c), key=lambda i: cajas_libres_en[i])
        hora_inicio = max(hora_llegada, cajas_libres_en[idx_caja])

        tiempo_servicio = _exponencial(mu)
        hora_fin = hora_inicio + tiempo_servicio
        cajas_libres_en[idx_caja] = hora_fin

        tiempo_espera = round(hora_inicio - hora_llegada, 4)

        clientes.append({
            "cliente_id": idx + 1,
            "hora_llegada": round(hora_llegada, 4),
            "hora_inicio_servicio": round(hora_inicio, 4),
            "hora_fin_servicio": round(hora_fin, 4),
            "tiempo_espera": tiempo_espera,
            "tiempo_servicio": round(tiempo_servicio, 4),
            "tiempo_en_sistema": round(hora_fin - hora_llegada, 4),
            "caja_asignada": idx_caja + 1,
        })

        eventos.append({"tipo": "llegada", "cliente_id": idx + 1, "tiempo": round(hora_llegada, 4)})
        eventos.append({"tipo": "inicio_servicio", "cliente_id": idx + 1, "tiempo": round(hora_inicio, 4)})
        eventos.append({"tipo": "fin_servicio", "cliente_id": idx + 1, "tiempo": round(hora_fin, 4)})

    eventos.sort(key=lambda e: e["tiempo"])

    if n_clientes > 0:
        espera_promedio = round(sum(c_["tiempo_espera"] for c_ in clientes) / n_clientes, 4)
        tiempo_sistema_promedio = round(sum(c_["tiempo_en_sistema"] for c_ in clientes) / n_clientes, 4)
        clientes_que_esperaron = sum(1 for c_ in clientes if c_["tiempo_espera"] > 0)
        prob_espero = round(clientes_que_esperaron / n_clientes, 4)
    else:
        espera_promedio = 0.0
        tiempo_sistema_promedio = 0.0
        prob_espero = 0.0

    # Lq = integral de la longitud de la fila en el tiempo, dividido por la duración.
    # Cada cliente que espera aporta exactamente su tiempo de espera al área bajo la
    # curva de la fila (está "en fila" durante ese intervalo), así que el área total
    # es simplemente la suma de los tiempos de espera de todos los clientes.
    suma_esperas = sum(c_["tiempo_espera"] for c_ in clientes)
    longitud_fila_promedio = round(suma_esperas / duracion_min, 4) if duracion_min > 0 else 0.0

    tiempo_total_servicio = sum(c_["tiempo_servicio"] for c_ in clientes)
    utilizacion_promedio = round(min(tiempo_total_servicio / (c * duracion_min), 1.0), 4)

    return {
        "modelo": "simulacion_eventos_discretos",
        "n_clientes": n_clientes,
        "clientes": clientes,
        "eventos": eventos,
        "metricas": {
            "espera_promedio": espera_promedio,
            "tiempo_en_sistema_promedio": tiempo_sistema_promedio,
            "longitud_fila_promedio": longitud_fila_promedio,
            "utilizacion_promedio_cajas": utilizacion_promedio,
            "probabilidad_esperar": prob_espero,
        },
    }
