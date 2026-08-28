from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resultado_simulacion import ResultadoSimulacion
from app.schemas.ley_little import (
    LeyLittleEntrada,
    LeyLittleSalida,
    VerificacionEntrada,
    VerificacionSalida,
)
from app.services.ley_little import calcular_ley_little, verificar_consistencia

router = APIRouter(prefix="/modelos/ley-little", tags=["Ley de Little"])


@router.post("/", response_model=LeyLittleSalida)
def ejecutar_ley_little(datos: LeyLittleEntrada, db: Session = Depends(get_db)):
    try:
        resultado = calcular_ley_little(lam=datos.lam, w=datos.w, l=datos.l)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="ley_little",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado


@router.post("/verificar", response_model=VerificacionSalida)
def ejecutar_verificacion(datos: VerificacionEntrada, db: Session = Depends(get_db)):
    try:
        resultado = verificar_consistencia(
            lam=datos.lam,
            w=datos.w,
            l_observado=datos.l_observado,
            tolerancia=datos.tolerancia,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    registro = ResultadoSimulacion(
        modelo="ley_little_verificacion",
        parametros_entrada=datos.model_dump(),
        resultados=resultado,
    )
    db.add(registro)
    db.commit()

    return resultado
