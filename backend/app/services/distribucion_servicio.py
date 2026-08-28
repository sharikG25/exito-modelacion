"""
Modelo matemático 6: Distribución de probabilidad del tiempo de servicio

Ajusta una muestra de tiempos de atención (en minutos) a las distribuciones
Exponencial y Normal, y usa la prueba de bondad de ajuste de
Kolmogorov-Smirnov (KS) para decidir cuál describe mejor los datos.

Este análisis es el insumo para decidir qué supuesto usar en el modelo de
teoría de colas (paso 3): M/M/1 y M/M/c asumen tiempos de servicio
exponenciales, así que este modelo permite validar (o cuestionar) ese
supuesto con datos reales, antes de confiar en los resultados analíticos.

Entrada:
    tiempos_servicio   muestra de tiempos de atención por cliente (minutos)
    tiempo_objetivo    opcional; tiempo "aceptable" de atención, para
                        estimar P(tiempo de servicio > tiempo_objetivo)
                        bajo cada distribución ajustada

Salida:
    n, media, desviacion, varianza    estadísticos descriptivos de la muestra
    ajuste_exponencial                {lambda, ks_estadistico, ks_p_valor,
                                        prob_superar_objetivo?}
    ajuste_normal                     {media, desviacion, ks_estadistico,
                                        ks_p_valor, prob_superar_objetivo?}
    mejor_ajuste                      "Exponencial" o "Normal", según cuál
                                       tiene mayor p-valor en la prueba KS
                                       (es decir, cuál se rechaza menos)
"""

from typing import Dict, List, Optional

import numpy as np
from scipy import stats


def _ajustar_exponencial(muestra: np.ndarray, tiempo_objetivo: Optional[float]) -> Dict:
    media = float(np.mean(muestra))
    if media <= 0:
        raise ValueError("La media de la muestra debe ser mayor que 0 para ajustar una Exponencial.")

    lam = 1 / media  # estimador de máxima verosimilitud para Exponencial

    ks_estadistico, ks_p_valor = stats.kstest(muestra, "expon", args=(0, media))

    resultado = {
        "lambda": round(lam, 4),
        "ks_estadistico": round(float(ks_estadistico), 4),
        "ks_p_valor": round(float(ks_p_valor), 4),
    }

    if tiempo_objetivo is not None:
        # P(X > t) para una Exponencial(lambda) = e^(-lambda * t)
        resultado["prob_superar_objetivo"] = round(
            float(stats.expon.sf(tiempo_objetivo, scale=media)), 4
        )

    return resultado


def _ajustar_normal(muestra: np.ndarray, tiempo_objetivo: Optional[float]) -> Dict:
    media = float(np.mean(muestra))
    desviacion = float(np.std(muestra, ddof=1)) if len(muestra) > 1 else 0.0

    if desviacion <= 0:
        raise ValueError(
            "La muestra no tiene variabilidad (desviación = 0); no se puede ajustar una Normal."
        )

    ks_estadistico, ks_p_valor = stats.kstest(muestra, "norm", args=(media, desviacion))

    resultado = {
        "media": round(media, 4),
        "desviacion": round(desviacion, 4),
        "ks_estadistico": round(float(ks_estadistico), 4),
        "ks_p_valor": round(float(ks_p_valor), 4),
    }

    if tiempo_objetivo is not None:
        # P(X > t) para una Normal(media, desviacion)
        resultado["prob_superar_objetivo"] = round(
            float(stats.norm.sf(tiempo_objetivo, loc=media, scale=desviacion)), 4
        )

    return resultado


def analizar_distribucion_servicio(
    tiempos_servicio: List[float],
    tiempo_objetivo: Optional[float] = None,
) -> Dict:
    if len(tiempos_servicio) < 2:
        raise ValueError("Se necesitan al menos 2 tiempos de servicio para el análisis.")

    if any(t <= 0 for t in tiempos_servicio):
        raise ValueError("Todos los tiempos de servicio deben ser mayores que 0.")

    muestra = np.array(tiempos_servicio, dtype=float)

    media = float(np.mean(muestra))
    desviacion = float(np.std(muestra, ddof=1))
    varianza = float(np.var(muestra, ddof=1))

    ajuste_exponencial = _ajustar_exponencial(muestra, tiempo_objetivo)
    ajuste_normal = _ajustar_normal(muestra, tiempo_objetivo)

    # Mejor ajuste = mayor p-valor en la prueba KS (menor evidencia para
    # rechazar la hipótesis de que los datos vienen de esa distribución).
    mejor_ajuste = (
        "Exponencial"
        if ajuste_exponencial["ks_p_valor"] >= ajuste_normal["ks_p_valor"]
        else "Normal"
    )

    return {
        "modelo": "distribucion_servicio",
        "n": len(tiempos_servicio),
        "media": round(media, 4),
        "desviacion": round(desviacion, 4),
        "varianza": round(varianza, 4),
        "ajuste_exponencial": ajuste_exponencial,
        "ajuste_normal": ajuste_normal,
        "mejor_ajuste": mejor_ajuste,
        "tiempo_objetivo": tiempo_objetivo,
    }
