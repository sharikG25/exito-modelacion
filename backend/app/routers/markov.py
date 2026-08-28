from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.markov import MarkovEntrada, MarkovSalida
from app.services.markov import calcular_markov

router = APIRouter(prefix="/modelos/markov", tags=["Cadenas de Markov"])


@router.post("/", response_model=MarkovSalida)
def ejecutar_markov(datos: MarkovEntrada, db: Session = Depends(get_db)):
    try:
        resultado = calcular_markov(
            estados=datos.estados,
            matriz_transicion=datos.matriz_transicion,
            estado_inicial=datos.estado_inicial,
            n_pasos=datos.n_pasos,
            estados_absorbentes=datos.estados_absorbentes,
            semilla=datos.semilla,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="cadena_markov",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
