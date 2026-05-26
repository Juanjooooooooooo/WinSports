// src/components/admin/DocumentTable.jsx
import { useMemo, useState } from "react";

const cardStyle = {
  background: "var(--color-surface)",
  border: "1px solid var(--color-border)",
  borderRadius: "8px",
  padding: "24px",
};

// Preserva el tipo original al editar: si el campo era número/booleano,
// castea el texto del input de vuelta a ese tipo antes de mandarlo a la API.
function coerce(original, value) {
  if (value === "") return null;
  if (typeof original === "number") {
    const n = Number(value);
    return Number.isNaN(n) ? value : n;
  }
  if (typeof original === "boolean") return value === "true" || value === true;
  return value;
}

function displayValue(v) {
  if (v === null || v === undefined) return "—";
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export default function DocumentTable({
  collections,
  collection,
  onCollectionChange,
  data,
  page,
  pageSize,
  onPageChange,
  onSave,
  onDelete,
}) {
  const [editingId, setEditingId] = useState(null);
  const [draft, setDraft] = useState({});
  const [rowError, setRowError] = useState(null);
  const [busy, setBusy] = useState(false);

  const documents = data?.documents ?? null;
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const columns = useMemo(() => {
    const docs = documents ?? [];
    const keys = new Set();
    docs.forEach((d) => Object.keys(d).forEach((k) => keys.add(k)));
    keys.delete("_id");
    return ["_id", ...keys];
  }, [documents]);

  const startEdit = (doc) => {
    setEditingId(doc._id);
    setDraft({ ...doc });
    setRowError(null);
  };
  const cancel = () => {
    setEditingId(null);
    setDraft({});
    setRowError(null);
  };

  const save = async (doc) => {
    setBusy(true);
    setRowError(null);
    try {
      const fields = {};
      for (const k of Object.keys(draft)) {
        if (k === "_id") continue;
        if (draft[k] !== doc[k]) fields[k] = coerce(doc[k], draft[k]);
      }
      await onSave(doc._id, fields);
      cancel();
    } catch (e) {
      setRowError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (doc) => {
    if (!window.confirm("¿Eliminar este documento? No se puede deshacer.")) return;
    setBusy(true);
    setRowError(null);
    try {
      await onDelete(doc._id);
    } catch (e) {
      setRowError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const cellStyle = {
    padding: "8px 10px",
    borderBottom: "1px solid var(--color-border)",
    fontSize: "12px",
    color: "var(--color-text)",
    whiteSpace: "nowrap",
    maxWidth: "240px",
    overflow: "hidden",
    textOverflow: "ellipsis",
  };

  return (
    <div style={cardStyle}>
      {/* Header: selector de colección + total */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "16px",
          gap: "12px",
          flexWrap: "wrap",
        }}
      >
        <div style={{ display: "flex", gap: "6px" }}>
          {collections.map((c) => (
            <button
              key={c}
              onClick={() => {
                cancel();
                onCollectionChange(c);
              }}
              style={{
                background:
                  c === collection ? "var(--color-primary)" : "var(--color-surface-2)",
                color: c === collection ? "white" : "var(--color-text-muted)",
                border: "1px solid var(--color-border)",
                borderRadius: "6px",
                padding: "6px 14px",
                fontSize: "12px",
                fontWeight: c === collection ? "600" : "400",
                cursor: "pointer",
              }}
            >
              {c}
            </button>
          ))}
        </div>
        <span style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>
          {total.toLocaleString()} documentos
        </span>
      </div>

      {rowError && (
        <div style={{ color: "var(--color-danger)", fontSize: "13px", marginBottom: "10px" }}>
          ⚠️ {rowError}
        </div>
      )}

      {documents === null ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center", padding: "24px" }}>
          Cargando...
        </div>
      ) : documents.length === 0 ? (
        <div style={{ color: "var(--color-text-muted)", textAlign: "center", padding: "24px" }}>
          Sin documentos
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ borderCollapse: "collapse", width: "100%", minWidth: "640px" }}>
            <thead>
              <tr>
                {columns.map((col) => (
                  <th
                    key={col}
                    style={{
                      ...cellStyle,
                      color: "var(--color-text-muted)",
                      textTransform: "uppercase",
                      letterSpacing: "0.4px",
                      fontSize: "11px",
                      textAlign: "left",
                    }}
                  >
                    {col}
                  </th>
                ))}
                <th style={{ ...cellStyle, textAlign: "right" }}>acciones</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => {
                const editing = editingId === doc._id;
                return (
                  <tr key={doc._id}>
                    {columns.map((col) => {
                      const value = doc[col];
                      const editable =
                        editing && col !== "_id" && typeof value !== "object";
                      return (
                        <td key={col} style={cellStyle} title={displayValue(value)}>
                          {editable ? (
                            <input
                              aria-label={col}
                              value={draft[col] ?? ""}
                              onChange={(e) =>
                                setDraft((d) => ({ ...d, [col]: e.target.value }))
                              }
                              style={{
                                background: "var(--color-bg)",
                                color: "var(--color-text)",
                                border: "1px solid var(--color-border)",
                                borderRadius: "4px",
                                padding: "4px 6px",
                                fontSize: "12px",
                                width: "140px",
                              }}
                            />
                          ) : (
                            displayValue(value)
                          )}
                        </td>
                      );
                    })}
                    <td style={{ ...cellStyle, textAlign: "right" }}>
                      {editing ? (
                        <span style={{ display: "inline-flex", gap: "6px" }}>
                          <button
                            onClick={() => save(doc)}
                            disabled={busy}
                            style={btnStyle("var(--color-success)")}
                          >
                            Guardar
                          </button>
                          <button onClick={cancel} disabled={busy} style={btnStyle()}>
                            Cancelar
                          </button>
                        </span>
                      ) : (
                        <span style={{ display: "inline-flex", gap: "6px" }}>
                          <button onClick={() => startEdit(doc)} style={btnStyle()}>
                            Editar
                          </button>
                          <button
                            onClick={() => remove(doc)}
                            style={btnStyle("var(--color-danger)")}
                          >
                            Eliminar
                          </button>
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Paginación */}
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          alignItems: "center",
          gap: "12px",
          marginTop: "16px",
        }}
      >
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          style={btnStyle()}
        >
          ‹ Anterior
        </button>
        <span style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>
          Página {page} de {totalPages}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          style={btnStyle()}
        >
          Siguiente ›
        </button>
      </div>
    </div>
  );
}

function btnStyle(accent) {
  return {
    background: "var(--color-surface-2)",
    color: accent || "var(--color-text-muted)",
    border: "1px solid var(--color-border)",
    borderRadius: "4px",
    padding: "4px 10px",
    fontSize: "12px",
    cursor: "pointer",
  };
}
