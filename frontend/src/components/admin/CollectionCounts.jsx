// src/components/admin/CollectionCounts.jsx
import KPICard from "../overview/KPICard";

const LABELS = {
  events: "Eventos (raw)",
  sessions: "Sesiones",
  content_stats: "Content stats",
};
const ORDER = ["events", "sessions", "content_stats"];

export default function CollectionCounts({ data }) {
  return (
    <div
      style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px" }}
    >
      <KPICard
        title="Total documentos"
        value={data ? data.total.toLocaleString() : null}
        subtitle="en las 3 colecciones"
      />
      {ORDER.map((name) => {
        const c = data?.collections?.find((x) => x.name === name);
        return (
          <KPICard
            key={name}
            title={LABELS[name]}
            value={c ? c.count.toLocaleString() : null}
            subtitle={name}
          />
        );
      })}
    </div>
  );
}
