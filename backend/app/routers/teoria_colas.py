from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.teoria_colas import TeoriaColasEntrada, TeoriaColasSalida
from app.services.teoria_colas import calcular_teoria_colas

router = APIRouter(prefix="/modelos/teoria-colas", tags=["Teoría de colas"])


@router.post("/", response_model=TeoriaColasSalida)
def ejecutar_teoria_colas(datos: TeoriaColasEntrada, db: Session = Depends(get_db)):
    try:
        resultado = calcular_teoria_colas(lam=datos.lam, mu=datos.mu, c=datos.c)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Guardar el resultado en la base de datos para trazabilidad
    registro = ResultadoSimulacion(
        modelo="teoria_colas",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
