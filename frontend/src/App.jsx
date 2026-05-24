// src/App.jsx
import { useState } from "react";
import Overview from "./pages/Overview";
import QoE from "./pages/QoE";
import Users from "./pages/Users";

const PAGES = ["Overview", "QoE", "Usuarios", "Alertas", "Admin"];
const IMPLEMENTED = new Set(["Overview", "QoE", "Usuarios"]);

export default function App() {
  const [activePage, setActivePage] = useState("Overview");

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Sidebar */}
      <aside
        style={{
          width: "220px",
          background: "var(--color-surface)",
          borderRight: "1px solid var(--color-border)",
          display: "flex",
          flexDirection: "column",
          padding: "24px 0",
          gap: "4px",
        }}
      >
        <div
          style={{
            padding: "0 24px 24px",
            borderBottom: "1px solid var(--color-border)",
            marginBottom: "12px",
          }}
        >
          <span
            style={{
              color: "var(--color-primary)",
              fontWeight: "700",
              fontSize: "20px",
              letterSpacing: "-0.5px",
            }}
          >
            Win Sports
          </span>
          <div
            style={{
              color: "var(--color-text-muted)",
              fontSize: "12px",
              marginTop: "2px",
            }}
          >
            Analytics
          </div>
        </div>

        {PAGES.map((page) => (
          <button
            key={page}
            onClick={() => setActivePage(page)}
            style={{
              background:
                activePage === page ? "var(--color-primary)" : "transparent",
              color: activePage === page ? "white" : "var(--color-text-muted)",
              border: "none",
              textAlign: "left",
              padding: "10px 24px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: activePage === page ? "600" : "400",
              borderRadius: "0",
              transition: "all 0.15s",
            }}
          >
            {page}
          </button>
        ))}
      </aside>

      {/* Main content */}
      <main
        style={{
          flex: 1,
          padding: "32px",
          background: "var(--color-bg)",
          overflowY: "auto",
        }}
      >
        <h1
          style={{
            fontSize: "24px",
            fontWeight: "700",
            color: "var(--color-text)",
            marginBottom: "24px",
          }}
        >
          {activePage}
        </h1>

        {activePage === "Overview" && <Overview />}
        {activePage === "QoE" && <QoE />}
        {activePage === "Usuarios" && <Users />}
        {!IMPLEMENTED.has(activePage) && (
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
            {activePage} — en construcción
          </div>
        )}
      </main>
    </div>
  );
}
