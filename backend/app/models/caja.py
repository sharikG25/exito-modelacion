from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Caja(Base):
    __tablename__ = "cajas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True)   # True = abierta
    cajero_asignado = Column(String, nullable=True)
    tasa_servicio = Column(Float, nullable=False)  # mu: clientes atendidos por minuto

    clientes = relationship("Cliente", back_populates="caja")
