// src/components/overview/DeviceRanking.jsx
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const DEVICE_COLORS = {
  WEB: "var(--color-primary)",
  IOS: "#888888",
  ANDR: "#555555",
};

export default function DeviceRanking({ data }) {
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
        Dispositivos
      </h3>

      {!data ? (
        <div
          style={{
            color: "var(--color-text-muted)",
            textAlign: "center",
            padding: "24px",
          }}
        >
          Cargando...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ left: 8, right: 24 }}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="device"
              tick={{ fill: "var(--color-text-muted)", fontSize: 13 }}
              axisLine={false}
              tickLine={false}
              width={48}
            />
            <Tooltip
              cursor={{ fill: "var(--color-surface-2)" }}
              contentStyle={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "6px",
                color: "var(--color-text)",
              }}
              formatter={(value) => [value, "Sesiones"]}
            />
            <Bar dataKey="sessions" radius={[0, 4, 4, 0]}>
              {data.map((entry) => (
                <Cell
                  key={entry.device}
                  fill={DEVICE_COLORS[entry.device] || "var(--color-primary)"}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
