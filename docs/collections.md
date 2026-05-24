# Colecciones

## events
Fuente de verdad. Un documento por evento del CSV. No se modifica post-inserción.

**Campos obligatorios:** date, subscriber_id, customer_id, type_event, device_type

**Campos opcionales destacados:**
- `buffer_time` — solo presente en START-BUFFERING y RE-BUFFERING
- `episode`, `season` — solo en contenido tipo EPISODE
- `position` — posición de reproducción en segundos

**Índices:**
- `(subscriber_id, customer_id, date)` — reconstrucción de sesiones
- `(date DESC)` — queries por ventana de tiempo (alertas)
- `(type_event, date DESC)` — filtros de QoE
- `(customer_id, type_event)` — rankings de contenido
- `(device_type)` — breakdown por plataforma

---

## sessions
Derivada de events. Una sesión = todos los eventos de un
(subscriber_id + customer_id) entre un START y el siguiente START.

**Clave única:** subscriber_id + customer_id + start_time

**Campos de progreso:**
- `reached_firstquartile/midpoint/thirdquartile/complete` — booleanos del funnel
- `completion_pct` — max_position / duration * 100
- `max_position` — posición máxima alcanzada en segundos

**Campos de calidad (QoE):**
- `total_buffer_time` — suma de buffer_time de todos los eventos de la sesión
- `rebuffer_count` — número de eventos RE-BUFFERING
- `pause_count` — número de eventos PAUSE

**Índices:**
- `(subscriber_id)` — perfil de usuario, usuarios únicos
- `(customer_id)` — queries por contenido
- `(device_type)` — ranking de dispositivos
- `(start_time DESC, total_buffer_time DESC)` — alertas
- `(customer_id, reached_complete)` — funnel de retención
- `(subscriber_id, customer_id, start_time)` UNIQUE — clave de upsert

---

## content_stats
Derivada de sessions. Un documento por customer_id (pieza de contenido).

**Clave única:** customer_id

**Nota importante:** customer_id representa una pieza de contenido específica
(un episodio, una película, un partido), no un show completo.
Para métricas por serie, agrupar por series_title en el repositorio.

**Métricas de volumen:**
- `total_plays` — número de sesiones
- `unique_viewers` — subscriber_ids distintos

**Funnel de retención (% de sesiones que llegaron a cada hito):**
- `firstquartile_rate`, `midpoint_rate`, `thirdquartile_rate`, `completion_rate`

**Métricas de calidad:**
- `avg_buffer_time` — promedio de total_buffer_time por sesión
- `rebuffer_rate` — % de sesiones con al menos 1 RE-BUFFERING
- `avg_completion_pct` — promedio del % de contenido visto

**Breakdown:**
- `plays_by_device` — `{ANDR: N, IOS: N, WEB: N}`
