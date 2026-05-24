// src/pages/Users.jsx
import { useState, useEffect } from "react";
import ActivityHeatmap from "../components/users/ActivityHeatmap";
import ContentCompletionRanking from "../components/users/ContentCompletionRanking";

const Placeholder = ({ title }) => (
  <div
    style={{
      background: "var(--color-surface)",
      border: "1px solid var(--color-border)",
      borderRadius: "8px",
      padding: "48px",
      textAlign: "center",
      color: "var(--color-text-muted)",
    }}
  >
    {title} — pendiente
  </div>
);

export default function Users() {
  const [heatmap, setHeatmap] = useState(null);
  const [completion, setCompletion] = useState(null);

  useEffect(() => {
    fetch("/api/users/activity-heatmap")
      .then((r) => r.json())
      .then((d) => setHeatmap(d.activity));

    fetch("/api/users/content-completion-ranking?min_plays=1")
      .then((r) => r.json())
      .then((d) => setCompletion(d));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Perfiles de usuario */}
      <Placeholder title="Perfiles de usuario (Casual / Regular / Heavy)" />

      {/* Heatmap + Completion */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "16px",
        }}
      >
        <ActivityHeatmap data={heatmap} />
        <ContentCompletionRanking data={completion} />
      </div>

      {/* Funnel */}
      <Placeholder title="Funnel de retención" />
    </div>
  );
}
