// src/pages/QoE.jsx
import { useState, useEffect } from "react";
import RebufferingRate from "../components/qoe/RebufferingRate";
import StartupTime from "../components/qoe/StartupTime";
import BufferByContent from "../components/qoe/BufferByContent";
import EventRanking from "../components/qoe/EventRanking";

export default function QoE() {
  const [rebuffering, setRebuffering] = useState(null);
  const [startup, setStartup] = useState(null);
  const [bufferByContent, setBufferByContent] = useState(null);
  const [eventRanking, setEventRanking] = useState(null);

  useEffect(() => {
    fetch("/api/qoe/rebuffering-rate")
      .then((r) => r.json())
      .then(setRebuffering);

    fetch("/api/qoe/startup-time")
      .then((r) => r.json())
      .then(setStartup);

    fetch("/api/qoe/buffer-by-content?limit=8")
      .then((r) => r.json())
      .then((d) => setBufferByContent(d.content));

    fetch("/api/qoe/event-ranking")
      .then((r) => r.json())
      .then((d) => setEventRanking(d.events));
  }, []);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      {/* Tasa de rebuffering + tiempo de inicialización */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
        }}
      >
        <RebufferingRate data={rebuffering} />
        <StartupTime data={startup} />
      </div>

      {/* Buffer por contenido + ranking de eventos */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
        }}
      >
        <BufferByContent data={bufferByContent} />
        <EventRanking data={eventRanking} />
      </div>
    </div>
  );
}
