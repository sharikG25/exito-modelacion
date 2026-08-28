from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class ResultadoSimulacion(Base):
    __tablename__ = "resultados_simulacion"

    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String, nullable=False)          # ej: "teoria_colas"
    parametros_entrada = Column(JSON, nullable=False)
    resultados = Column(JSON, nullable=False)
    fecha_ejecucion = Column(DateTime, server_default=func.now())
