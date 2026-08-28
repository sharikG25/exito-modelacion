from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.simulacion_des import SimulacionDESEntrada, SimulacionDESSalida
from app.services.simulacion_des import simular_eventos_discretos

router = APIRouter(prefix="/modelos/simulacion-des", tags=["Simulación de eventos discretos"])


@router.post("/", response_model=SimulacionDESSalida)
def ejecutar_simulacion_des(datos: SimulacionDESEntrada, db: Session = Depends(get_db)):
    try:
        resultado = simular_eventos_discretos(
            lam=datos.lam,
            mu=datos.mu,
            c=datos.c,
            duracion_min=datos.duracion_min,
            semilla=datos.semilla,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="simulacion_eventos_discretos",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
