# WinSports — Analítica de streaming deportivo

Dashboard de métricas para Win Sports (plataforma colombiana de streaming
deportivo). Procesa eventos de reproducción (START, BUFFERING, COMPLETE, …)
desde un CSV hacia MongoDB Atlas y los expone vía una API FastAPI consumida por
un frontend React.

## Stack

| Capa      | Tecnología                                  |
|-----------|---------------------------------------------|
| Base de datos | MongoDB Atlas + Motor (driver async)    |
| API       | FastAPI + Uvicorn + Pydantic v2             |
| Frontend  | React 19 + Vite + Recharts + Leaflet        |
| Entorno   | Python 3.14 + uv · Node 18+                 |

## Arquitectura de datos

Tres colecciones con responsabilidades separadas (detalle en `docs/`):

```
CSV → load_csv.py → events  ──(change stream)──>  sessions  ──(change stream)──>  content_stats
```

- **events** — fuente de verdad, un documento por evento del CSV.
- **sessions** — derivada: agrupa eventos en sesiones de reproducción.
- **content_stats** — derivada: métricas agregadas por contenido.

En desarrollo, las derivadas se construyen con `scripts/test_pipeline.py`.
En producción, los change streams las mantienen sincronizadas en tiempo real.

## Puesta en marcha

### 1. Configurar el entorno

```bash
# Dependencias de Python
uv sync

# Dependencias del frontend
cd frontend && npm install && cd ..
```

### 2. Variables de entorno

Edita el archivo `.env` de la raíz y pega tu connection string de Atlas:

```ini
MONGO_URI=mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=winsports
```

> El `.env` está en `.gitignore` — no se sube al repo.

### 3. Cargar datos

```bash
# Carga el CSV a la colección events (crea validator + índices)
uv run scripts/load_csv.py --file data/tu_archivo.csv

# Construye las colecciones derivadas (sessions + content_stats)
uv run scripts/test_pipeline.py

# Verificar conexión a Atlas en cualquier momento
uv run scripts/verify_connection.py
```

### 4. Levantar el dashboard (dos terminales)

```bash
# Terminal 1 — API
uv run uvicorn api.main:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

- Frontend: <http://localhost:5173>
- API docs (Swagger): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/api/health>

El proxy de Vite redirige `/api` → `http://localhost:8000`, así que no hay que
tocar CORS en desarrollo.

## Páginas del dashboard

| Página   | Contenido                                                              |
|----------|-----------------------------------------------------------------------|
| Overview | Total de reproducciones, usuarios únicos, contenido más visto, mapa de burbujas de usuarios activos, ranking de dispositivos y actividad por hora |
| QoE      | Buffer promedio por contenido, tasa de re-buffering, tiempo de inicialización y ranking de eventos |
| Usuarios | Perfiles (Heavy / Mid / Vague), funnel de retención, heatmap de actividad y completion por contenido |

## Estructura

```
api/          FastAPI: routes + schemas
config/       settings (.env) + constantes (colecciones, centroides de países)
db/           connection · collections (validators) · indexes · pipelines · repositories
scripts/      load_csv · test_pipeline · verify_connection
frontend/     React + Vite (src/pages, src/components, src/styles)
docs/         arquitectura, colecciones, scripts y frontend
data/         CSVs de eventos
```
