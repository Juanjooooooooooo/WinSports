// src/components/users/RetentionFunnel.jsx

export default function RetentionFunnel({ data }) {
  const stages = data
    ? [
        { label: "Inicio (START)", value: data.total },
        { label: "25% — Primer cuartil", value: data.firstquartile },
        { label: "50% — Mitad", value: data.midpoint },
        { label: "75% — Tercer cuartil", value: data.thirdquartile },
        { label: "100% — Completo", value: data.complete },
      ]
    : [];

  const max = data?.total || 1;

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
        Funnel de retención
      </h3>

      {!data ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Cargando...
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          {stages.map((stage, i) => {
            const pct = max ? (stage.value / max) * 100 : 0;
            return (
              <div key={i}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "baseline",
                    marginBottom: "4px",
                  }}
                >
                  <span style={{ fontSize: "12px", color: "var(--color-text)" }}>
                    {stage.label}
                  </span>
                  <span
                    style={{
                      fontSize: "12px",
                      color: "var(--color-text-muted)",
                    }}
                  >
                    {stage.value.toLocaleString()} ({pct.toFixed(1)}%)
                  </span>
                </div>
                <div
                  style={{
                    height: "28px",
                    background: "var(--color-surface-2)",
                    borderRadius: "4px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${Math.max(pct, 1)}%`,
                      background: `linear-gradient(90deg, var(--color-primary), var(--color-primary-dim))`,
                      borderRadius: "4px",
                      transition: "width 0.4s ease",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
