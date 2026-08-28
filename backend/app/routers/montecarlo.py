from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.montecarlo import MontecarloEntrada, MontecarloSalida
from app.services.montecarlo import simular_llegadas_montecarlo

router = APIRouter(prefix="/modelos/montecarlo", tags=["Montecarlo - Llegadas"])


@router.post("/", response_model=MontecarloSalida)
def ejecutar_montecarlo(datos: MontecarloEntrada, db: Session = Depends(get_db)):
    try:
        resultado = simular_llegadas_montecarlo(
            lam=datos.lam,
            duracion_min=datos.duracion_min,
            tiempo_servicio_prom=datos.tiempo_servicio_prom,
            semilla=datos.semilla,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="montecarlo_llegadas",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
