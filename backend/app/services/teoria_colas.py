"""
Modelo matemático 1: Teoría de colas (M/M/1 y M/M/c)

Aplicado al flujo de clientes en las cajas de un almacén tipo Éxito.

Notación estándar:
    lam (λ) = tasa de llegada de clientes (clientes por minuto)
    mu  (μ) = tasa de servicio por caja (clientes atendidos por minuto)
    c       = número de cajas abiertas (servidores)

Entrada:
    lam, mu, c

Salida:
    rho              -> factor de utilización del sistema
    p0               -> probabilidad de que el sistema esté vacío
    lq               -> número promedio de clientes esperando en fila
    l                -> número promedio de clientes en el sistema (fila + siendo atendidos)
    wq               -> tiempo promedio de espera en fila (minutos)
    w                -> tiempo promedio en el sistema (minutos)
    prob_esperar     -> probabilidad de que un cliente tenga que esperar (fórmula de Erlang C)
"""

import math
from typing import Dict


def _erlang_c_p0(lam: float, mu: float, c: int) -> float:
    """Calcula P0 (probabilidad de sistema vacío) para un modelo M/M/c."""
    a = lam / mu  # intensidad de tráfico (Erlangs)

    suma = sum((a ** n) / math.factorial(n) for n in range(c))
    ultimo_termino = (a ** c) / (math.factorial(c) * (1 - (lam / (c * mu))))

    p0 = 1 / (suma + ultimo_termino)
    return p0


def calcular_mm1(lam: float, mu: float) -> Dict[str, float]:
    """Modelo M/M/1: una sola caja abierta."""
    if lam >= mu:
        raise ValueError(
            "El sistema es inestable: la tasa de llegada (lam) debe ser menor "
            "que la tasa de servicio (mu) para una sola caja."
        )

    rho = lam / mu
    p0 = 1 - rho
    l = rho / (1 - rho)
    lq = (rho ** 2) / (1 - rho)
    w = 1 / (mu - lam)
    wq = rho / (mu - lam)

    return {
        "modelo": "M/M/1",
        "rho": round(rho, 4),
        "p0": round(p0, 4),
        "l": round(l, 4),
        "lq": round(lq, 4),
        "w": round(w, 4),
        "wq": round(wq, 4),
        "prob_esperar": round(rho, 4),  # en M/M/1 coincide con rho
    }


def calcular_mmc(lam: float, mu: float, c: int) -> Dict[str, float]:
    """Modelo M/M/c: c cajas abiertas en paralelo."""
    if c < 1:
        raise ValueError("El número de cajas (c) debe ser al menos 1.")
    if lam >= c * mu:
        raise ValueError(
            "El sistema es inestable: la tasa de llegada (lam) debe ser menor "
            "que la capacidad total de servicio (c * mu)."
        )

    if c == 1:
        return calcular_mm1(lam, mu)

    a = lam / mu
    rho = lam / (c * mu)
    p0 = _erlang_c_p0(lam, mu, c)

    prob_esperar = ((a ** c) / (math.factorial(c) * (1 - rho))) * p0

    lq = (prob_esperar * rho) / (1 - rho)
    l = lq + a
    wq = lq / lam
    w = wq + (1 / mu)

    return {
        "modelo": "M/M/c",
        "c": c,
        "rho": round(rho, 4),
        "p0": round(p0, 4),
        "l": round(l, 4),
        "lq": round(lq, 4),
        "w": round(w, 4),
        "wq": round(wq, 4),
        "prob_esperar": round(prob_esperar, 4),
    }


def calcular_teoria_colas(lam: float, mu: float, c: int = 1) -> Dict[str, float]:
    """Punto de entrada único: decide entre M/M/1 o M/M/c según el número de cajas."""
    if c == 1:
        return calcular_mm1(lam, mu)
    return calcular_mmc(lam, mu, c)
