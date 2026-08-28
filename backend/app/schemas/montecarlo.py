from typing import List, Optional
from pydantic import BaseModel, Field


class MontecarloEntrada(BaseModel):
    lam: float = Field(..., gt=0, description="Tasa promedio de llegada (clientes por minuto)")
    duracion_min: float = Field(..., gt=0, description="Duración de la simulación en minutos")
    tiempo_servicio_prom: Optional[float] = Field(
        None, gt=0, description="Tiempo promedio de servicio por cliente (minutos), opcional"
    )
    semilla: Optional[int] = Field(None, description="Semilla aleatoria para resultados reproducibles")

    class Config:
        json_schema_extra = {
            "example": {"lam": 2.0, "duracion_min": 480, "tiempo_servicio_prom": 3.0, "semilla": 42}
        }


class MontecarloSalida(BaseModel):
    modelo: str
    numero_clientes: int
    tiempos_llegada: List[float]
    tiempos_entre_llegadas: List[float]
    promedio_entre_llegadas: float
    tasa_llegada_observada: float
    clientes_por_hora: List[int]
    tiempos_servicio_simulados: Optional[List[float]] = None
