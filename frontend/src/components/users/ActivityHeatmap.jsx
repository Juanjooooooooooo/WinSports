// src/components/users/ActivityHeatmap.jsx

const DAYS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

export default function ActivityHeatmap({ data }) {
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

  // Máximo para normalizar el color
  const maxSessions = Math.max(...data.map((d) => d.sessions), 1);

  const getColor = (sessions) => {
    if (sessions === 0) return "var(--color-surface-2)";
    const intensity = sessions / maxSessions;
    const alpha = 0.2 + intensity * 0.8;
    return `rgba(255, 107, 0, ${alpha})`;
  };

  // Organizar en grilla weekday×hour
  const grid = {};
  data.forEach(({ weekday, hour, sessions }) => {
    if (!grid[weekday]) grid[weekday] = {};
    grid[weekday][hour] = sessions;
  });

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
        Actividad por hora y día
      </h3>

      <div style={{ overflowX: "auto" }}>
        {/* Header horas */}
        <div
          style={{ display: "flex", marginLeft: "36px", marginBottom: "4px" }}
        >
          {Array.from({ length: 24 }, (_, h) => (
            <div
              key={h}
              style={{
                width: "20px",
                fontSize: "9px",
                color: "var(--color-text-muted)",
                textAlign: "center",
                flexShrink: 0,
              }}
            >
              {h % 6 === 0 ? `${h}h` : ""}
            </div>
          ))}
        </div>

        {/* Filas por día */}
        {Array.from({ length: 7 }, (_, i) => {
          const weekday = i + 1; // Mongo: 1=domingo
          return (
            <div
              key={weekday}
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "3px",
              }}
            >
              <div
                style={{
                  width: "32px",
                  fontSize: "10px",
                  color: "var(--color-text-muted)",
                  flexShrink: 0,
                }}
              >
                {DAYS[i]}
              </div>
              {Array.from({ length: 24 }, (_, hour) => {
                const sessions = grid[weekday]?.[hour] ?? 0;
                return (
                  <div
                    key={hour}
                    title={`${DAYS[i]} ${hour}h — ${sessions} sesiones`}
                    style={{
                      width: "18px",
                      height: "18px",
                      borderRadius: "3px",
                      background: getColor(sessions),
                      marginRight: "2px",
                      flexShrink: 0,
                      cursor: sessions > 0 ? "pointer" : "default",
                    }}
                  />
                );
              })}
            </div>
          );
        })}
      </div>

      {/* Leyenda */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginTop: "12px",
          justifyContent: "flex-end",
        }}
      >
        <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
          Menos
        </span>
        {[0.1, 0.3, 0.5, 0.7, 1].map((intensity) => (
          <div
            key={intensity}
            style={{
              width: "14px",
              height: "14px",
              borderRadius: "2px",
              background: `rgba(255, 107, 0, ${0.2 + intensity * 0.8})`,
            }}
          />
        ))}
        <span style={{ fontSize: "10px", color: "var(--color-text-muted)" }}>
          Más
        </span>
      </div>
    </div>
  );
}
