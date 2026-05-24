// src/pages/Overview.jsx
import { useState, useEffect } from "react";
import KPICard from "../components/overview/KPICard";
import DeviceRanking from "../components/overview/DeviceRanking";
import ActivityTimeline from "../components/overview/ActivityTimeline";
import ContentRanking from "../components/overview/ContentRanking";
import UsersMap from "../components/overview/UsersMap";

export default function Overview() {
  const [uniqueUsers, setUniqueUsers] = useState(null);
  const [deviceRanking, setDeviceRanking] = useState(null);
  const [activityByHour, setActivityByHour] = useState(null);

  useEffect(() => {
    fetch("/api/overview/unique-users")
      .then((r) => r.json())
      .then((d) => setUniqueUsers(d.total));

    fetch("/api/overview/device-ranking")
      .then((r) => r.json())
      .then((d) => setDeviceRanking(d.devices));

    fetch("/api/overview/activity-by-hour")
      .then((r) => r.json())
      .then((d) => setActivityByHour(d.activity));
  }, []);

  const deviceLider = deviceRanking?.[0]?.device ?? null;

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
        <KPICard title="Total Reproducciones" value={null} />
        <KPICard
          title="Usuarios Únicos"
          value={uniqueUsers}
          subtitle="suscriptores distintos"
        />
        <KPICard title="Contenido Más Visto" value={null} />
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
        <ContentRanking />
      </div>
    </div>
  );
}
