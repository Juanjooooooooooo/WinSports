# tests/api/test_routes.py
#
# Tests de contrato de la API: que cada endpoint enrute, serialice según su
# schema y valide los query params. La capa de datos se monkeypatchea — no se
# necesita Mongo, así se testea la API aislada de la base.

import pytest
from fastapi.testclient import TestClient

import api.routes.overview as ov_routes
import api.routes.qoe as qoe_routes
import api.routes.users as us_routes
from api.main import app
from db.connection import get_db


def async_return(value):
    async def _inner(*args, **kwargs):
        return value

    return _inner


@pytest.fixture(autouse=True)
def _override_db():
    # Las funciones de repo van monkeypatcheadas, así que el db puede ser dummy.
    app.dependency_overrides[get_db] = lambda: None
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ─── health ───────────────────────────────────────────────────────────────────


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ─── overview ─────────────────────────────────────────────────────────────────


def test_unique_users(client, monkeypatch):
    monkeypatch.setattr(ov_routes, "get_unique_users", async_return(7))
    r = client.get("/api/overview/unique-users")
    assert r.status_code == 200
    assert r.json() == {"total": 7}


def test_total_plays(client, monkeypatch):
    monkeypatch.setattr(ov_routes, "get_total_plays", async_return(123))
    r = client.get("/api/overview/total-plays")
    assert r.status_code == 200
    assert r.json() == {"total": 123}


def test_device_ranking(client, monkeypatch):
    monkeypatch.setattr(
        ov_routes,
        "get_device_ranking",
        async_return([{"device": "WEB", "sessions": 5}]),
    )
    r = client.get("/api/overview/device-ranking")
    assert r.status_code == 200
    assert r.json() == {"devices": [{"device": "WEB", "sessions": 5}]}


def test_activity_by_hour(client, monkeypatch):
    monkeypatch.setattr(
        ov_routes, "get_activity_by_hour", async_return([{"hour": 3, "sessions": 2}])
    )
    r = client.get("/api/overview/activity-by-hour")
    assert r.status_code == 200
    assert r.json()["activity"][0] == {"hour": 3, "sessions": 2}


def test_top_content(client, monkeypatch):
    monkeypatch.setattr(
        ov_routes,
        "get_top_content",
        async_return(
            [
                {
                    "title": "Partido",
                    "total_plays": 10,
                    "unique_viewers": 4,
                    "content_type": "MOVIE",
                }
            ]
        ),
    )
    r = client.get("/api/overview/top-content?limit=5")
    assert r.status_code == 200
    assert r.json()["content"][0]["title"] == "Partido"


def test_top_content_limit_invalido(client):
    r = client.get("/api/overview/top-content?limit=0")
    assert r.status_code == 422


def test_users_map(client, monkeypatch):
    point = {
        "subscriber_id": "abc12345",
        "country_code": "CO",
        "lat": 4.5,
        "lon": -74.0,
        "sessions": 3,
        "total_buffer_time": 1.2,
    }
    monkeypatch.setattr(ov_routes, "get_users_map", async_return([point]))
    r = client.get("/api/overview/users-map")
    assert r.status_code == 200
    assert r.json()["points"][0] == point


def test_users_map_limit_invalido(client):
    r = client.get("/api/overview/users-map?limit=0")
    assert r.status_code == 422


# ─── qoe ──────────────────────────────────────────────────────────────────────


def test_buffer_by_content(client, monkeypatch):
    monkeypatch.setattr(
        qoe_routes,
        "get_buffer_by_content",
        async_return(
            [
                {
                    "title": "Partido",
                    "avg_buffer_time": 2.5,
                    "rebuffer_rate": 10.0,
                    "total_plays": 8,
                }
            ]
        ),
    )
    r = client.get("/api/qoe/buffer-by-content?limit=5")
    assert r.status_code == 200
    assert r.json()["content"][0]["avg_buffer_time"] == 2.5


def test_buffer_by_content_limit_invalido(client):
    r = client.get("/api/qoe/buffer-by-content?limit=999")
    assert r.status_code == 422


def test_rebuffering_rate(client, monkeypatch):
    result = {
        "rebuffer_events": 1,
        "total_events": 4,
        "event_rate": 25.0,
        "rebuffer_sessions": 1,
        "total_sessions": 2,
        "session_rate": 50.0,
    }
    monkeypatch.setattr(qoe_routes, "get_rebuffering_rate", async_return(result))
    r = client.get("/api/qoe/rebuffering-rate")
    assert r.status_code == 200
    assert r.json() == result


def test_startup_time(client, monkeypatch):
    result = {
        "avg_seconds": 2.0,
        "max_seconds": 12.0,
        "count": 3,
        "buckets": [{"bucket": "0-1s", "count": 1}],
    }
    monkeypatch.setattr(qoe_routes, "get_startup_time", async_return(result))
    r = client.get("/api/qoe/startup-time")
    assert r.status_code == 200
    assert r.json()["avg_seconds"] == 2.0
    assert r.json()["buckets"][0]["bucket"] == "0-1s"


def test_event_ranking(client, monkeypatch):
    monkeypatch.setattr(
        qoe_routes,
        "get_event_ranking",
        async_return([{"type_event": "PAUSE", "count": 9}]),
    )
    r = client.get("/api/qoe/event-ranking")
    assert r.status_code == 200
    assert r.json()["events"][0] == {"type_event": "PAUSE", "count": 9}


# ─── users ────────────────────────────────────────────────────────────────────


def test_retention_funnel(client, monkeypatch):
    result = {
        "total": 10,
        "firstquartile": 8,
        "midpoint": 6,
        "thirdquartile": 4,
        "complete": 2,
    }
    monkeypatch.setattr(us_routes, "get_retention_funnel", async_return(result))
    r = client.get("/api/users/retention-funnel")
    assert r.status_code == 200
    assert r.json() == result


def test_activity_heatmap(client, monkeypatch):
    monkeypatch.setattr(
        us_routes,
        "get_activity_heatmap",
        async_return([{"weekday": 2, "hour": 10, "sessions": 3}]),
    )
    r = client.get("/api/users/activity-heatmap")
    assert r.status_code == 200
    assert r.json()["activity"][0] == {"weekday": 2, "hour": 10, "sessions": 3}


def test_content_completion_ranking(client, monkeypatch):
    result = {
        "most_completed": [{"title": "A", "completion_rate": 90.0, "total_plays": 5}],
        "most_abandoned": [{"title": "B", "completion_rate": 10.0, "total_plays": 5}],
    }
    monkeypatch.setattr(
        us_routes, "get_content_completion_ranking", async_return(result)
    )
    r = client.get("/api/users/content-completion-ranking")
    assert r.status_code == 200
    assert r.json()["most_completed"][0]["title"] == "A"


def test_user_profiles(client, monkeypatch):
    result = {
        "profiles": [
            {
                "profile": "Heavy",
                "count": 2,
                "total_events": 120,
                "avg_events": 60.0,
                "range": "≥ 50 eventos",
            }
        ],
        "total_users": 2,
    }
    monkeypatch.setattr(us_routes, "get_user_profiles", async_return(result))
    r = client.get("/api/users/user-profiles")
    assert r.status_code == 200
    assert r.json()["profiles"][0]["profile"] == "Heavy"
    assert r.json()["total_users"] == 2
