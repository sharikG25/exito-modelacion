from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.asignacion import AsignacionEntrada, AsignacionSalida
from app.services.asignacion import calcular_asignacion

router = APIRouter(prefix="/modelos/asignacion", tags=["Asignación de personal"])


@router.post("/", response_model=AsignacionSalida)
def ejecutar_asignacion(datos: AsignacionEntrada, db: Session = Depends(get_db)):
    try:
        resultado = calcular_asignacion(
            empleados=datos.empleados,
            puestos=datos.puestos,
            matriz_costos=datos.matriz_costos,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="asignacion_personal",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
