from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DistribucionServicioEntrada(BaseModel):
    tiempos_servicio: List[float] = Field(
        ..., min_length=2, description="Muestra de tiempos de atención por cliente (minutos)"
    )
    tiempo_objetivo: Optional[float] = Field(
        None,
        gt=0,
        description="Tiempo 'aceptable' de atención (minutos), para calcular la probabilidad de superarlo",
    )

    @field_validator("tiempos_servicio")
    @classmethod
    def valores_positivos(cls, valores: List[float]) -> List[float]:
        if any(v <= 0 for v in valores):
            raise ValueError("Todos los tiempos de servicio deben ser mayores que 0.")
        return valores

    class Config:
        json_schema_extra = {
            "example": {
                "tiempos_servicio": [2.1, 3.4, 1.8, 2.9, 4.2, 2.5, 3.0, 2.2, 3.8, 2.6],
                "tiempo_objetivo": 4.0,
            }
        }


class AjusteExponencial(BaseModel):
    lambda_: float = Field(..., alias="lambda")
    ks_estadistico: float
    ks_p_valor: float
    prob_superar_objetivo: Optional[float] = None

    class Config:
        populate_by_name = True


class AjusteNormal(BaseModel):
    media: float
    desviacion: float
    ks_estadistico: float
    ks_p_valor: float
    prob_superar_objetivo: Optional[float] = None


class DistribucionServicioSalida(BaseModel):
    modelo: str
    n: int
    media: float
    desviacion: float
    varianza: float
    ajuste_exponencial: AjusteExponencial
    ajuste_normal: AjusteNormal
    mejor_ajuste: str
    tiempo_objetivo: Optional[float] = None
