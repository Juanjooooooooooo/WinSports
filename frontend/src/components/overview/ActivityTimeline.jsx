// src/components/overview/ActivityTimeline.jsx
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const formatHour = (hour) => {
  if (hour === 0) return "12am";
  if (hour === 12) return "12pm";
  return hour < 12 ? `${hour}am` : `${hour - 12}pm`;
};

export default function ActivityTimeline({ data }) {
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
        Actividad por hora
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
          <AreaChart data={data} margin={{ left: -16, right: 8 }}>
            <defs>
              <linearGradient id="activityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF5500" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#FF5500" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="hour"
              tickFormatter={formatHour}
              tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              interval={3}
            />
            <YAxis
              allowDecimals={false}
              tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "var(--color-surface)",
                border: "1px solid var(--color-border)",
                borderRadius: "6px",
                color: "var(--color-text)",
              }}
              labelFormatter={formatHour}
              formatter={(value) => [value, "Sesiones"]}
            />
            <Area
              type="monotone"
              dataKey="sessions"
              stroke="#FF5500"
              strokeWidth={2}
              fill="url(#activityGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
