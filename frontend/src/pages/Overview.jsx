// src/pages/Overview.jsx
import { useState, useEffect } from "react";
import KPICard from "../components/overview/KPICard";
import DeviceRanking from "../components/overview/DeviceRanking";
import ActivityTimeline from "../components/overview/ActivityTimeline";
import ContentRanking from "../components/overview/ContentRanking";
import UsersMap from "../components/overview/UsersMap";

export default function Overview() {
  const [uniqueUsers, setUniqueUsers] = useState(null);
  const [totalPlays, setTotalPlays] = useState(null);
  const [deviceRanking, setDeviceRanking] = useState(null);
  const [activityByHour, setActivityByHour] = useState(null);
  const [topContent, setTopContent] = useState(null);

  useEffect(() => {
    fetch("/api/overview/unique-users")
      .then((r) => r.json())
      .then((d) => setUniqueUsers(d.total));

    fetch("/api/overview/total-plays")
      .then((r) => r.json())
      .then((d) => setTotalPlays(d.total));

    fetch("/api/overview/device-ranking")
      .then((r) => r.json())
      .then((d) => setDeviceRanking(d.devices));

    fetch("/api/overview/activity-by-hour")
      .then((r) => r.json())
      .then((d) => setActivityByHour(d.activity));

    fetch("/api/overview/top-content?limit=8")
      .then((r) => r.json())
      .then((d) => setTopContent(d.content));
  }, []);

  const deviceLider = deviceRanking?.[0]?.device ?? null;
  const contenidoTop = topContent?.[0]?.title ?? null;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* KPIs */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "16px",
        }}
      >
        <KPICard
          title="Total Reproducciones"
          value={totalPlays?.toLocaleString() ?? null}
          subtitle="sesiones de reproducción"
        />
        <KPICard
          title="Usuarios Únicos"
          value={uniqueUsers}
          subtitle="suscriptores distintos"
        />
        <KPICard
          title="Contenido Más Visto"
          value={
            contenidoTop ? (
              <span style={{ fontSize: "18px" }}>{contenidoTop}</span>
            ) : null
          }
          subtitle={
            topContent?.[0] ? `${topContent[0].total_plays} reproducciones` : null
          }
        />
        <KPICard
          title="Dispositivo Líder"
          value={deviceLider}
          subtitle={
            deviceRanking ? `${deviceRanking[0]?.sessions} sesiones` : null
          }
        />
      </div>

      {/* Mapa + Device Ranking */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "16px",
        }}
      >
        <UsersMap />
        <DeviceRanking data={deviceRanking} />
      </div>

      {/* Timeline + Content Ranking */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
        }}
      >
        <ActivityTimeline data={activityByHour} />
        <ContentRanking data={topContent} />
      </div>
    </div>
  );
}
