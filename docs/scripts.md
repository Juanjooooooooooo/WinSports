# Scripts

## load_csv.py
Carga un CSV de eventos Win Sports a la colección `events` en Atlas.
Solo inserta — nunca borra ni construye colecciones derivadas.

**Uso:**
```bash
uv run scripts/load_csv.py --file data/archivo.csv
```

**Qué hace:**
1. Configura la colección `events` (crea con validator + índices, o re-aplica el
   validator vía `collMod` si ya existe)
2. Lee el CSV con pandas
3. Parsea cada fila (casteo de tipos, NaN → None, fecha → datetime UTC; los
   enteros tipo `"2023.0"` se castean vía float)
4. Filtra filas sin date, subscriber_id, customer_id, type_event o device_type
   (los campos obligatorios del validator)
5. Inserta en batches de 1.000 documentos con ordered=False

**ordered=False:** si un documento falla la validación de Mongo,
el batch continúa en vez de detenerse. El conteo de insertados se toma del
resultado real de cada batch (incluyendo el `nInserted` de un BulkWriteError).

**Parseo compartido:** los casteos (`_to_int`, `_to_date`, `parse_row`, …) y la
inserción por batches viven en `db/csv_ingest.py`. `load_csv.py` los re-exporta,
y el endpoint `POST /api/admin/upload-csv` usa el mismo módulo — así el script y
el panel de admin procesan los CSVs de forma idéntica.

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
