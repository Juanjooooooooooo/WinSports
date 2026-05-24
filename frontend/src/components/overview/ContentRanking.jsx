export default function ContentRanking({ data }) {
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
          fontSize: "14px",
          color: "var(--color-text-muted)",
          marginBottom: "16px",
        }}
      >
        CONTENIDO MÁS VISTO
      </h3>
      <div
        style={{
          color: "var(--color-text-muted)",
          textAlign: "center",
          padding: "24px",
        }}
      >
        Placeholder — Top contenidos
      </div>
    </div>
  );
}
