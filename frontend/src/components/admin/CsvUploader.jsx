// src/components/admin/CsvUploader.jsx
import { useRef, useState } from "react";

const cardStyle = {
  background: "var(--color-surface)",
  border: "1px solid var(--color-border)",
  borderRadius: "8px",
  padding: "24px",
};
const headingStyle = {
  fontSize: "12px",
  color: "var(--color-text-muted)",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
  marginBottom: "16px",
};

export default function CsvUploader({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | uploading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const upload = async () => {
    if (!file) return;
    setStatus("uploading");
    setError(null);
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const r = await fetch("/api/admin/upload-csv", { method: "POST", body: fd });
      const body = await r.json();
      if (!r.ok) throw new Error(body.detail || "Error al subir el CSV");
      setResult(body);
      setStatus("done");
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
      onUploaded?.();
    } catch (e) {
      setError(e.message);
      setStatus("error");
    }
  };

  const uploading = status === "uploading";

  return (
    <div style={cardStyle}>
      <h3 style={headingStyle}>Cargar nuevo CSV de eventos</h3>

      <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          aria-label="Archivo CSV"
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null);
            setStatus("idle");
            setError(null);
            setResult(null);
          }}
          style={{ color: "var(--color-text)", fontSize: "13px" }}
        />
        <button
          onClick={upload}
          disabled={!file || uploading}
          style={{
            background:
              !file || uploading ? "var(--color-surface-2)" : "var(--color-primary)",
            color: !file || uploading ? "var(--color-text-muted)" : "white",
            border: "none",
            borderRadius: "6px",
            padding: "8px 18px",
            fontSize: "13px",
            fontWeight: "600",
            cursor: !file || uploading ? "not-allowed" : "pointer",
          }}
        >
          {uploading ? "Procesando..." : "Subir y procesar"}
        </button>
      </div>

      <p style={{ fontSize: "11px", color: "var(--color-text-muted)", marginTop: "10px" }}>
        Inserta los eventos en <code>events</code> y re-construye{" "}
        <code>sessions</code> y <code>content_stats</code>. El dashboard se
        actualiza al terminar.
      </p>

      {error && (
        <div
          style={{
            marginTop: "14px",
            color: "var(--color-danger)",
            fontSize: "13px",
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {result && (
        <div
          style={{
            marginTop: "14px",
            background: "var(--color-surface-2)",
            borderRadius: "6px",
            padding: "14px 16px",
            fontSize: "13px",
            color: "var(--color-text)",
            lineHeight: 1.7,
          }}
        >
          ✅ <strong>{result.filename}</strong> procesado.
          <br />
          Insertados: <strong>{result.inserted.toLocaleString()}</strong> · Omitidos:{" "}
          {result.rows_skipped.toLocaleString()} de {result.rows_total.toLocaleString()}
          {result.batch_errors > 0 && ` · Batches con error: ${result.batch_errors}`}
          <br />
          Total en <code>events</code>: {result.events_total.toLocaleString()} · Sesiones:{" "}
          {result.sessions_built.toLocaleString()} · Content stats:{" "}
          {result.content_stats_built.toLocaleString()}
        </div>
      )}
    </div>
  );
}
