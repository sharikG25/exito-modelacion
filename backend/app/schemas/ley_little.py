from typing import Optional
from pydantic import BaseModel, Field, model_validator


class LeyLittleEntrada(BaseModel):
    lam: Optional[float] = Field(None, gt=0, description="Tasa de llegada (clientes por minuto)")
    w: Optional[float] = Field(None, gt=0, description="Tiempo promedio en el sistema (minutos)")
    l: Optional[float] = Field(None, gt=0, description="Número promedio de clientes en el sistema")

    @model_validator(mode="after")
    def exactamente_dos_valores(self):
        dados = [v for v in (self.lam, self.w, self.l) if v is not None]
        if len(dados) != 2:
            raise ValueError("Debes proporcionar exactamente 2 de las 3 variables (lam, w, l).")
        return self

    class Config:
        json_schema_extra = {
            "example": {"lam": 2.0, "w": 1.2}
        }


class LeyLittleSalida(BaseModel):
    modelo: str
    lam: float
    w: float
    l: float
    variable_calculada: str


class VerificacionEntrada(BaseModel):
    lam: float = Field(..., gt=0, description="Tasa de llegada observada (clientes por minuto)")
    w: float = Field(..., gt=0, description="Tiempo promedio en el sistema observado (minutos)")
    l_observado: float = Field(..., gt=0, description="Número promedio de clientes en el sistema, observado")
    tolerancia: float = Field(0.05, gt=0, lt=1, description="Tolerancia relativa aceptada (ej. 0.05 = 5%)")


class VerificacionSalida(BaseModel):
    modelo: str
    l_esperado_segun_little: float
    l_observado: float
    diferencia_relativa: float
    es_consistente: bool
    tolerancia_usada: float
