export default function AlertsCounter({ total_red, total_yellow, total_blue }) {
  const counters = [
    {
      label: "Buffer Crítico",
      value: total_red,
      color: "var(--color-danger)",
      bg: "rgba(239,68,68,0.1)",
    },
    {
      label: "Re-buffering Alto",
      value: total_yellow,
      color: "var(--color-warning)",
      bg: "rgba(234,179,8,0.1)",
    },
    {
      label: "Pausas Excesivas",
      value: total_blue,
      color: "#60A5FA",
      bg: "rgba(96,165,250,0.1)",
    },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "16px",
      }}
    >
      {counters.map(({ label, value, color, bg }) => (
        <div
          key={label}
          style={{
            background: bg,
            border: `1px solid ${color}`,
            borderRadius: "8px",
            padding: "24px",
            textAlign: "center",
          }}
        >
          <div
            style={{
              fontSize: "48px",
              fontWeight: "700",
              color,
              lineHeight: 1,
            }}
          >
            {value ?? "—"}
          </div>
          <div
            style={{
              fontSize: "12px",
              color: "var(--color-text-muted)",
              marginTop: "8px",
              textTransform: "uppercase",
              letterSpacing: "0.5px",
            }}
          >
            {label}
          </div>
        </div>
      ))}
    </div>
  );
}
