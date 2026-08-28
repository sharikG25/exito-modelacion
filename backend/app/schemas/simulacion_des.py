from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SimulacionDESEntrada(BaseModel):
    lam: float = Field(..., gt=0, description="Tasa de llegada (clientes por minuto)")
    mu: float = Field(..., gt=0, description="Tasa de servicio por caja (clientes por minuto)")
    c: int = Field(..., ge=1, description="Número de cajas abiertas")
    duracion_min: float = Field(..., gt=0, description="Duración de la simulación en minutos")
    semilla: Optional[int] = Field(None, description="Semilla aleatoria para resultados reproducibles")

    class Config:
        json_schema_extra = {
            "example": {"lam": 2.0, "mu": 1.5, "c": 2, "duracion_min": 120, "semilla": 42}
        }


class ClienteSimulado(BaseModel):
    cliente_id: int
    hora_llegada: float
    hora_inicio_servicio: float
    hora_fin_servicio: float
    tiempo_espera: float
    tiempo_servicio: float
    tiempo_en_sistema: float
    caja_asignada: int


class EventoSimulado(BaseModel):
    tipo: str
    cliente_id: int
    tiempo: float


class SimulacionDESSalida(BaseModel):
    modelo: str
    n_clientes: int
    clientes: List[ClienteSimulado]
    eventos: List[EventoSimulado]
    metricas: Dict[str, float]
