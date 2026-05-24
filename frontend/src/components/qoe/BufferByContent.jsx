// src/components/qoe/BufferByContent.jsx

export default function BufferByContent({ data }) {
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
        Buffer promedio por contenido
      </h3>

      {!data ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Cargando...
        </div>
      ) : data.length === 0 ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Sin buffering registrado
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          {data.map((item, i) => {
            const max = Math.max(...data.map((d) => d.avg_buffer_time), 1);
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
                  <span
                    style={{
                      fontSize: "13px",
                      color: "var(--color-text)",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      maxWidth: "65%",
                    }}
                  >
                    {item.title || "—"}
                  </span>
                  <span
                    style={{
                      fontSize: "13px",
                      fontWeight: "600",
                      color: "var(--color-warning)",
                    }}
                  >
                    {item.avg_buffer_time}s
                  </span>
                </div>
                <div
                  style={{
                    height: "6px",
                    background: "var(--color-surface-2)",
                    borderRadius: "3px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      height: "100%",
                      width: `${(item.avg_buffer_time / max) * 100}%`,
                      background: "var(--color-warning)",
                      borderRadius: "3px",
                    }}
                  />
                </div>
                <div
                  style={{
                    fontSize: "10px",
                    color: "var(--color-text-muted)",
                    marginTop: "2px",
                  }}
                >
                  {item.total_plays} reproducciones · rebuffer {item.rebuffer_rate}%
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
