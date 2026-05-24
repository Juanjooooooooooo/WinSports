# tests/db/test_load_csv.py
#
# Tests del parseo del CSV a documentos de `events`.

from datetime import datetime, timezone

from scripts.load_csv import _to_date, _to_float, _to_int, _to_str, parse_row

NAN = float("nan")


# ─── _to_str ──────────────────────────────────────────────────────────────────


def test_to_str_limpia_espacios():
    assert _to_str("  hola  ") == "hola"


def test_to_str_vacio_es_none():
    assert _to_str("") is None
    assert _to_str("   ") is None


def test_to_str_nan_es_none():
    assert _to_str(NAN) is None
    assert _to_str(None) is None


# ─── _to_int ──────────────────────────────────────────────────────────────────


def test_to_int_normal():
    assert _to_int("42") == 42
    assert _to_int(42) == 42


def test_to_int_float_string():
    # El CSV trae enteros como "2023.0" — antes esto devolvía None (bug)
    assert _to_int("2023.0") == 2023


def test_to_int_basura_es_none():
    assert _to_int("abc") is None
    assert _to_int(NAN) is None
    assert _to_int(None) is None


# ─── _to_float ────────────────────────────────────────────────────────────────


def test_to_float_normal():
    assert _to_float("6.805") == 6.805


def test_to_float_cero():
    assert _to_float("0") == 0.0


def test_to_float_nan_y_none():
    assert _to_float(NAN) is None
    assert _to_float(None) is None
    assert _to_float("xyz") is None


# ─── _to_date ─────────────────────────────────────────────────────────────────


def test_to_date_valida_en_utc():
    d = _to_date("2026-01-01 01:23:19")
    assert d == datetime(2026, 1, 1, 1, 23, 19, tzinfo=timezone.utc)


def test_to_date_invalida_es_none():
    assert _to_date("no es fecha") is None
    assert _to_date(None) is None
    assert _to_date("") is None


# ─── parse_row ────────────────────────────────────────────────────────────────


def _csv_row():
    return {
        "Date": "2026-01-01 01:23:19",
        "CountryCode": "CO",
        "SubscriberID": "sub123",
        "CustomerId": "cont456",
        "ContentType": "EPISODE",
        "Title": "ARTE Y PASION",
        "Episode": "1",
        "SeriesTitle": "ARTE Y PASION",
        "ReleaseYear": "2023.0",
        "Duration": "387",
        "Season": "1",
        "Genres": "Series",
        "DeviceType": "ANDR",
        "TypeEvent": "START",
        "Position": "1079999",
        "Language": "ES",
        "Bitrate": "18197686",
        "BufferTime": "6.805",
        "PlaybackNetTime": "0",
        "deviceDescription": "android app",
        "CALC_ProgramType": "SERIE",
        "CALC_BitrateType": "HIGH",
    }


def test_parse_row_mapea_campos():
    doc = parse_row(_csv_row())
    assert doc["subscriber_id"] == "sub123"
    assert doc["customer_id"] == "cont456"
    assert doc["device_type"] == "ANDR"
    assert doc["type_event"] == "START"
    assert doc["country_code"] == "CO"


def test_parse_row_castea_tipos():
    doc = parse_row(_csv_row())
    assert doc["episode"] == 1
    assert doc["release_year"] == 2023  # "2023.0" → 2023
    assert doc["duration"] == 387
    assert doc["bitrate"] == 18197686
    assert doc["buffer_time"] == 6.805
    assert isinstance(doc["date"], datetime)


def test_parse_row_campos_faltantes_a_none():
    row = _csv_row()
    row["BufferTime"] = ""
    row["Episode"] = NAN
    doc = parse_row(row)
    assert doc["buffer_time"] is None
    assert doc["episode"] is None
