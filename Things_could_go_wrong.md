# Riesgos y cosas que podrían salir mal

## Resueltos

1. **Duplicados en `sessions`** — la clave es `subscriber_id + customer_id + start_time`.
   Blindado con el índice único `idx_sessions_unique_key` (`db/indexes/sessions.py`)
   y todos los escritos van por `update_one(... upsert=True)` usando esa misma
   clave (batch en `db/pipelines/sessions.py` y change stream en
   `db/collections/sessions.py`). Un re-procesamiento actualiza la sesión en vez
   de duplicarla.

2. **Memoria en los `find` a Mongo** — ningún repositorio trae documentos
   completos: el pipeline de sesiones proyecta solo los campos necesarios
   (`db/pipelines/sessions.py`) y los repos de la API (`overview`, `qoe`,
   `users`) resuelven todo con agregaciones `$group`/`$project` o `count_documents`,
   que agregan del lado del servidor.

## Abierto / a vigilar

- `get_unique_users` usa `distinct("subscriber_id")`. Sirve de sobra al volumen
  actual, pero `distinct` tiene tope de 16 MB de BSON; si el nº de suscriptores
  crece mucho, cambiar a `$group` + `$count`.
- El bundle del frontend pesa > 500 kB (leaflet + recharts). Solo un warning de
  build por ahora; si molesta, code-splitting con `import()` dinámico del mapa.
