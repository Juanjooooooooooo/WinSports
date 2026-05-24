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
│   └── overview/
│       ├── KPICard.jsx          — tarjeta de métrica reutilizable
│       ├── DeviceRanking.jsx    — ranking de dispositivos
│       ├── ActivityTimeline.jsx — actividad por hora del día
│       ├── ContentRanking.jsx   — contenidos más vistos
│       └── UsersMap.jsx         — mapa de usuarios por país
├── pages/
│   └── Overview.jsx             — página principal del dashboard
├── styles/
│   └── theme.css                — CSS variables de los dos temas
├── App.jsx                      — layout principal + navegación
├── main.jsx                     — punto de entrada
└── index.css                    — reset global + import del tema
```
## Temas
El dashboard tiene dos temas definidos en `src/styles/theme.css`:
- **brand** — naranja Win Sports `#FF6B00` sobre gris oscuro `#1A1A1A`
- **premium** — naranja más quemado `#E85D00` sobre casi negro `#111318`

Para cambiar el tema, modificar el atributo en `src/main.jsx`:
```js
document.documentElement.setAttribute('data-theme', 'brand') // o 'premium'
```

## Páginas
| Página   | Estado         |
|----------|----------------|
| Overview | En desarrollo  |
| QoE      | En construcción|
| Usuarios | En desarrollo  |
| Alertas  | En construcción|
| Admin    | En construcción|

## Endpoints implementados

### Overview
| Endpoint                        | Método | Descripción                        |
|---------------------------------|--------|------------------------------------|
| `/api/overview/unique-users`    | GET    | Total de suscriptores únicos       |
| `/api/overview/device-ranking`  | GET    | Sesiones agrupadas por dispositivo |
| `/api/overview/activity-by-hour`| GET    | Sesiones agrupadas por hora del día|

### Componentes Overview
| Componente          | Datos que consume                  | Estado     |
|---------------------|------------------------------------|------------|
| KPICard             | `unique-users`, `device-ranking`   | ✅ Listo   |
| DeviceRanking       | `device-ranking`                   | ✅ Listo   |
| ActivityTimeline    | `activity-by-hour`                 | ✅ Listo   |
| ContentRanking      | Pendiente compañero                | ⏳ Pendiente|
| UsersMap            | Pendiente compañero                | ⏳ Pendiente|

### Users
| Endpoint                                      | Método | Descripción                                    |
|-----------------------------------------------|--------|------------------------------------------------|
| `/api/users/retention-funnel`                 | GET    | Funnel de retención por hitos                  |
| `/api/users/activity-heatmap`                 | GET    | Sesiones por hora y día de semana              |
| `/api/users/content-completion-ranking`       | GET    | Ranking de contenidos por completion rate      |
| `/api/users/user-profiles`                    | GET    | Clasificación Casual / Regular / Heavy         |

Query params: `content-completion-ranking` acepta `min_plays` (default: 5)

### Componentes Users
| Componente               | Datos que consume              | Estado       |
|--------------------------|-------------------------------|--------------|
| UserProfiles             | `user-profiles`               | ⏳ Pendiente  |
| ActivityHeatmap          | `activity-heatmap`            | ✅ Listo      |
| ContentCompletionRanking | `content-completion-ranking`  | ✅ Listo      |
| RetentionFunnel          | `retention-funnel`            | ⏳ Pendiente  |
