import { useState, useEffect, useCallback } from "react";
import AlertsCounter from "../components/alerts/AlertsCounter";
import AlertsTable from "../components/alerts/AlertsTable";

export default function Alerts() {
  const [data, setData] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchAlerts = useCallback(() => {
    fetch("/api/alerts/")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setLastUpdate(new Date());
      });
  }, []);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30_000);
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Header con último update */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <p style={{ fontSize: "13px", color: "var(--color-text-muted)" }}>
          Monitoreo en tiempo real — ventana de 1 hora
        </p>
        {lastUpdate && (
          <span style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>
            Última actualización: {lastUpdate.toLocaleTimeString("es-CO")}
          </span>
        )}
      </div>

      {/* Contadores */}
      <AlertsCounter
        total_red={data?.total_red}
        total_yellow={data?.total_yellow}
        total_blue={data?.total_blue}
      />

      {/* Tabla */}
      <AlertsTable alerts={data?.alerts} />
    </div>
  );
}
