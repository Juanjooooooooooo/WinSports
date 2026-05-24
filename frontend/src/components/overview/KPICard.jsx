// src/components/overview/KPICard.jsx

export default function KPICard({ title, value, subtitle, color }) {
  return (
    <div
      style={{
        background: "var(--color-surface)",
        border: "1px solid var(--color-border)",
        borderTop: `3px solid ${color || "var(--color-primary)"}`,
        borderRadius: "8px",
        padding: "24px",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
      }}
    >
      <span
        style={{
          fontSize: "12px",
          color: "var(--color-text-muted)",
          textTransform: "uppercase",
          letterSpacing: "0.5px",
        }}
      >
        {title}
      </span>
      <span
        style={{
          fontSize: "32px",
          fontWeight: "700",
          color: "var(--color-text)",
          lineHeight: 1,
        }}
      >
        {value ?? "—"}
      </span>
      {subtitle && (
        <span style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>
          {subtitle}
        </span>
      )}
    </div>
  );
}
