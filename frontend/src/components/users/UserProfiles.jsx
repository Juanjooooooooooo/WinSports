// src/components/users/UserProfiles.jsx

const PROFILE_META = {
  Heavy: { color: "var(--color-primary)", emoji: "🔥", label: "Heavy user" },
  Mid: { color: "var(--color-warning)", emoji: "⚡", label: "Mid user" },
  Vague: { color: "var(--color-text-muted)", emoji: "💤", label: "Vague user" },
};

export default function UserProfiles({ data }) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderRadius: "8px",
        padding: "24px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
          marginBottom: "20px",
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
          Perfiles de usuario
        </h3>
        {data && (
          <span style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>
            {data.total_users} usuarios · clasificados por nº de eventos
          </span>
        )}
      </div>

      {!data ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Cargando...
        </div>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "16px",
          }}
        >
          {data.profiles.map((p) => {
            const meta = PROFILE_META[p.profile] || {};
            const pct = data.total_users
              ? Math.round((p.count / data.total_users) * 100)
              : 0;
            return (
              <div
                key={p.profile}
                style={{
                  background: "var(--color-surface-2)",
                  border: "1px solid var(--color-border)",
                  borderTop: `3px solid ${meta.color}`,
                  borderRadius: "8px",
                  padding: "20px",
                }}
              >
                <div style={{ fontSize: "22px", marginBottom: "4px" }}>
                  {meta.emoji}
                </div>
                <div
                  style={{
                    fontSize: "13px",
                    color: "var(--color-text-muted)",
                    marginBottom: "8px",
                  }}
                >
                  {meta.label}
                </div>
                <div
                  style={{
                    fontSize: "30px",
                    fontWeight: "700",
                    color: "var(--color-text)",
                    lineHeight: 1,
                  }}
                >
                  {p.count.toLocaleString()}
                </div>
                <div
                  style={{
                    fontSize: "12px",
                    color: meta.color,
                    fontWeight: "600",
                    marginTop: "4px",
                  }}
                >
                  {pct}% de usuarios
                </div>
                <div
                  style={{
                    fontSize: "11px",
                    color: "var(--color-text-muted)",
                    marginTop: "10px",
                    lineHeight: 1.5,
                  }}
                >
                  {p.range}
                  <br />
                  prom. {p.avg_events} eventos/usuario
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
