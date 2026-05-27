const SEVERITY_META = {
  red: {
    color: "var(--color-danger)",
    label: "CRÍTICA",
    bg: "rgba(239,68,68,0.1)",
  },
  yellow: {
    color: "var(--color-warning)",
    label: "ALERTA",
    bg: "rgba(234,179,8,0.1)",
  },
  blue: { color: "#60A5FA", label: "INFO", bg: "rgba(96,165,250,0.1)" },
};

const formatTime = (ts) => {
  const d = new Date(ts);
  return d.toLocaleTimeString("es-CO", { hour: "2-digit", minute: "2-digit" });
};

export default function AlertsTable({ alerts }) {
  if (!alerts)
    return (
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "8px",
          padding: "48px",
          textAlign: "center",
          color: "var(--color-text-muted)",
        }}
      >
        Cargando...
      </div>
    );

  if (alerts.length === 0)
    return (
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "8px",
          padding: "48px",
          textAlign: "center",
          color: "var(--color-text-muted)",
        }}
      >
        ✅ Sin alertas activas en la última hora
      </div>
    );

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "8px",
        overflow: "hidden",
      }}
    >
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--color-border)" }}>
            {["Severidad", "Tipo", "Descripción", "Dispositivo", "Hora"].map(
              (h) => (
                <th
                  key={h}
                  style={{
                    padding: "12px 16px",
                    textAlign: "left",
                    fontSize: "11px",
                    color: "var(--color-text-muted)",
                    textTransform: "uppercase",
                    letterSpacing: "0.5px",
                    fontWeight: "600",
                  }}
                >
                  {h}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert, i) => {
            const meta = SEVERITY_META[alert.severity];
            return (
              <tr
                key={i}
                style={{
                  borderBottom: "1px solid var(--color-border)",
                  background:
                    i % 2 === 0 ? "transparent" : "var(--color-surface-2)",
                }}
              >
                <td style={{ padding: "12px 16px" }}>
                  <span
                    style={{
                      background: meta.bg,
                      color: meta.color,
                      border: `1px solid ${meta.color}`,
                      borderRadius: "4px",
                      padding: "2px 8px",
                      fontSize: "11px",
                      fontWeight: "600",
                    }}
                  >
                    {meta.label}
                  </span>
                </td>
                <td
                  style={{
                    padding: "12px 16px",
                    fontSize: "12px",
                    color: "var(--color-text-muted)",
                  }}
                >
                  {alert.type}
                </td>
                <td
                  style={{
                    padding: "12px 16px",
                    fontSize: "13px",
                    color: "var(--color-text)",
                  }}
                >
                  {alert.description}
                </td>
                <td
                  style={{
                    padding: "12px 16px",
                    fontSize: "12px",
                    color: "var(--color-text-muted)",
                  }}
                >
                  {alert.device_type || "—"}
                </td>
                <td
                  style={{
                    padding: "12px 16px",
                    fontSize: "12px",
                    color: "var(--color-text-muted)",
                  }}
                >
                  {formatTime(alert.timestamp)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
