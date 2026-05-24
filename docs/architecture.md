# Arquitectura WinSports

## Contexto
Sistema de analítica para Win Sports, plataforma colombiana de streaming deportivo.
El dataset contiene eventos de reproducción (START, PAUSE, BUFFERING, COMPLETE, etc.)
generados por usuarios en Android, iOS y Web.

## Por qué MongoDB
Los datos son eventos de streaming — cada reproducción genera una secuencia de eventos
sin esquema fijo (BufferTime solo aparece en eventos de buffering, Episode solo en series).
MongoDB maneja esta flexibilidad naturalmente sin NULLs forzados ni joins complejos.

En producción, estos eventos llegarían como live data a ~100M de documentos.
MongoDB escala horizontalmente para ese volumen sin cambiar la arquitectura.

## Tres colecciones, responsabilidades separadas

**`events`** — fuente de verdad. Raw log del CSV, un documento por evento.
Nunca se modifica después de insertarse.

**`sessions`** — derivada de events. Agrupa eventos en sesiones de reproducción
y precalcula métricas (buffer total, completion %, funnel de retención).
Evita recalcular sobre 2M de eventos en cada query del dashboard.

**`content_stats`** — derivada de sessions. Un documento por pieza de contenido
con métricas agregadas (completion rate, QoE, plays por dispositivo).
Alimenta directamente los rankings del dashboard.

## Flujo de datos
```
CSV → load_csv.py → events
↓ (change stream)
sessions
↓ (change stream)
content_stats
```
En desarrollo: load_csv.py carga events, test_pipeline.py construye las derivadas.
En producción: los change streams mantienen todo sincronizado en tiempo real.

## Stack técnico
- **MongoDB Atlas** — base de datos principal
- **Motor** — driver async de MongoDB para Python
- **FastAPI** — API REST con soporte async nativo
- **React + Vite** — dashboard frontend
- **Python 3.14 + uv** — entorno de desarrollo

## Separación de capas
```
db/collections/   validators + índices + setup de cada colección
db/indexes/       definición de índices (importados por collections)
db/pipelines/     lógica de construcción de colecciones derivadas
db/repositories/  queries hacia Mongo (una función por operación)
api/schemas/      modelos Pydantic — forma del JSON que recibe React
api/routes/       endpoints FastAPI — une repositories con schemas
```
## Decisiones que se tomaron conscientemente

**Change streams en vez de recalcular en cada request** — con 2M+ de eventos,
agregar en tiempo real sería demasiado lento para un dashboard interactivo.
Las colecciones derivadas actúan como caché persistente.

**`validationAction: "warn"` en vez de "error"** — durante carga masiva,
un documento con un campo inesperado no debe detener la inserción de 2M de filas.
Los errores se loguean sin interrumpir el proceso.

**Upsert con clave única en sessions** — subscriber_id + customer_id + start_time
garantiza idempotencia: cargar el mismo CSV dos veces no duplica sesiones.

**Scripts separados para carga y pipeline** — load_csv.py solo inserta events,
test_pipeline.py construye las derivadas. Permite iterar el pipeline sin
volver a subir el CSV completo.
