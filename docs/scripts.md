# Scripts

## load_csv.py
Carga un CSV de eventos Win Sports a la colección `events` en Atlas.
Solo inserta — nunca borra ni construye colecciones derivadas.

**Uso:**
```bash
uv run scripts/load_csv.py --file data/archivo.csv
```

**Qué hace:**
1. Lee el CSV con pandas
2. Parsea cada fila (casteo de tipos, NaN → None, fecha → datetime UTC)
3. Filtra filas sin date, subscriber_id, customer_id o type_event
4. Inserta en batches de 1.000 documentos con ordered=False

**ordered=False:** si un documento falla la validación de Mongo,
el batch continúa en vez de detenerse.

---

## test_pipeline.py
Construye las colecciones derivadas (sessions y content_stats)
a partir de los eventos ya cargados en Atlas.

**Uso:**
```bash
# Construir sessions y content_stats
uv run scripts/test_pipeline.py

# Borrar todo y reconstruir desde cero
uv run scripts/test_pipeline.py --HARD
```

**--HARD:** borra sessions y content_stats antes de correr.
Útil para debugging cuando los datos están en un estado inconsistente.

**Qué hace:**
1. Setup de colecciones sessions y content_stats (crea si no existen, índices siempre)
2. Lee todos los events de Atlas
3. Agrupa por (subscriber_id, customer_id), parte en sub-sesiones por START
4. Hace upsert en sessions por clave única
5. Lee todas las sessions, agrega por customer_id
6. Hace upsert en content_stats por customer_id
7. Imprime conteo final de documentos en cada colección
