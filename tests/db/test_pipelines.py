# tests/db/test_pipelines.py
#
# Tests de la lógica pura de construcción de colecciones derivadas.
# No tocan Mongo — ejercitan _build_sessions y _build_content_stats directo.

from datetime import datetime, timezone

from db.pipelines.content_stats import _build_content_stats
from db.pipelines.sessions import _build_sessions


def ev(minute, type_event, **overrides):
    """Crea un evento de prueba con valores por defecto razonables."""
    base = {
        "subscriber_id": "sub1",
        "customer_id": "cont1",
        "date": datetime(2026, 1, 1, 10, minute, 0, tzinfo=timezone.utc),
        "type_event": type_event,
        "device_type": "WEB",
        "country_code": "CO",
        "title": "Partido",
        "series_title": None,
        "content_type": "MOVIE",
        "genres": "Deportes",
        "duration": 100,
        "position": None,
        "buffer_time": None,
        "calc_bitrate_type": "HIGH",
    }
    base.update(overrides)
    return base


# ─── _build_sessions ────────────────────────────────────────────────────────


def test_una_sesion_por_grupo_simple():
    events = [ev(0, "START"), ev(1, "PAUSE"), ev(2, "COMPLETE")]
    sessions = _build_sessions(events)
    assert len(sessions) == 1
    assert sessions[0]["event_count"] == 3


def test_dos_starts_parten_en_dos_sesiones():
    events = [ev(0, "START"), ev(1, "PAUSE"), ev(5, "START"), ev(6, "COMPLETE")]
    sessions = _build_sessions(events)
    assert len(sessions) == 2
    assert sessions[0]["event_count"] == 2
    assert sessions[1]["event_count"] == 2


def test_eventos_antes_del_primer_start_forman_sesion():
    # Si no hay START inicial, los eventos previos igual cuentan como sesión
    events = [ev(0, "RESUME"), ev(1, "PAUSE"), ev(5, "START"), ev(6, "COMPLETE")]
    sessions = _build_sessions(events)
    assert len(sessions) == 2


def test_start_end_time():
    events = [ev(0, "START"), ev(9, "COMPLETE")]
    s = _build_sessions(events)[0]
    assert s["start_time"] == datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    assert s["end_time"] == datetime(2026, 1, 1, 10, 9, 0, tzinfo=timezone.utc)


def test_total_buffer_time_suma():
    events = [
        ev(0, "START"),
        ev(1, "START-BUFFERING", buffer_time=2.5),
        ev(2, "RE-BUFFERING", buffer_time=1.0),
    ]
    s = _build_sessions(events)[0]
    assert s["total_buffer_time"] == 3.5


def test_rebuffer_y_pause_count():
    events = [
        ev(0, "START"),
        ev(1, "PAUSE"),
        ev(2, "PAUSE"),
        ev(3, "RE-BUFFERING", buffer_time=1.0),
    ]
    s = _build_sessions(events)[0]
    assert s["pause_count"] == 2
    assert s["rebuffer_count"] == 1


def test_flags_de_retencion():
    events = [
        ev(0, "START"),
        ev(1, "FIRSTQUARTILE"),
        ev(2, "MIDPOINT"),
        ev(3, "COMPLETE"),
    ]
    s = _build_sessions(events)[0]
    assert s["reached_firstquartile"] is True
    assert s["reached_midpoint"] is True
    assert s["reached_thirdquartile"] is False
    assert s["reached_complete"] is True


def test_completion_pct_normal():
    events = [ev(0, "START", position=50, duration=100)]
    s = _build_sessions(events)[0]
    assert s["completion_pct"] == 50.0


def test_completion_pct_capeado_a_100():
    # Position en otra unidad → no debe pasar de 100%
    events = [ev(0, "START", position=1_000_000, duration=100)]
    s = _build_sessions(events)[0]
    assert s["completion_pct"] == 100.0


def test_completion_pct_none_sin_duracion():
    events = [ev(0, "START", position=50, duration=None)]
    s = _build_sessions(events)[0]
    assert s["completion_pct"] is None


def test_max_position():
    events = [ev(0, "START", position=10), ev(1, "PROGRESSMARK", position=80)]
    s = _build_sessions(events)[0]
    assert s["max_position"] == 80


def test_dominant_bitrate():
    events = [
        ev(0, "START", calc_bitrate_type="LOW"),
        ev(1, "RESUME", calc_bitrate_type="HIGH"),
        ev(2, "RESUME", calc_bitrate_type="HIGH"),
    ]
    s = _build_sessions(events)[0]
    assert s["dominant_bitrate_type"] == "HIGH"


def test_grupos_por_usuario_y_contenido():
    events = [
        ev(0, "START", subscriber_id="a", customer_id="x"),
        ev(0, "START", subscriber_id="b", customer_id="x"),
        ev(0, "START", subscriber_id="a", customer_id="y"),
    ]
    sessions = _build_sessions(events)
    assert len(sessions) == 3


# ─── _build_content_stats ─────────────────────────────────────────────────────


def session(sub, cont, **overrides):
    base = {
        "subscriber_id": sub,
        "customer_id": cont,
        "title": "Partido",
        "series_title": None,
        "content_type": "MOVIE",
        "genres": "Deportes",
        "release_year": 2024,
        "duration": 100,
        "device_type": "WEB",
        "total_buffer_time": 0.0,
        "rebuffer_count": 0,
        "completion_pct": 50.0,
        "reached_firstquartile": True,
        "reached_midpoint": False,
        "reached_thirdquartile": False,
        "reached_complete": False,
    }
    base.update(overrides)
    return base


def test_content_stats_volumen_y_viewers():
    sessions = [
        session("a", "c1"),
        session("a", "c1"),
        session("b", "c1"),
    ]
    docs = _build_content_stats(sessions)
    assert len(docs) == 1
    d = docs[0]
    assert d["total_plays"] == 3
    assert d["unique_viewers"] == 2


def test_content_stats_rates():
    sessions = [
        session("a", "c1", reached_complete=True),
        session("b", "c1", reached_complete=False),
    ]
    d = _build_content_stats(sessions)[0]
    assert d["completion_rate"] == 50.0
    assert d["firstquartile_rate"] == 100.0


def test_content_stats_rebuffer_rate():
    sessions = [
        session("a", "c1", rebuffer_count=2),
        session("b", "c1", rebuffer_count=0),
        session("c", "c1", rebuffer_count=0),
    ]
    d = _build_content_stats(sessions)[0]
    assert d["rebuffer_rate"] == round(1 / 3 * 100, 2)


def test_content_stats_avg_buffer():
    sessions = [
        session("a", "c1", total_buffer_time=2.0),
        session("b", "c1", total_buffer_time=4.0),
    ]
    d = _build_content_stats(sessions)[0]
    assert d["avg_buffer_time"] == 3.0


def test_content_stats_plays_by_device():
    sessions = [
        session("a", "c1", device_type="WEB"),
        session("b", "c1", device_type="WEB"),
        session("c", "c1", device_type="IOS"),
    ]
    d = _build_content_stats(sessions)[0]
    assert d["plays_by_device"] == {"WEB": 2, "IOS": 1}


def test_content_stats_avg_completion():
    sessions = [
        session("a", "c1", completion_pct=40.0),
        session("b", "c1", completion_pct=60.0),
    ]
    d = _build_content_stats(sessions)[0]
    assert d["avg_completion_pct"] == 50.0


def test_content_stats_separa_por_contenido():
    sessions = [session("a", "c1"), session("a", "c2")]
    docs = _build_content_stats(sessions)
    assert {d["customer_id"] for d in docs} == {"c1", "c2"}
