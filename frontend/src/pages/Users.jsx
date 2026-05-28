// src/pages/Users.jsx
import { useState, useEffect } from "react";
import ActivityHeatmap from "../components/users/ActivityHeatmap";
import ContentCompletionRanking from "../components/users/ContentCompletionRanking";
import UserProfiles from "../components/users/UserProfiles";
import RetentionFunnel from "../components/users/RetentionFunnel";

export default function Users() {
  const [heatmap, setHeatmap] = useState(null);
  const [completion, setCompletion] = useState(null);
  const [profiles, setProfiles] = useState(null);
  const [funnel, setFunnel] = useState(null);

  useEffect(() => {
    fetch("/api/users/activity-heatmap")
      .then((r) => r.json())
      .then((d) => setHeatmap(d.activity));

    fetch("/api/users/content-completion-ranking")
      .then((r) => r.json())
      .then((d) => setCompletion(d));

    fetch("/api/users/user-profiles")
      .then((r) => r.json())
      .then(setProfiles);

    fetch("/api/users/retention-funnel")
      .then((r) => r.json())
      .then(setFunnel);
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Perfiles de usuario */}
      <UserProfiles data={profiles} />

      {/* Funnel de retención */}
      <RetentionFunnel data={funnel} />

      {/* Heatmap + Completion */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 3fr",
          gap: "16px",
        }}
      >
        <ActivityHeatmap data={heatmap} />
        <ContentCompletionRanking data={completion} />
      </div>
    </div>
  );
}
