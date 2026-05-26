// src/pages/Admin.jsx
import { useCallback, useEffect, useState } from "react";
import CollectionCounts from "../components/admin/CollectionCounts";
import CsvUploader from "../components/admin/CsvUploader";
import DocumentTable from "../components/admin/DocumentTable";

const COLLECTIONS = ["events", "sessions", "content_stats"];
const PAGE_SIZE = 25;

export default function Admin() {
  const [counts, setCounts] = useState(null);
  const [collection, setCollection] = useState("events");
  const [page, setPage] = useState(1);
  const [docs, setDocs] = useState(null);

  const loadCounts = useCallback(() => {
    fetch("/api/admin/collections")
      .then((r) => r.json())
      .then(setCounts)
      .catch(() => setCounts(null));
  }, []);

  const loadDocs = useCallback(() => {
    // El reseteo a "cargando" (setDocs(null)) se hace en los handlers de evento,
    // no aquí, para no llamar setState síncrono dentro del useEffect.
    fetch(`/api/admin/documents/${collection}?page=${page}&page_size=${PAGE_SIZE}`)
      .then((r) => r.json())
      .then(setDocs)
      .catch(() => setDocs({ total: 0, documents: [] }));
  }, [collection, page]);

  useEffect(() => {
    loadCounts();
  }, [loadCounts]);

  useEffect(() => {
    loadDocs();
  }, [loadDocs]);

  const changeCollection = (c) => {
    if (c === collection) return;
    setDocs(null);
    setCollection(c);
    setPage(1);
  };

  const changePage = (p) => {
    setDocs(null);
    setPage(p);
  };

  const handleUploaded = () => {
    loadCounts();
    setDocs(null);
    loadDocs();
  };

  const handleSave = async (id, fields) => {
    const r = await fetch(`/api/admin/documents/${collection}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fields }),
    });
    if (!r.ok) {
      const body = await r.json().catch(() => ({}));
      throw new Error(body.detail || "No se pudo guardar el documento");
    }
    loadDocs();
  };

  const handleDelete = async (id) => {
    const r = await fetch(`/api/admin/documents/${collection}/${id}`, {
      method: "DELETE",
    });
    if (!r.ok) {
      const body = await r.json().catch(() => ({}));
      throw new Error(body.detail || "No se pudo eliminar el documento");
    }
    loadCounts();
    loadDocs();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
      <CollectionCounts data={counts} />
      <CsvUploader onUploaded={handleUploaded} />
      <DocumentTable
        collections={COLLECTIONS}
        collection={collection}
        onCollectionChange={changeCollection}
        data={docs}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={changePage}
        onSave={handleSave}
        onDelete={handleDelete}
      />
    </div>
  );
}
