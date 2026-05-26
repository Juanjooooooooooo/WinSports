# Panel de Administración

Pestaña **Admin** del dashboard. Pensada para que el equipo de Win Sports
gestione los datos sin tocar Mongo a mano: cargar nuevos CSVs, ver cuántos
documentos hay y editar/borrar documentos en vivo.

> ⚠️ **Sin autenticación todavía.** El panel asume que la API corre en una red
> interna. Antes de exponerlo a producción hay que ponerle auth (ver
> [Pendientes](#pendientes)).

---

## Componentes de la UI

`frontend/src/pages/Admin.jsx` orquesta tres bloques:

| Componente | Archivo | Qué hace |
|------------|---------|----------|
| `CollectionCounts` | `components/admin/CollectionCounts.jsx` | 4 tarjetas: total + conteo de `events`, `sessions`, `content_stats`. |
| `CsvUploader` | `components/admin/CsvUploader.jsx` | Sube un `.csv`, muestra el resumen de la carga. |
| `DocumentTable` | `components/admin/DocumentTable.jsx` | Tabla paginada con edición y borrado por fila. |

---

## 1. Cargar un CSV nuevo

1. Click en **"Cargar nuevo CSV de eventos"** → elegir un `.csv`.
2. **Subir y procesar**. El backend:
   - asegura la colección `events` (validator + índices),
   - parsea y filtra las filas (mismos casteos que `scripts/load_csv.py`, vía
     `db/csv_ingest.py`),
   - inserta en batches,
   - **re-construye** `sessions` y `content_stats`.
3. Al terminar muestra: insertados, omitidos, total en `events`, y cuántas
   sesiones y content_stats quedaron. El dashboard se refresca solo.

**Endpoint:** `POST /api/admin/upload-csv` (multipart, campo `file`).

> El CSV debe traer las columnas originales del dataset (`Date`, `SubscriberID`,
> `CustomerId`, `TypeEvent`, `DeviceType`, …). Las filas sin alguno de los campos
> obligatorios se omiten (cuentan en `rows_skipped`).

---

## 2. Conteo de documentos

Las tarjetas superiores leen `GET /api/admin/collections` y muestran el total y
el desglose por colección. Se refrescan tras cada carga, edición o borrado.

---

## 3. Editar / borrar en vivo

En la tabla:

- **Selector de colección** (`events` / `sessions` / `content_stats`) y paginación
  (25 por página).
- **Editar** convierte los campos escalares de la fila en inputs. Al **Guardar**
  solo se envían los campos que cambiaron (`PUT …/documents/{col}/{id}`).
- **Eliminar** pide confirmación y borra el documento (`DELETE …`).

### Preservación de tipos

Al editar, el front castea el texto de vuelta al tipo original del campo
(número → número, booleano → booleano) antes de mandarlo. Así un `duration`
sigue siendo entero y no se convierte en string.

### Caveats

- **`_id` es de solo lectura** (inmutable).
- **Campos anidados (objetos/arrays)** se muestran como JSON pero no son editables
  desde la tabla.
- **Fechas**: se editan como texto ISO. Como el validator de Mongo está en
  `warn`, un valor mal formado no bloquea el guardado pero puede dejar el campo
  como string — editar fechas con cuidado.
- Editar una colección **derivada** (`sessions`, `content_stats`) es un cambio
  manual: una nueva carga de CSV la re-construye y sobreescribe. Para cambios
  permanentes, editar `events` y volver a procesar.

---

## Pendientes

- **Autenticación / autorización** del panel (hoy abierto).
- Edición de campos anidados y de fechas con un date-picker tipado.
- Búsqueda/filtro dentro de la tabla (hoy solo paginación secuencial).
