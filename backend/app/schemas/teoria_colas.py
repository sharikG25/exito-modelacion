from pydantic import BaseModel, Field


class TeoriaColasEntrada(BaseModel):
    lam: float = Field(..., gt=0, description="Tasa de llegada de clientes (clientes por minuto)")
    mu: float = Field(..., gt=0, description="Tasa de servicio por caja (clientes por minuto)")
    c: int = Field(1, ge=1, description="Número de cajas abiertas")

    class Config:
        json_schema_extra = {
            "example": {"lam": 2.5, "mu": 3.0, "c": 2}
        }


class TeoriaColasSalida(BaseModel):
    modelo: str
    c: int | None = None
    rho: float
    p0: float
    l: float
    lq: float
    w: float
    wq: float
    prob_esperar: float
