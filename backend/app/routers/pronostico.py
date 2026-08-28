from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.pronostico import PronosticoEntrada, PronosticoSalida
from app.services.pronostico import calcular_pronostico

router = APIRouter(prefix="/modelos/pronostico", tags=["Pronóstico de afluencia"])


@router.post("/", response_model=PronosticoSalida)
def ejecutar_pronostico(datos: PronosticoEntrada, db: Session = Depends(get_db)):
    try:
        resultado = calcular_pronostico(
            historico=datos.historico,
            metodo=datos.metodo,
            n_periodos_pred=datos.n_periodos_pred,
            ventana=datos.ventana,
            alpha=datos.alpha,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="pronostico_afluencia",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
