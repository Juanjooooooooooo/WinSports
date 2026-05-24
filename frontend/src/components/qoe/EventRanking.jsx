// src/components/qoe/EventRanking.jsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

// Eventos de calidad se resaltan en otro color
const QOE_EVENTS = new Set(["RE-BUFFERING", "START-BUFFERING", "PAUSE"]);

export default function EventRanking({ data }) {
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
        Ranking de eventos
      </h3>

      {!data ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Cargando...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={Math.max(data.length * 30, 120)}>
          <BarChart data={data} layout="vertical" margin={{ left: 40, right: 24 }}>
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="type_event"
              tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={120}
            />
            <Tooltip
              cursor={{ fill: "var(--color-surface-2)" }}
              contentStyle={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "6px",
                color: "var(--color-text)",
              }}
              formatter={(value) => [value.toLocaleString(), "Eventos"]}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {data.map((entry) => (
                <Cell
                  key={entry.type_event}
                  fill={
                    QOE_EVENTS.has(entry.type_event)
                      ? "var(--color-warning)"
                      : "var(--color-primary)"
                  }
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
