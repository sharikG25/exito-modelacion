from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    teoria_colas,
    montecarlo,
    markov,
    pronostico,
    asignacion,
    distribucion_servicio,
    simulacion_des,
    ley_little,
)

app = FastAPI(title="Simulación Almacenes Éxito - API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # app Angular en desarrollo
    allow_methods=["*"],
    allow_headers=["*"],
)

# El esquema de la base de datos se gestiona con Alembic (ver backend/alembic/), no aquí.
# Corre `alembic upgrade head` antes de levantar la API (ver README).

app.include_router(teoria_colas.router)
app.include_router(montecarlo.router)
app.include_router(markov.router)
app.include_router(pronostico.router)
app.include_router(asignacion.router)
app.include_router(distribucion_servicio.router)
app.include_router(simulacion_des.router)
app.include_router(ley_little.router)


@app.get("/")
def root():
    return {"mensaje": "API de simulación de almacenes Éxito funcionando"}
