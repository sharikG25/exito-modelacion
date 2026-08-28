"""
Modelo matemático 8: Ley de Little (L = lambda * W)

La Ley de Little es una relación fundamental, válida para cualquier
sistema en estado estable (sin importar la distribución de llegadas
o servicio): el número promedio de clientes en un sistema (L) es
igual a la tasa de llegada (lambda) multiplicada por el tiempo
promedio que cada cliente pasa en el sistema (W).

    L  = lambda * W        (clientes en todo el sistema: fila + servicio)
    Lq = lambda * Wq        (clientes solo en la fila)

Este modelo permite:
    1. Calcular la variable faltante si se conocen las otras dos
       (ej. si mides lambda y W en campo, puedes obtener L sin necesidad
       de contarlos directamente).
    2. Verificar la consistencia entre los resultados de los otros
       modelos (teoría de colas, simulación DES): si L != lambda * W
       en los resultados de otro modelo, algo no cuadra.

Entrada (dar exactamente 2 de las 3 variables; la tercera se calcula):
    lam    tasa de llegada (clientes/minuto)
    w      tiempo promedio en el sistema (minutos)
    l      número promedio de clientes en el sistema

Salida:
    lam, w, l              los tres valores (el que faltaba, calculado)
    variable_calculada     cuál de los tres se calculó
"""

from typing import Dict, Optional


def calcular_ley_little(
    lam: Optional[float] = None,
    w: Optional[float] = None,
    l: Optional[float] = None,
) -> Dict:
    valores_dados = [v for v in (lam, w, l) if v is not None]
    if len(valores_dados) != 2:
        raise ValueError(
            "Debes proporcionar exactamente 2 de las 3 variables (lam, w, l); "
            "la tercera se calcula automáticamente."
        )

    for nombre, valor in (("lam", lam), ("w", w), ("l", l)):
        if valor is not None and valor <= 0:
            raise ValueError(f"El valor de '{nombre}' debe ser mayor que 0.")

    if l is None:
        l = lam * w
        variable_calculada = "l"
    elif w is None:
        if lam == 0:
            raise ValueError("lam no puede ser 0 al calcular w.")
        w = l / lam
        variable_calculada = "w"
    else:  # lam is None
        if w == 0:
            raise ValueError("w no puede ser 0 al calcular lam.")
        lam = l / w
        variable_calculada = "lam"

    return {
        "modelo": "ley_little",
        "lam": round(lam, 4),
        "w": round(w, 4),
        "l": round(l, 4),
        "variable_calculada": variable_calculada,
    }


def verificar_consistencia(lam: float, w: float, l_observado: float, tolerancia: float = 0.05) -> Dict:
    """
    Compara el L observado (por ejemplo, en una simulación DES) contra el L
    esperado por la Ley de Little (lam * w), para validar la consistencia
    de los resultados entre modelos.
    """
    if lam <= 0 or w <= 0:
        raise ValueError("lam y w deben ser mayores que 0.")

    l_esperado = round(lam * w, 4)
    diferencia_relativa = round(abs(l_observado - l_esperado) / l_esperado, 4) if l_esperado > 0 else 0.0
    es_consistente = diferencia_relativa <= tolerancia

    return {
        "modelo": "ley_little_verificacion",
        "l_esperado_segun_little": l_esperado,
        "l_observado": round(l_observado, 4),
        "diferencia_relativa": diferencia_relativa,
        "es_consistente": es_consistente,
        "tolerancia_usada": tolerancia,
    }
