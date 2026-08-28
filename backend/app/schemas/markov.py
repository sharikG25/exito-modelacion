from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MarkovEntrada(BaseModel):
    estados: List[str] = Field(..., min_length=2, description="Nombres de las zonas del almacén")
    matriz_transicion: List[List[float]] = Field(
        ..., description="Matriz NxN de probabilidades de transición entre zonas"
    )
    estado_inicial: str = Field(..., description="Zona donde comienza el cliente")
    n_pasos: int = Field(10, ge=1, description="Número de pasos a simular/proyectar")
    estados_absorbentes: Optional[List[str]] = Field(
        None, description="Zonas donde el cliente sale del sistema, ej. 'Salida'"
    )
    semilla: Optional[int] = Field(None, description="Semilla aleatoria para el recorrido simulado")

    class Config:
        json_schema_extra = {
            "example": {
                "estados": ["Entrada", "Pasillos", "Cajas", "Salida"],
                "matriz_transicion": [
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.7, 0.3, 0.0],
                    [0.0, 0.1, 0.2, 0.7],
                    [0.0, 0.0, 0.0, 1.0],
                ],
                "estado_inicial": "Entrada",
                "n_pasos": 8,
                "estados_absorbentes": ["Salida"],
                "semilla": 42,
            }
        }


class MarkovSalida(BaseModel):
    modelo: str
    estados: List[str]
    estado_inicial: str
    distribucion_por_paso: List[Dict[str, float]]
    recorrido_simulado: List[str]
    pasos_hasta_absorcion: Optional[Dict[str, float]] = None
