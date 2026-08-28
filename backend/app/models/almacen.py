from sqlalchemy import Column, Integer, String
from app.database import Base


class Almacen(Base):
    __tablename__ = "almacenes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    sede = Column(String, nullable=False)
    numero_cajas_totales = Column(Integer, nullable=False)
    capacidad_max_clientes = Column(Integer, nullable=False)
