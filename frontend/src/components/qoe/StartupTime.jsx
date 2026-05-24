// src/components/qoe/StartupTime.jsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function StartupTime({ data }) {
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
        Tiempo de inicialización
      </h3>

      {!data ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center" }}>
          Cargando...
        </div>
      ) : (
        <>
          <div style={{ display: "flex", gap: "32px", marginBottom: "20px" }}>
            <div>
              <div
                style={{
                  fontSize: "32px",
                  fontWeight: "700",
                  color: "var(--color-primary)",
                  lineHeight: 1,
                }}
              >
                {data.avg_seconds}s
              </div>
              <div
                style={{
                  fontSize: "11px",
                  color: "var(--color-text-muted)",
                  marginTop: "6px",
                }}
              >
                promedio (startup buffer)
              </div>
            </div>
            <div>
              <div
                style={{
                  fontSize: "32px",
                  fontWeight: "700",
                  color: "var(--color-text)",
                  lineHeight: 1,
                }}
              >
                {data.max_seconds}s
              </div>
              <div
                style={{
                  fontSize: "11px",
                  color: "var(--color-text-muted)",
                  marginTop: "6px",
                }}
              >
                máximo · {data.count.toLocaleString()} arranques
              </div>
            </div>
          </div>

          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={data.buckets} margin={{ left: -16, right: 8 }}>
              <XAxis
                dataKey="bucket"
                tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                allowDecimals={false}
                tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                cursor={{ fill: "var(--color-surface-2)" }}
                contentStyle={{
                  background: "var(--color-surface)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "6px",
                  color: "var(--color-text)",
                }}
                formatter={(value) => [value, "Arranques"]}
              />
              <Bar
                dataKey="count"
                fill="var(--color-primary)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}
