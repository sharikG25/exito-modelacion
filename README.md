# Simulación Almacenes Éxito

Software de modelación icónica, analógica y analítica del flujo de clientes en un almacén tipo Éxito.

## Stack
- **Backend:** Python (FastAPI) + SQLAlchemy + PostgreSQL
- **Frontend:** Angular
- **Diseño:** Figma
- **Despliegue:** Railway (backend + BD) / Vercel (frontend)

## Estructura actual

```
backend/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── cliente.py
│   │   ├── caja.py
│   │   ├── almacen.py
│   │   ├── simulacion_evento.py
│   │   └── resultado_simulacion.py
│   ├── schemas/
│   │   ├── teoria_colas.py
│   │   ├── montecarlo.py
│   │   ├── markov.py
│   │   ├── pronostico.py
│   │   ├── asignacion.py
│   │   ├── distribucion_servicio.py
│   │   ├── simulacion_des.py
│   │   └── ley_little.py
│   ├── routers/
│   │   ├── teoria_colas.py
│   │   ├── montecarlo.py
│   │   ├── markov.py
│   │   ├── pronostico.py
│   │   ├── asignacion.py
│   │   ├── distribucion_servicio.py
│   │   ├── simulacion_des.py
│   │   └── ley_little.py
│   └── services/
│       ├── teoria_colas.py          (Modelo M/M/1 y M/M/c)
│       ├── montecarlo.py            (Simulación de llegadas ~ Poisson/Exponencial)
│       ├── markov.py                (Cadena de Markov: recorrido del cliente)
│       ├── pronostico.py            (Promedio móvil, suavización exponencial, regresión lineal)
│       ├── asignacion.py            (Algoritmo húngaro: asignación de personal)
│       ├── distribucion_servicio.py (Ajuste Exponencial/Normal + prueba KS)
│       ├── simulacion_des.py        (Simulación de eventos discretos, cliente por cliente)
│       └── ley_little.py            (Ley de Little: L = lambda * W, y verificación cruzada)
├── requirements.txt
├── .env.example
├── alembic.ini
└── alembic/
    ├── env.py              (usa Base.metadata y DATABASE_URL de app/database.py)
    └── versions/
        └── ..._esquema_inicial.py

docker-compose.yml   (Postgres local para desarrollo)
```

## Cómo correr el backend

**1. Levantar PostgreSQL local con Docker** (recomendado; evita instalar Postgres a mano):
```bash
docker compose up -d
```
Esto levanta Postgres en `localhost:5432` con las mismas credenciales que espera `.env.example`
(usuario `usuario`, contraseña `password`, base de datos `exito_simulacion`), con un volumen
persistente para que los datos sobrevivan reinicios.

Si prefieres usar tu propia instalación de Postgres, sáltate este paso y solo asegúrate de que
`DATABASE_URL` en tu `.env` apunte a una base existente.

**2. Levantar la API:**
```bash
cd backend
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # ajusta DATABASE_URL solo si no usaste el docker-compose de arriba
alembic upgrade head          # crea/actualiza las tablas según las migraciones
uvicorn app.main:app --reload
```

La API quedará disponible en `http://localhost:8000` y la documentación interactiva en `http://localhost:8000/docs`.

## Migraciones (Alembic)

El esquema de la base de datos se versiona con Alembic — ya no se usa `Base.metadata.create_all()`.
Todos los comandos se corren desde `backend/` con el entorno virtual activado.

```bash
alembic upgrade head                              # aplica todas las migraciones pendientes
alembic downgrade -1                               # revierte la última migración
alembic revision --autogenerate -m "algo cambió"   # genera una migración a partir de cambios en app/models/
alembic current                                     # muestra la migración aplicada actualmente
alembic history                                     # lista todas las migraciones
```

Flujo al modificar un modelo (ej. agregar una columna en `app/models/cliente.py`):
1. Edita el modelo SQLAlchemy.
2. Corre `alembic revision --autogenerate -m "descripción del cambio"`.
3. **Revisa el archivo generado en `alembic/versions/`** — el autogenerate no siempre detecta
   todo correctamente (ej. renombrar una columna se ve como "borrar + crear"; hay que ajustarlo).
4. Corre `alembic upgrade head` para aplicarla.

La migración inicial (`alembic/versions/..._esquema_inicial.py`) crea las 5 tablas del modelo de
datos (`almacenes`, `cajas`, `clientes`, `resultados_simulacion`, `simulacion_eventos`) y fue
verificada: se probó `upgrade` → `alembic check` (sin diffs pendientes contra los modelos) →
`downgrade`, confirmando que es reversible y coincide exactamente con `app/models/`.

## Modelo de datos

- **Cliente**: llegada, inicio/fin de atención, tiempo de espera/servicio, caja asignada, abandono
- **Caja**: número, estado, cajero asignado, tasa de servicio (μ)
- **Almacen**: nombre, sede, número de cajas, capacidad máxima
- **SimulacionEvento**: registro de eventos (llegada / inicio_servicio / fin_servicio / abandono) para reconstruir el recorrido del cliente
- **ResultadoSimulacion**: parámetros de entrada y resultados de cada modelo matemático ejecutado

## Endpoint disponible: Teoría de colas

`POST /modelos/teoria-colas/`

Body de ejemplo:
```json
{
  "lam": 2.5,
  "mu": 3.0,
  "c": 2
}
```

- `lam`: tasa de llegada de clientes (clientes/minuto)
- `mu`: tasa de servicio por caja (clientes/minuto)
- `c`: número de cajas abiertas

Devuelve `rho` (utilización), `p0`, `l`/`lq` (clientes en sistema/fila), `w`/`wq` (tiempo en sistema/fila) y `prob_esperar`. Internamente decide entre el modelo M/M/1 (una caja) o M/M/c (varias cajas, fórmula de Erlang C), y guarda cada ejecución en la tabla `resultados_simulacion`.

## Endpoint disponible: Simulación de Montecarlo (llegadas)

`POST /modelos/montecarlo/`

Body de ejemplo:
```json
{
  "lam": 2.0,
  "duracion_min": 480,
  "tiempo_servicio_prom": 3.0,
  "semilla": 42
}
```

- `lam`: tasa promedio de llegada de clientes (clientes/minuto)
- `duracion_min`: duración de la jornada simulada (ej. 480 = 8 horas)
- `tiempo_servicio_prom`: opcional, si se incluye también genera tiempos de servicio simulados por cliente
- `semilla`: opcional, para que la simulación sea reproducible

Genera los tiempos de llegada de cada cliente usando un proceso de Poisson (intervalos exponenciales), y devuelve el listado completo de llegadas, el promedio observado entre llegadas, la tasa observada, y un histograma de clientes por hora. Este resultado puede alimentar directamente al modelo de teoría de colas o a la futura simulación de eventos discretos.

## Endpoint disponible: Cadenas de Markov (recorrido del cliente)

`POST /modelos/markov/`

Body de ejemplo:
```json
{
  "estados": ["Entrada", "Pasillos", "Cajas", "Salida"],
  "matriz_transicion": [
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.7, 0.3, 0.0],
    [0.0, 0.1, 0.2, 0.7],
    [0.0, 0.0, 0.0, 1.0]
  ],
  "estado_inicial": "Entrada",
  "n_pasos": 8,
  "estados_absorbentes": ["Salida"],
  "semilla": 42
}
```

- `estados`: nombres de las zonas del almacén (icónico: coinciden con el layout de Figma)
- `matriz_transicion`: fila i = probabilidad de pasar de la zona i a cada otra zona (cada fila debe sumar 1.0)
- `estado_inicial`: zona donde entra el cliente
- `estados_absorbentes`: zonas donde el cliente sale del sistema (ej. "Salida")

Devuelve la distribución de probabilidad de estar en cada zona en cada paso, un recorrido concreto simulado (útil para animar la vista icónica), y el número esperado de pasos hasta salir del almacén desde cada zona (usando la matriz fundamental de cadenas absorbentes).

## Endpoint disponible: Pronóstico de afluencia

`POST /modelos/pronostico/`

Body de ejemplo:
```json
{
  "historico": [120, 135, 128, 150, 145, 160, 158],
  "metodo": "suavizacion_exponencial",
  "n_periodos_pred": 3,
  "alpha": 0.3
}
```

- `historico`: serie de clientes observados por periodo (hora/día)
- `metodo`: `"promedio_movil"`, `"suavizacion_exponencial"` o `"regresion_lineal"`
- `ventana`: tamaño de la ventana (solo si el método es promedio móvil)
- `alpha`: factor de suavizado entre 0 y 1 (solo si el método es suavización exponencial)

Devuelve los valores ajustados sobre el histórico, el pronóstico para los próximos periodos, y el error medio absoluto (MAE) para comparar qué tan bien ajusta cada método. Este pronóstico alimenta directamente la asignación de personal (paso 7) y la simulación de eventos discretos (paso 9).

## Endpoint disponible: Asignación de personal (algoritmo húngaro)

`POST /modelos/asignacion/`

Body de ejemplo:
```json
{
  "empleados": ["Ana", "Luis", "Marta"],
  "puestos": ["Caja 1", "Caja 2", "Caja 3"],
  "matriz_costos": [
    [4, 2, 8],
    [3, 6, 5],
    [7, 4, 3]
  ]
}
```

- `empleados` / `puestos`: nombres de empleados y de puestos/cajas a cubrir (no necesitan ser del mismo tamaño)
- `matriz_costos[i][j]`: costo (o tiempo estimado de atención) de asignar al empleado i al puesto j

Resuelve el problema de asignación óptima usando el algoritmo húngaro (`scipy.optimize.linear_sum_assignment`), devolviendo la combinación empleado-puesto que minimiza el costo total, junto con empleados sin asignar o puestos sin cubrir si las cantidades no coinciden.

## Endpoint disponible: Distribución de tiempo de servicio

`POST /modelos/distribucion-servicio/`

Body de ejemplo:
```json
{
  "tiempos_servicio": [2.1, 3.4, 1.8, 2.9, 4.2, 2.5, 3.0, 2.2, 3.8, 2.6],
  "tiempo_objetivo": 4.0
}
```

- `tiempos_servicio`: muestra de tiempos reales de atención por cliente (minutos)
- `tiempo_objetivo`: opcional, tiempo "aceptable" de atención para calcular la probabilidad de superarlo

Calcula media, desviación y varianza de la muestra, ajusta las distribuciones Exponencial y Normal (con prueba de bondad de ajuste Kolmogorov-Smirnov para saber cuál describe mejor los datos), y si se da un tiempo objetivo, estima la probabilidad de que un cliente tarde más que ese tiempo bajo cada distribución. Este análisis valida qué supuesto usar en el modelo de teoría de colas (paso 3).

## Endpoint disponible: Simulación de eventos discretos

`POST /modelos/simulacion-des/`

Body de ejemplo:
```json
{
  "lam": 2.0,
  "mu": 1.5,
  "c": 2,
  "duracion_min": 120,
  "semilla": 42
}
```

- `lam` / `mu` / `c`: mismos parámetros que en teoría de colas (llegada, servicio, número de cajas)
- `duracion_min`: duración de la jornada a simular

Simula cliente por cliente (llegada, inicio y fin de servicio), devolviendo el detalle completo de cada cliente y la lista cronológica de eventos — ideal para animar la vista icónica/analógica en el frontend. También calcula las métricas agregadas (espera promedio, longitud de fila, utilización), que fueron **validadas contra el modelo analítico M/M/c**: con duraciones largas, ambos convergen al mismo resultado, confirmando que ambos modelos son consistentes entre sí.

## Endpoint disponible: Ley de Little

`POST /modelos/ley-little/`

Body de ejemplo (solo 2 de las 3 variables; la tercera se calcula):
```json
{
  "lam": 2.0,
  "w": 1.2
}
```

- `lam`: tasa de llegada (clientes/minuto)
- `w`: tiempo promedio en el sistema (minutos)
- `l`: número promedio de clientes en el sistema

Calcula la variable faltante usando `L = λ·W`.

`POST /modelos/ley-little/verificar`

Body de ejemplo:
```json
{
  "lam": 2.0,
  "w": 1.2168,
  "l_observado": 2.4336,
  "tolerancia": 0.05
}
```

Compara el `L` observado (por ejemplo, de la simulación DES del paso 9) contra el `L` esperado según la Ley de Little, para **validar la consistencia entre todos los modelos matemáticos del proyecto**. Es el cierre natural: con este modelo puedes demostrar en tu sustentación que teoría de colas, simulación de Montecarlo, DES y Ley de Little dan resultados coherentes entre sí.

## Roadmap

1. [x] Modelo de datos
2. [x] Estructura base del backend (FastAPI + SQLAlchemy)
3. [x] Modelo matemático 1: Teoría de colas (M/M/1, M/M/c)
4. [x] Modelo matemático 2: Simulación de Montecarlo de llegadas
5. [x] Modelo matemático 3: Cadenas de Markov (recorrido del cliente)
6. [x] Modelo matemático 4: Pronóstico de afluencia
7. [x] Modelo matemático 5: Asignación de personal (algoritmo húngaro)
8. [x] Modelo matemático 6: Distribución de tiempo de servicio
9. [x] Modelo matemático 7: Simulación de eventos discretos (DES)
10. [x] Modelo matemático 8: Ley de Little (L = λW)
11. [x] Endpoints de la API por modelo — 8 de 8 completos
12. [x] Frontend Angular — scaffold + las 8 páginas de modelos implementadas
13. [x] Migraciones con Alembic — migración inicial generada, probada (upgrade/check/downgrade) y `create_all()` removido de `main.py`
14. [ ] Diseño en Figma (vista icónica y analógica)
15. [ ] Despliegue (Railway + Vercel)

> Nota de infraestructura: `docker-compose.yml` levanta Postgres local para desarrollo, y el
> esquema ahora se gestiona con Alembic (ver sección "Migraciones" arriba) en vez de
> `Base.metadata.create_all()`.

## Frontend (Angular)

Proyecto Angular 18 standalone (sin NgModules), con lazy loading por ruta.

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.component.ts       (raíz, monta el shell)
│   │   ├── app.config.ts          (providers: router + http client)
│   │   ├── app.routes.ts          (una ruta lazy por modelo)
│   │   ├── core/
│   │   │   ├── api.service.ts     (POST genérico hacia el backend)
│   │   │   └── estaciones.ts      (metadata de las 8 "estaciones" del menú)
│   │   ├── layout/
│   │   │   ├── shell.component.ts (sidebar + header con el carril de flujo)
│   │   │   └── shell.component.css
│   │   ├── shared/
│   │   │   └── metric-grid.component.ts  (tarjetas de métricas reutilizables)
│   │   └── pages/
│   │       ├── page-shared.css    (layout formulario/resultados + histogramas compartidos)
│   │       ├── teoria-colas/      (✅ implementada)
│   │       ├── montecarlo/        (✅ implementada — incluye histograma de clientes por hora)
│   │       ├── markov/            (✅ implementada — matriz editable + recorrido simulado)
│   │       ├── pronostico/        (✅ implementada — comparativo real vs. ajustado)
│   │       ├── asignacion/        (✅ implementada — matriz de costos editable)
│   │       ├── distribucion-servicio/  (✅ implementada — ajuste Exp/Normal con veredicto KS)
│   │       ├── simulacion-des/    (✅ implementada — tabla detallada por cliente)
│   │       └── ley-little/        (✅ implementada — modo "calcular variable faltante" y modo "verificar consistencia")
│   ├── environments/
│   ├── index.html
│   ├── main.ts
│   └── styles.css                 (sistema de diseño: colores, tipografía)
├── angular.json
├── package.json
└── tsconfig*.json
```

### Sistema de diseño

Concepto "sala de control de operaciones": fondo oscuro tipo consola, métricas en fuente monoespaciada (IBM Plex Mono), encabezados en Space Grotesk, y un **carril de flujo animado** en el header (puntos que se desplazan) que representa clientes moviéndose por el sistema — la firma visual del proyecto, coherente con el enfoque en el cliente definido para los 8 modelos.

### Cómo correr el frontend

```bash
cd frontend
npm install
npm start          # sirve en http://localhost:4200, conectado a la API en localhost:8000
```

Antes de desplegar, actualizar `src/environments/environment.prod.ts` con la URL real del backend en Railway.

### Patrón de cada página de modelo

Cada página en `pages/<modelo>/` sigue la misma estructura (ver `teoria-colas` como referencia):
1. Interfaz TypeScript de la salida del endpoint
2. Formulario con `[(ngModel)]` para los parámetros de entrada
3. Llamada a `ApiService.post<TSalida>(ruta, body)` al enviar
4. Resultados mostrados con `<app-metric-grid>` (u otro componente si el resultado no es tabular, como Markov o DES)

**Verificado:** el proyecto compila correctamente con `ng build` (7 páginas + scaffold), confirmando que el layout, el sistema de diseño y la integración con la API funcionan de punta a punta.
