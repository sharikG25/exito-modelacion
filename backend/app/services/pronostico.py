"""
Modelo matemático 4: Pronóstico de afluencia de clientes

Predice cuántos clientes llegarán en los próximos periodos (horas/días)
a partir de un histórico de afluencia, usando tres métodos clásicos de
series de tiempo:

    - Promedio móvil simple (media de los últimos k periodos)
    - Suavización exponencial simple (da más peso a los datos recientes)
    - Regresión lineal (ajusta una tendencia y proyecta hacia adelante)

Entrada:
    historico        lista de valores observados (ej. clientes por hora, en orden cronológico)
    metodo            "promedio_movil" | "suavizacion_exponencial" | "regresion_lineal"
    n_periodos_pred   cuántos periodos futuros pronosticar
    ventana           (solo promedio_movil) tamaño de la ventana k
    alpha             (solo suavizacion_exponencial) factor de suavizado, 0 < alpha < 1

Salida:
    valores_ajustados     valores estimados por el modelo sobre el histórico (para comparar con lo real)
    pronostico            valores pronosticados para los próximos n_periodos_pred
    error_medio_absoluto  MAE del modelo sobre el histórico (medida de qué tan bien ajusta)
"""

from typing import Dict, List

import numpy as np


def _mae(reales: List[float], ajustados: List[float]) -> float:
    reales_arr = np.array(reales)
    ajustados_arr = np.array(ajustados)
    return round(float(np.mean(np.abs(reales_arr - ajustados_arr))), 4)


def _promedio_movil(historico: List[float], ventana: int, n_periodos_pred: int) -> Dict:
    if ventana < 1 or ventana > len(historico):
        raise ValueError("La ventana del promedio móvil debe ser >= 1 y <= la longitud del histórico.")

    valores_ajustados = [None] * ventana
    for i in range(ventana, len(historico)):
        valores_ajustados.append(round(float(np.mean(historico[i - ventana:i])), 4))

    # Pronóstico: se usa siempre el promedio de los últimos 'ventana' valores disponibles
    serie_extendida = list(historico)
    pronostico = []
    for _ in range(n_periodos_pred):
        siguiente = round(float(np.mean(serie_extendida[-ventana:])), 4)
        pronostico.append(siguiente)
        serie_extendida.append(siguiente)

    # MAE solo sobre los puntos donde sí hubo ajuste (se excluyen los primeros 'ventana' None)
    reales_validos = historico[ventana:]
    ajustados_validos = valores_ajustados[ventana:]
    mae = _mae(reales_validos, ajustados_validos) if reales_validos else 0.0

    return {
        "valores_ajustados": valores_ajustados,
        "pronostico": pronostico,
        "error_medio_absoluto": mae,
    }


def _suavizacion_exponencial(historico: List[float], alpha: float, n_periodos_pred: int) -> Dict:
    if not (0 < alpha < 1):
        raise ValueError("Alpha debe estar entre 0 y 1 (exclusivo).")

    valores_ajustados = [historico[0]]
    for i in range(1, len(historico)):
        siguiente = alpha * historico[i - 1] + (1 - alpha) * valores_ajustados[-1]
        valores_ajustados.append(round(siguiente, 4))

    ultimo_ajustado = alpha * historico[-1] + (1 - alpha) * valores_ajustados[-1]
    pronostico = [round(ultimo_ajustado, 4)] * n_periodos_pred  # la SES proyecta un valor plano

    mae = _mae(historico, valores_ajustados)

    return {
        "valores_ajustados": valores_ajustados,
        "pronostico": pronostico,
        "error_medio_absoluto": mae,
    }


def _regresion_lineal(historico: List[float], n_periodos_pred: int) -> Dict:
    n = len(historico)
    x = np.arange(n)
    y = np.array(historico)

    # Ajuste por mínimos cuadrados: y = a*x + b
    a, b = np.polyfit(x, y, 1)

    valores_ajustados = [round(float(a * xi + b), 4) for xi in x]

    x_futuro = np.arange(n, n + n_periodos_pred)
    pronostico = [round(float(a * xi + b), 4) for xi in x_futuro]

    mae = _mae(historico, valores_ajustados)

    return {
        "valores_ajustados": valores_ajustados,
        "pronostico": pronostico,
        "error_medio_absoluto": mae,
        "pendiente": round(float(a), 4),
        "intercepto": round(float(b), 4),
    }


def calcular_pronostico(
    historico: List[float],
    metodo: str,
    n_periodos_pred: int = 1,
    ventana: int = 3,
    alpha: float = 0.3,
) -> Dict:
    if len(historico) < 2:
        raise ValueError("El histórico debe tener al menos 2 observaciones.")
    if n_periodos_pred < 1:
        raise ValueError("n_periodos_pred debe ser al menos 1.")

    if metodo == "promedio_movil":
        resultado = _promedio_movil(historico, ventana, n_periodos_pred)
    elif metodo == "suavizacion_exponencial":
        resultado = _suavizacion_exponencial(historico, alpha, n_periodos_pred)
    elif metodo == "regresion_lineal":
        resultado = _regresion_lineal(historico, n_periodos_pred)
    else:
        raise ValueError(
            "Método no reconocido. Usa 'promedio_movil', 'suavizacion_exponencial' o 'regresion_lineal'."
        )

    resultado["modelo"] = "pronostico_afluencia"
    resultado["metodo"] = metodo
    return resultado
