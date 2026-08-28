from typing import List
from pydantic import BaseModel, Field


class AsignacionEntrada(BaseModel):
    empleados: List[str] = Field(..., min_length=1, description="Nombres de los empleados disponibles")
    puestos: List[str] = Field(..., min_length=1, description="Nombres de los puestos/cajas a cubrir")
    matriz_costos: List[List[float]] = Field(
        ..., description="Matriz empleados x puestos con el costo/tiempo de cada asignación posible"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "empleados": ["Ana", "Luis", "Marta"],
                "puestos": ["Caja 1", "Caja 2", "Caja 3"],
                "matriz_costos": [
                    [4, 2, 8],
                    [3, 6, 5],
                    [7, 4, 3],
                ],
            }
        }


class AsignacionResultado(BaseModel):
    empleado: str
    puesto: str
    costo: float


class AsignacionSalida(BaseModel):
    modelo: str
    asignaciones: List[AsignacionResultado]
    costo_total: float
    empleados_sin_asignar: List[str]
    puestos_sin_cubrir: List[str]
