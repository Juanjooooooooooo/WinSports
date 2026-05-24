// src/components/users/ContentCompletionRanking.jsx

const Bar = ({ value, max }) => (
  <div
    style={{
      height: "6px",
      background: "var(--color-surface-2)",
      borderRadius: "3px",
      marginTop: "4px",
      overflow: "hidden",
    }}
  >
    <div
      style={{
        height: "100%",
        width: `${(value / max) * 100}%`,
        background: value > 50 ? "var(--color-primary)" : "var(--color-danger)",
        borderRadius: "3px",
        transition: "width 0.4s ease",
      }}
    />
  </div>
);

export default function ContentCompletionRanking({ data }) {
  if (!data)
    return (
      <div
        style={{
          background: "var(--color-surface)",
          border: "1px solid var(--color-border)",
          borderRadius: "8px",
          padding: "24px",
          color: "var(--color-text-muted)",
          textAlign: "center",
        }}
      >
        Cargando...
      </div>
    );

  const allItems = [
    ...(data.most_completed || []),
    ...(data.most_abandoned || []),
  ];
  const maxPlays = Math.max(...allItems.map((d) => d.total_plays), 1);

  const renderList = (items, label) => (
    <div style={{ flex: 1 }}>
      <div
        style={{
          fontSize: "11px",
          color: "var(--color-text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.5px",
          marginBottom: "12px",
        }}
      >
        {label}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {items.length === 0 ? (
          <span style={{ color: "var(--color-text-muted)", fontSize: "13px" }}>
            Sin datos suficientes
          </span>
        ) : (
          items.map((item, i) => (
            <div key={i}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "baseline",
                }}
              >
                <span
                  style={{
                    fontSize: "12px",
                    color: "var(--color-text)",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    maxWidth: "70%",
                  }}
                >
                  {item.title}
                </span>
                <span
                  style={{
                    fontSize: "12px",
                    fontWeight: "600",
                    color:
                      item.completion_rate > 50
                        ? "var(--color-primary)"
                        : "var(--color-danger)",
                  }}
                >
                  {item.completion_rate}%
                </span>
              </div>
              <Bar value={item.completion_rate} max={100} />
              <div
                style={{
                  fontSize: "10px",
                  color: "var(--color-text-muted)",
                  marginTop: "2px",
                }}
              >
                {item.total_plays} reproducciones
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );

  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "8px",
        padding: "24px",
      }}
    >
      <h3
        style={{
          fontSize: "12px",
          color: "var(--color-text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.5px",
          marginBottom: "20px",
        }}
      >
        Completion por contenido
      </h3>

      <div style={{ display: "flex", gap: "24px" }}>
        {renderList(data.most_completed, "✅ Más completados")}
        <div style={{ width: "1px", background: "var(--color-border)" }} />
        {renderList(data.most_abandoned, "❌ Más abandonados")}
      </div>
    </div>
  );
}
