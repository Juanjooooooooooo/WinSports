# tests/db/test_repositories.py
#
# Tests de repositorios contra mongomock (Mongo async en memoria).
# Cubren las agregaciones soportadas por el mock. Las que usan $round
# (buffer-by-content, content-completion-ranking) se cubren en los tests de API.

from datetime import datetime, timezone

import pytest

from db.repositories import overview as ov
from db.repositories import qoe
from db.repositories import users as us


def _session(sub, cont, hour=10, weekday_date=None, **kw):
    base = {
        "subscriber_id": sub,
        "customer_id": cont,
        "device_type": "WEB",
        "country_code": "CO",
        "start_time": weekday_date
        or datetime(2026, 1, 1, hour, 0, 0, tzinfo=timezone.utc),
        "total_buffer_time": 0.0,
        "rebuffer_count": 0,
        "reached_firstquartile": True,
        "reached_midpoint": False,
        "reached_thirdquartile": False,
        "reached_complete": False,
    }
    base.update(kw)
    return base


def _event(sub, type_event, **kw):
    base = {
        "subscriber_id": sub,
        "customer_id": "c1",
        "device_type": "WEB",
        "type_event": type_event,
        "date": datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "buffer_time": None,
    }
    base.update(kw)
    return base


# ─── overview ─────────────────────────────────────────────────────────────────


async def test_unique_users(db):
    await db.sessions.insert_many(
        [_session("a", "c1"), _session("a", "c2"), _session("b", "c1")]
    )
    assert await ov.get_unique_users(db) == 2


async def test_total_plays(db):
    await db.sessions.insert_many([_session("a", "c1"), _session("b", "c1")])
    assert await ov.get_total_plays(db) == 2


async def test_device_ranking(db):
    await db.sessions.insert_many(
        [
            _session("a", "c1", device_type="WEB"),
            _session("b", "c1", device_type="WEB"),
            _session("c", "c1", device_type="IOS"),
        ]
    )
    ranking = await ov.get_device_ranking(db)
    assert ranking[0] == {"device": "WEB", "sessions": 2}
    assert {r["device"] for r in ranking} == {"WEB", "IOS"}


async def test_activity_by_hour(db):
    await db.sessions.insert_many(
        [_session("a", "c1", hour=3), _session("b", "c1", hour=3)]
    )
    activity = await ov.get_activity_by_hour(db)
    assert len(activity) == 24
    h3 = next(a for a in activity if a["hour"] == 3)
    assert h3["sessions"] == 2


async def test_top_content(db):
    await db.content_stats.insert_many(
        [
            {"title": "A", "total_plays": 10, "unique_viewers": 5, "content_type": "MOVIE"},
            {"title": "B", "total_plays": 3, "unique_viewers": 2, "content_type": "MOVIE"},
        ]
    )
    top = await ov.get_top_content(db, limit=10)
    assert top[0]["title"] == "A"
    assert top[0]["total_plays"] == 10


async def test_users_map_un_punto_por_usuario(db):
    await db.sessions.insert_many(
        [_session("aaa", "c1"), _session("aaa", "c2"), _session("bbb", "c1")]
    )
    points = await ov.get_users_map(db)
    assert len(points) == 2
    by_sub = {p["subscriber_id"]: p for p in points}
    assert by_sub["aaa"[:8]]["sessions"] == 2
    # El punto cae cerca del centroide de Colombia
    for p in points:
        assert -5 < p["lat"] < 15
        assert p["country_code"] == "CO"


# ─── qoe ──────────────────────────────────────────────────────────────────────


async def test_rebuffering_rate(db):
    await db.events.insert_many(
        [
            _event("a", "START"),
            _event("a", "RE-BUFFERING", buffer_time=1.0),
            _event("a", "PAUSE"),
            _event("a", "RESUME"),
        ]
    )
    await db.sessions.insert_many(
        [_session("a", "c1", rebuffer_count=1), _session("b", "c1", rebuffer_count=0)]
    )
    r = await qoe.get_rebuffering_rate(db)
    assert r["rebuffer_events"] == 1
    assert r["total_events"] == 4
    assert r["event_rate"] == 25.0
    assert r["rebuffer_sessions"] == 1
    assert r["total_sessions"] == 2
    assert r["session_rate"] == 50.0


async def test_rebuffering_rate_sin_datos(db):
    r = await qoe.get_rebuffering_rate(db)
    assert r["event_rate"] == 0.0
    assert r["session_rate"] == 0.0


async def test_startup_time(db):
    await db.events.insert_many(
        [
            _event("a", "START-BUFFERING", buffer_time=0.5),
            _event("a", "START-BUFFERING", buffer_time=3.0),
            _event("a", "START-BUFFERING", buffer_time=12.0),
            _event("a", "START"),  # no cuenta
        ]
    )
    r = await qoe.get_startup_time(db)
    assert r["count"] == 3
    assert r["avg_seconds"] == round((0.5 + 3.0 + 12.0) / 3, 3)
    assert r["max_seconds"] == 12.0
    buckets = {b["bucket"]: b["count"] for b in r["buckets"]}
    assert buckets["0-1s"] == 1
    assert buckets["2-5s"] == 1
    assert buckets["10s+"] == 1


async def test_event_ranking(db):
    await db.events.insert_many(
        [
            _event("a", "PAUSE"),
            _event("a", "PAUSE"),
            _event("a", "START"),
        ]
    )
    ranking = await qoe.get_event_ranking(db)
    assert ranking[0] == {"type_event": "PAUSE", "count": 2}


# ─── users ────────────────────────────────────────────────────────────────────


async def test_retention_funnel(db):
    await db.sessions.insert_many(
        [
            _session("a", "c1", reached_firstquartile=True, reached_complete=True),
            _session("b", "c1", reached_firstquartile=True, reached_complete=False),
        ]
    )
    f = await us.get_retention_funnel(db)
    assert f["total"] == 2
    assert f["firstquartile"] == 2
    assert f["complete"] == 1


async def test_activity_heatmap_168_puntos(db):
    await db.sessions.insert_many([_session("a", "c1", hour=10)])
    heatmap = await us.get_activity_heatmap(db)
    assert len(heatmap) == 24 * 7
    assert sum(h["sessions"] for h in heatmap) == 1


async def test_user_profiles_clasifica_por_eventos(db):
    # usuario heavy (60 eventos), mid (20), vague (3)
    docs = []
    docs += [_event("heavy", "PAUSE") for _ in range(60)]
    docs += [_event("mid", "PAUSE") for _ in range(20)]
    docs += [_event("vague", "PAUSE") for _ in range(3)]
    await db.events.insert_many(docs)

    result = await us.get_user_profiles(db)
    by_name = {p["profile"]: p for p in result["profiles"]}
    assert by_name["Heavy"]["count"] == 1
    assert by_name["Mid"]["count"] == 1
    assert by_name["Vague"]["count"] == 1
    assert result["total_users"] == 3
    assert by_name["Heavy"]["avg_events"] == 60.0


async def test_user_profiles_vacio(db):
    result = await us.get_user_profiles(db)
    assert result["total_users"] == 0
    assert {p["profile"] for p in result["profiles"]} == {"Heavy", "Mid", "Vague"}


# ─── geo: _jitter ─────────────────────────────────────────────────────────────


def test_jitter_es_deterministico():
    assert ov._jitter("usuario-x") == ov._jitter("usuario-x")


def test_jitter_difiere_por_semilla():
    assert ov._jitter("usuario-a") != ov._jitter("usuario-b")


def test_jitter_dentro_del_spread():
    lat, lon = ov._jitter("cualquiera", spread=2.5)
    assert -2.5 <= lat <= 2.5
    assert -2.5 <= lon <= 2.5
