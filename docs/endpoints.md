# WinSports API — Referencia de Endpoints

**Base URL:** `http://localhost:8000`
**Documentación interactiva:** `http://localhost:8000/docs` (Swagger UI)
**Versión:** 0.1.0

Toda la API vive bajo el prefijo `/api`. Las respuestas son JSON; los errores
retornan `{ "detail": "Mensaje en español" }`.

---

## Índice

- [General](#general)
- [Overview](#overview)
- [QoE](#qoe)
- [Users](#users)
- [Admin](#admin)
- [Códigos de error](#códigos-de-error)

---

## General

### `GET /api/health`

Ping de salud — verifica que la API responde.

**Respuesta `200`:**
```json
{ "status": "ok", "app": "WinSports", "version": "0.1.0" }
```

---

## Overview

Métricas de portada. Fuente: `sessions` y `content_stats`.

### `GET /api/overview/unique-users`
Total de suscriptores distintos. → `{ "total": 1234 }`

### `GET /api/overview/total-plays`
Total de reproducciones (= nº de sesiones). → `{ "total": 5678 }`

### `GET /api/overview/device-ranking`
Sesiones agrupadas por dispositivo.
```json
{ "devices": [ { "device": "WEB", "sessions": 320 }, { "device": "ANDR", "sessions": 210 } ] }
```

### `GET /api/overview/activity-by-hour`
Sesiones por hora del día (las 24 horas, con 0 donde no hay datos).
```json
{ "activity": [ { "hour": 0, "sessions": 12 }, { "hour": 1, "sessions": 4 } ] }
```

### `GET /api/overview/top-content`
Contenidos más vistos, agrupados por título.

| Param | Tipo | Default | Rango |
|-------|------|---------|-------|
| `limit` | int | 10 | 1–50 |

```json
{ "content": [ { "title": "Liga BetPlay", "total_plays": 120, "unique_viewers": 80, "content_type": "LIVE" } ] }
```

### `GET /api/overview/users-map`
Una burbuja por usuario activo, ubicada en el centroide de su país + jitter
determinístico. El `subscriber_id` se trunca a 8 chars (no se expone completo).

| Param | Tipo | Default | Rango |
|-------|------|---------|-------|
| `limit` | int | 800 | 1–5000 |

```json
{ "points": [ { "subscriber_id": "a1b2c3d4", "country_code": "CO", "lat": 4.57, "lon": -74.29, "sessions": 9, "total_buffer_time": 12.4 } ] }
```

---

## QoE

Calidad de experiencia. Fuente: `events` (conteos crudos) y `content_stats`.

### `GET /api/qoe/buffer-by-content`
Buffer promedio por contenido (peores primero).

| Param | Tipo | Default | Rango |
|-------|------|---------|-------|
| `limit` | int | 10 | 1–50 |

```json
{ "content": [ { "title": "Partido X", "avg_buffer_time": 2.314, "rebuffer_rate": 18.5, "total_plays": 40 } ] }
```

### `GET /api/qoe/rebuffering-rate`
Tasa de re-buffering medida por eventos y por sesiones.
```json
{
  "rebuffer_events": 350, "total_events": 10000, "event_rate": 3.5,
  "rebuffer_sessions": 60, "total_sessions": 500, "session_rate": 12.0
}
```

### `GET /api/qoe/startup-time`
Tiempo de inicialización (buffer previo al primer frame, eventos `START-BUFFERING`).
```json
{
  "avg_seconds": 1.82, "max_seconds": 9.4, "count": 480,
  "buckets": [ { "bucket": "0-1s", "count": 120 }, { "bucket": "1-2s", "count": 200 } ]
}
```

### `GET /api/qoe/event-ranking`
Ranking de tipos de evento por frecuencia (sobre `events`).
```json
{ "events": [ { "type_event": "START", "count": 5000 }, { "type_event": "PAUSE", "count": 1200 } ] }
```

---

## Users

Comportamiento y retención. Fuente: `sessions`, `content_stats` y `events`.

### `GET /api/users/retention-funnel`
Funnel por hitos de progreso (cuántas sesiones llegaron a cada cuartil).
```json
{ "total": 1000, "firstquartile": 800, "midpoint": 600, "thirdquartile": 400, "complete": 200 }
```

### `GET /api/users/activity-heatmap`
Sesiones por hora × día de semana (168 puntos; `weekday` 1=domingo … 7=sábado).
```json
{ "activity": [ { "weekday": 1, "hour": 0, "sessions": 3 } ] }
```

### `GET /api/users/content-completion-ranking`
Contenidos más completados y más abandonados.

| Param | Tipo | Default | Rango |
|-------|------|---------|-------|
| `min_plays` | int | 5 | ≥ 1 |

```json
{
  "most_completed": [ { "title": "Doc X", "total_plays": 30, "completion_rate": 92.1 } ],
  "most_abandoned": [ { "title": "Serie Y", "total_plays": 25, "completion_rate": 11.4 } ]
}
```

### `GET /api/users/user-profiles`
Clasifica usuarios por nº de eventos: **Vague** (<10), **Mid** (10–49), **Heavy** (≥50).
```json
{
  "profiles": [ { "profile": "Heavy", "count": 20, "total_events": 1500, "avg_events": 75.0, "range": "≥ 50 eventos" } ],
  "total_users": 100
}
```

---

## Admin

Operaciones de administración: carga de CSVs, conteo de colecciones y edición en
vivo de documentos. Todas bajo `/api/admin`. Las colecciones válidas son
`events`, `sessions` y `content_stats`; cualquier otra retorna `404`.

Ver también [`admin.md`](admin.md) para el panel de la UI.

### `GET /api/admin/collections`
Conteo de documentos por colección.
```json
{
  "collections": [ { "name": "events", "count": 50 }, { "name": "sessions", "count": 12 }, { "name": "content_stats", "count": 4 } ],
  "total": 66
}
```

### `POST /api/admin/upload-csv`
Sube un CSV de eventos. Lo inserta en `events` y **re-construye** `sessions` y
`content_stats`. Body `multipart/form-data` con el campo `file`.

**Validaciones:** el archivo debe terminar en `.csv` y no estar vacío (si no → `400`).

**Respuesta `200`:**
```json
{
  "filename": "nuevos.csv",
  "rows_total": 50, "rows_skipped": 2, "inserted": 48, "batch_errors": 0,
  "events_total": 98, "sessions_built": 20, "content_stats_built": 8
}
```

`curl`:
```bash
curl -F "file=@data/nuevos.csv" http://localhost:8000/api/admin/upload-csv
```

### `GET /api/admin/documents/{collection}`
Documentos paginados de una colección (para la tabla editable). `_id` se devuelve
como string.

| Param | Tipo | Default | Rango |
|-------|------|---------|-------|
| `page` | int | 1 | ≥ 1 |
| `page_size` | int | 50 | 1–500 |

```json
{ "collection": "events", "total": 50, "page": 1, "page_size": 25, "documents": [ { "_id": "65aa…", "title": "Liga", "duration": 120 } ] }
```

### `PUT /api/admin/documents/{collection}/{doc_id}`
Edición en vivo: aplica un `$set` con los campos enviados. `_id` es inmutable
(se ignora si viene en `fields`).

**Body:**
```json
{ "fields": { "title": "Nuevo título", "duration": 200 } }
```

**Respuestas:** `200 → { "ok": true, "modified": 1 }` · `400` ID inválido · `404` colección desconocida.

### `DELETE /api/admin/documents/{collection}/{doc_id}`
Elimina un documento por `_id`.

**Respuestas:** `200 → { "ok": true, "deleted": 1 }` · `400` ID inválido · `404` no encontrado.

---

## Códigos de error

| Código | Significado |
|--------|-------------|
| `400` | Petición inválida (ID malformado, archivo no-CSV o vacío). |
| `404` | Recurso o colección no encontrada. |
| `422` | Error de validación de query params / body (rangos, tipos). |
| `500` | Error interno del servidor. |

Todos los errores retornan: `{ "detail": "Mensaje en español" }`.
