from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class PronosticoEntrada(BaseModel):
    historico: List[float] = Field(..., min_length=2, description="Serie histórica de clientes por periodo")
    metodo: Literal["promedio_movil", "suavizacion_exponencial", "regresion_lineal"] = Field(
        ..., description="Método de pronóstico a usar"
    )
    n_periodos_pred: int = Field(1, ge=1, description="Cantidad de periodos futuros a pronosticar")
    ventana: int = Field(3, ge=1, description="Tamaño de ventana (solo para promedio_movil)")
    alpha: float = Field(0.3, gt=0, lt=1, description="Factor de suavizado (solo para suavizacion_exponencial)")

    class Config:
        json_schema_extra = {
            "example": {
                "historico": [120, 135, 128, 150, 145, 160, 158],
                "metodo": "suavizacion_exponencial",
                "n_periodos_pred": 3,
                "alpha": 0.3,
            }
        }


class PronosticoSalida(BaseModel):
    modelo: str
    metodo: str
    valores_ajustados: List[Optional[float]]
    pronostico: List[float]
    error_medio_absoluto: float
    pendiente: Optional[float] = None
    intercepto: Optional[float] = None
