// src/components/overview/UsersMap.jsx
import { useState, useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Una burbuja por usuario activo. El radio escala con el nº de sesiones.
export default function UsersMap() {
  const [points, setPoints] = useState(null);

  useEffect(() => {
    fetch("/api/overview/users-map")
      .then((r) => r.json())
      .then((d) => setPoints(d.points))
      .catch(() => setPoints([]));
  }, []);

  const maxSessions = points?.length
    ? Math.max(...points.map((p) => p.sessions), 1)
    : 1;

  const radiusFor = (sessions) => 4 + (sessions / maxSessions) * 18;

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "8px",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          marginBottom: "16px",
        }}
      >
        <h3
          style={{
            fontSize: "12px",
            color: "var(--color-text-muted)",
            textTransform: "uppercase",
            letterSpacing: "0.5px",
          }}
        >
          Usuarios activos
        </h3>
        {points && (
          <span style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>
            {points.length} usuarios · burbuja = nº de sesiones
          </span>
        )}
      </div>

      {!points ? (
        <div
          style={{
            height: "360px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "var(--color-text-muted)",
          }}
        >
          Cargando mapa...
        </div>
      ) : (
        <div
          style={{
            height: "360px",
            borderRadius: "6px",
            overflow: "hidden",
          }}
        >
          <MapContainer
            center={[12, -55]}
            zoom={3}
            minZoom={2}
            scrollWheelZoom={false}
            style={{ height: "100%", width: "100%", background: "#0a0a0a" }}
          >
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {points.map((p, i) => (
              <CircleMarker
                key={`${p.subscriber_id}-${i}`}
                center={[p.lat, p.lon]}
                radius={radiusFor(p.sessions)}
                pathOptions={{
                  color: "#FF5500",
                  fillColor: "#FF5500",
                  fillOpacity: 0.45,
                  weight: 1,
                }}
              >
                <Tooltip direction="top" opacity={0.95}>
                  <div style={{ fontSize: "12px", lineHeight: 1.4 }}>
                    <strong>{p.subscriber_id}…</strong> ({p.country_code})
                    <br />
                    {p.sessions} sesiones
                    <br />
                    {p.total_buffer_time}s buffer total
                  </div>
                </Tooltip>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      )}
    </div>
  );
}
