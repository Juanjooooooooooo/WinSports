# tests/api/test_admin.py
#
# Tests de contrato de las rutas de admin. La capa de datos va monkeypatcheada,
# así que no se necesita Mongo: se prueba enrutado, serialización y validación.

import pytest
from fastapi.testclient import TestClient

import api.routes.admin as admin_routes
from api.main import app
from db.connection import get_db


def async_return(value):
    async def _inner(*args, **kwargs):
        return value

    return _inner


def async_raise(exc):
    async def _inner(*args, **kwargs):
        raise exc

    return _inner


@pytest.fixture(autouse=True)
def _override_db():
    app.dependency_overrides[get_db] = lambda: None
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ─── collections ────────────────────────────────────────────────────────────


def test_collections_suma_total(client, monkeypatch):
    monkeypatch.setattr(
        admin_routes,
        "count_collections",
        async_return(
            [
                {"name": "events", "count": 50},
                {"name": "sessions", "count": 12},
                {"name": "content_stats", "count": 4},
            ]
        ),
    )
    r = client.get("/api/admin/collections")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 66
    assert {c["name"] for c in body["collections"]} == {
        "events",
        "sessions",
        "content_stats",
    }


# ─── documents ──────────────────────────────────────────────────────────────


def test_documents_ok(client, monkeypatch):
    monkeypatch.setattr(
        admin_routes,
        "list_documents",
        async_return({"total": 1, "documents": [{"_id": "abc", "title": "Liga"}]}),
    )
    r = client.get("/api/admin/documents/events?page=1&page_size=10")
    assert r.status_code == 200
    body = r.json()
    assert body["collection"] == "events"
    assert body["total"] == 1
    assert body["documents"][0]["title"] == "Liga"


def test_documents_coleccion_desconocida_404(client):
    r = client.get("/api/admin/documents/no_existe")
    assert r.status_code == 404


def test_documents_page_size_fuera_de_rango_422(client):
    r = client.get("/api/admin/documents/events?page_size=99999")
    assert r.status_code == 422


# ─── edición en vivo ─────────────────────────────────────────────────────────


def test_edit_document_ok(client, monkeypatch):
    monkeypatch.setattr(admin_routes, "update_document", async_return(1))
    r = client.put(
        "/api/admin/documents/events/65aa00000000000000000000",
        json={"fields": {"title": "Nuevo título"}},
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True, "modified": 1}


def test_edit_document_id_invalido_400(client, monkeypatch):
    monkeypatch.setattr(
        admin_routes, "update_document", async_raise(ValueError("ID inválido"))
    )
    r = client.put(
        "/api/admin/documents/events/xxx", json={"fields": {"title": "x"}}
    )
    assert r.status_code == 400


def test_edit_document_coleccion_desconocida_404(client):
    r = client.put("/api/admin/documents/foo/abc", json={"fields": {"a": 1}})
    assert r.status_code == 404


# ─── borrado ─────────────────────────────────────────────────────────────────


def test_delete_document_ok(client, monkeypatch):
    monkeypatch.setattr(admin_routes, "delete_document", async_return(1))
    r = client.delete("/api/admin/documents/events/65aa00000000000000000000")
    assert r.status_code == 200
    assert r.json() == {"ok": True, "deleted": 1}


def test_delete_document_no_encontrado_404(client, monkeypatch):
    monkeypatch.setattr(admin_routes, "delete_document", async_return(0))
    r = client.delete("/api/admin/documents/events/65aa00000000000000000000")
    assert r.status_code == 404


# ─── upload CSV ──────────────────────────────────────────────────────────────


def test_upload_csv_ok(client, monkeypatch):
    monkeypatch.setattr(
        admin_routes,
        "ingest_csv",
        async_return(
            {
                "rows_total": 50,
                "rows_skipped": 2,
                "inserted": 48,
                "batch_errors": 0,
                "events_total": 98,
                "sessions_built": 20,
                "content_stats_built": 8,
            }
        ),
    )
    r = client.post(
        "/api/admin/upload-csv",
        files={"file": ("nuevos.csv", b"Date,SubscriberID\n", "text/csv")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["filename"] == "nuevos.csv"
    assert body["inserted"] == 48
    assert body["events_total"] == 98


def test_upload_csv_rechaza_no_csv(client):
    r = client.post(
        "/api/admin/upload-csv",
        files={"file": ("datos.txt", b"hola", "text/plain")},
    )
    assert r.status_code == 400


def test_upload_csv_rechaza_vacio(client):
    r = client.post(
        "/api/admin/upload-csv",
        files={"file": ("vacio.csv", b"", "text/csv")},
    )
    assert r.status_code == 400
