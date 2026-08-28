from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class SimulacionEvento(Base):
    __tablename__ = "simulacion_eventos"

    id = Column(Integer, primary_key=True, index=True)
    simulacion_id = Column(Integer, ForeignKey("resultados_simulacion.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    tipo_evento = Column(String, nullable=False)  # llegada / inicio_servicio / fin_servicio / abandono
    timestamp = Column(DateTime, nullable=False)
