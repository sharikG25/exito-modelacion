from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.distribucion_servicio import (
    DistribucionServicioEntrada,
    DistribucionServicioSalida,
)
from app.services.distribucion_servicio import analizar_distribucion_servicio

router = APIRouter(prefix="/modelos/distribucion-servicio", tags=["Distribución de tiempo de servicio"])


@router.post("/", response_model=DistribucionServicioSalida)
def ejecutar_distribucion_servicio(datos: DistribucionServicioEntrada, db: Session = Depends(get_db)):
    try:
        resultado = analizar_distribucion_servicio(
            tiempos_servicio=datos.tiempos_servicio,
            tiempo_objetivo=datos.tiempo_objetivo,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="distribucion_servicio",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
