import KPICard from "../components/overview/KPICard";
import DeviceRanking from "../components/overview/DeviceRanking";
import ActivityTimeline from "../components/overview/ActivityTimeline";
import ContentRanking from "../components/overview/ContentRanking";
import UsersMap from "../components/overview/UsersMap";

export default function Overview() {
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
        <KPICard title="Usuarios Únicos" value={null} />
        <KPICard title="Contenido Más Visto" value={null} />
        <KPICard title="Dispositivo Líder" value={null} />
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
        <DeviceRanking />
      </div>

      {/* Timeline + Content Ranking */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
        }}
      >
        <ActivityTimeline />
        <ContentRanking />
      </div>
    </div>
  );
}
