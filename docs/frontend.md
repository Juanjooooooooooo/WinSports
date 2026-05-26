# Frontend

## Stack
- **Vite** — servidor de desarrollo y empaquetador
- **React 19** — framework de UI
- **Recharts** — gráficas (línea de tiempo, rankings)
- **Leaflet + react-leaflet** — mapa de usuarios

## Requisitos
- Node.js v18 o superior (probado en v26.1.0)

## Instalación
Desde la carpeta `frontend/`:
```bash
npm install
```

## Levantar en desarrollo
Se necesitan dos terminales simultáneas desde la raíz del proyecto:

**Terminal 1 — API:**
```bash
uv run uvicorn api.main:app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

El frontend corre en `http://localhost:5173`.
Las llamadas a `/api` se redirigen automáticamente a `http://localhost:8000`
via el proxy configurado en `vite.config.js` — no hay que configurar CORS manualmente.

## Variables de entorno
El frontend no tiene su propio `.env` — lee `API_BASE_URL` del `.env` de la raíz
del proyecto a través de `vite.config.js`. Si cambias el puerto de la API, solo
hay que actualizar ese valor.

## Estructura de `src/`
```
src/
├── components/
│   ├── overview/   KPICard · DeviceRanking · ActivityTimeline · ContentRanking · UsersMap
│   ├── qoe/        RebufferingRate · StartupTime · BufferByContent · EventRanking
│   ├── users/      UserProfiles · RetentionFunnel · ActivityHeatmap · ContentCompletionRanking
│   └── admin/      CollectionCounts · CsvUploader · DocumentTable
├── pages/          Overview.jsx · QoE.jsx · Users.jsx · Admin.jsx
├── layout/         SideBar · TopBar
├── styles/
│   └── theme.css   — CSS variables de los dos temas
├── test/
│   └── setup.jsx   — setup de Vitest (jsdom, mocks de react-leaflet y fetch)
├── App.jsx         — layout principal + navegación
├── main.jsx        — punto de entrada
└── index.css       — reset global + import del tema
```

Los tests de componentes viven junto a cada `*.jsx` como `*.test.jsx`.
Ver [testing](#testing) abajo.
## Temas
El dashboard tiene dos temas definidos en `src/styles/theme.css`:
- **brand** — naranja Win Sports `#FF6B00` sobre gris oscuro `#1A1A1A`
- **premium** — naranja más quemado `#E85D00` sobre casi negro `#111318`

Para cambiar el tema, modificar el atributo en `src/main.jsx`:
```js
document.documentElement.setAttribute('data-theme', 'brand') // o 'premium'
```

## Páginas
| Página   | Estado          |
|----------|-----------------|
| Overview | ✅ Listo        |
| QoE      | ✅ Listo        |
| Usuarios | ✅ Listo        |
| Alertas  | En construcción |
| Admin    | ✅ Listo        |

## Endpoints implementados

### Overview
| Endpoint                        | Método | Descripción                          |
|---------------------------------|--------|--------------------------------------|
| `/api/overview/unique-users`    | GET    | Total de suscriptores únicos         |
| `/api/overview/total-plays`     | GET    | Total de reproducciones (sesiones)   |
| `/api/overview/device-ranking`  | GET    | Sesiones agrupadas por dispositivo   |
| `/api/overview/activity-by-hour`| GET    | Sesiones agrupadas por hora del día  |
| `/api/overview/top-content`     | GET    | Contenidos más vistos (param `limit`)|
| `/api/overview/users-map`       | GET    | Puntos del mapa, uno por usuario activo (param `limit`) |

### Componentes Overview
| Componente          | Datos que consume                  | Estado     |
|---------------------|------------------------------------|------------|
| KPICard             | `unique-users`, `total-plays`, `top-content`, `device-ranking` | ✅ Listo |
| DeviceRanking       | `device-ranking`                   | ✅ Listo   |
| ActivityTimeline    | `activity-by-hour`                 | ✅ Listo   |
| ContentRanking      | `top-content`                      | ✅ Listo   |
| UsersMap            | `users-map` (Leaflet, burbujas)    | ✅ Listo   |

### QoE
| Endpoint                       | Método | Descripción                                       |
|--------------------------------|--------|---------------------------------------------------|
| `/api/qoe/buffer-by-content`   | GET    | Buffer promedio por contenido (param `limit`)     |
| `/api/qoe/rebuffering-rate`    | GET    | Tasa de re-buffering por eventos y por sesiones   |
| `/api/qoe/startup-time`        | GET    | Tiempo de inicialización (avg/max + distribución) |
| `/api/qoe/event-ranking`       | GET    | Ranking de tipos de evento por frecuencia         |

### Componentes QoE
| Componente        | Datos que consume        | Estado   |
|-------------------|--------------------------|----------|
| RebufferingRate   | `rebuffering-rate`       | ✅ Listo |
| StartupTime       | `startup-time`           | ✅ Listo |
| BufferByContent   | `buffer-by-content`      | ✅ Listo |
| EventRanking      | `event-ranking`          | ✅ Listo |

### Users
| Endpoint                                      | Método | Descripción                                    |
|-----------------------------------------------|--------|------------------------------------------------|
| `/api/users/retention-funnel`                 | GET    | Funnel de retención por hitos                  |
| `/api/users/activity-heatmap`                 | GET    | Sesiones por hora y día de semana              |
| `/api/users/content-completion-ranking`       | GET    | Ranking de contenidos por completion rate      |
| `/api/users/user-profiles`                    | GET    | Clasificación Casual / Regular / Heavy         |

Query params: `content-completion-ranking` acepta `min_plays` (default: 5)

Nota: `user-profiles` clasifica por **número de eventos** por usuario
(Vague / Mid / Heavy) y devuelve `count`, `total_events`, `avg_events` y `range`.

### Componentes Users
| Componente               | Datos que consume              | Estado    |
|--------------------------|-------------------------------|-----------|
| UserProfiles             | `user-profiles`               | ✅ Listo  |
| ActivityHeatmap          | `activity-heatmap`            | ✅ Listo  |
| ContentCompletionRanking | `content-completion-ranking`  | ✅ Listo  |
| RetentionFunnel          | `retention-funnel`            | ✅ Listo  |

### Admin

Panel de gestión de datos. Detalle completo en [`admin.md`](admin.md).

| Endpoint                                   | Método | Descripción                               |
|--------------------------------------------|--------|-------------------------------------------|
| `/api/admin/collections`                   | GET    | Conteo de documentos por colección        |
| `/api/admin/upload-csv`                    | POST   | Sube un CSV y re-construye las derivadas  |
| `/api/admin/documents/{collection}`        | GET    | Documentos paginados (`page`, `page_size`)|
| `/api/admin/documents/{collection}/{id}`   | PUT    | Edición en vivo (`$set` de campos)        |
| `/api/admin/documents/{collection}/{id}`   | DELETE | Borrar un documento                       |

| Componente        | Datos que consume                  | Estado   |
|-------------------|------------------------------------|----------|
| CollectionCounts  | `collections`                      | ✅ Listo |
| CsvUploader       | `upload-csv`                       | ✅ Listo |
| DocumentTable     | `documents` (+ PUT/DELETE)         | ✅ Listo |

## Testing

Runner: **Vitest** + **@testing-library/react** sobre **jsdom**.

```bash
cd frontend
npm run test         # corre toda la batería una vez
npm run test:watch   # modo watch
```

Setup global en `src/test/setup.jsx`: registra los matchers de `jest-dom`,
limpia el DOM entre tests, y mockea `react-leaflet` (jsdom no monta el mapa) y
`fetch`. Los tests se enfocan en los componentes presentacionales (estados de
carga / vacío / datos) y la navegación del shell.
