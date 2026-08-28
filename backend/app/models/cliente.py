from sqlalchemy import Column, Integer, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    hora_llegada = Column(DateTime, nullable=False)
    hora_inicio_atencion = Column(DateTime, nullable=True)
    hora_salida = Column(DateTime, nullable=True)
    tiempo_espera = Column(Float, nullable=True)      # en minutos
    tiempo_servicio = Column(Float, nullable=True)    # en minutos
    caja_asignada_id = Column(Integer, ForeignKey("cajas.id"), nullable=True)
    abandono = Column(Boolean, default=False)
    simulacion_id = Column(Integer, ForeignKey("resultados_simulacion.id"), nullable=True)

    caja = relationship("Caja", back_populates="clientes")
