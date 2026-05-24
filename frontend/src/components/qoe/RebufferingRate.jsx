// src/components/qoe/RebufferingRate.jsx

const Gauge = ({ label, pct, detail }) => (
  <div style={{ flex: 1 }}>
    <div
      style={{
        fontSize: "11px",
        color: "var(--color-text-muted)",
        textTransform: "uppercase",
        letterSpacing: "0.5px",
        marginBottom: "8px",
      }}
    >
      {label}
    </div>
    <div
      style={{
        fontSize: "32px",
        fontWeight: "700",
        color: pct > 10 ? "var(--color-danger)" : "var(--color-primary)",
        lineHeight: 1,
      }}
    >
      {pct}%
    </div>
    <div
      style={{
        height: "6px",
        background: "var(--color-surface-2)",
        borderRadius: "3px",
        marginTop: "10px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${Math.min(pct, 100)}%`,
          background: pct > 10 ? "var(--color-danger)" : "var(--color-primary)",
          borderRadius: "3px",
        }}
      />
    </div>
    <div
      style={{
        fontSize: "11px",
        color: "var(--color-text-muted)",
        marginTop: "8px",
      }}
    >
      {detail}
    </div>
  </div>
);

export default function RebufferingRate({ data }) {
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
        Tasa de re-buffering
      </h3>

      {!data ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Cargando...
        </div>
      ) : (
        <div style={{ display: "flex", gap: "24px" }}>
          <Gauge
            label="Por eventos"
            pct={data.event_rate}
            detail={`${data.rebuffer_events.toLocaleString()} / ${data.total_events.toLocaleString()} eventos`}
          />
          <div style={{ width: "1px", background: "var(--color-border)" }} />
          <Gauge
            label="Por sesiones"
            pct={data.session_rate}
            detail={`${data.rebuffer_sessions.toLocaleString()} / ${data.total_sessions.toLocaleString()} sesiones`}
          />
        </div>
      )}
    </div>
  );
}
