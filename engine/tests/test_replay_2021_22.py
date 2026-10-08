"""
Pinned results of the 2021-22 Ludhiana replay (Open-Meteo ERA5
archive, observed weather standing in for the forecast, forecast rain
not trusted). These are the numbers quoted in the demo: if a change to
the engine or the data moves them, this test fails so the figures are
re-checked before they are used again.
"""

import json
from datetime import date
from pathlib import Path

import pytest

from engine.replay import replay


CACHE = Path(__file__).resolve().parents[2] / "replay" / "cache"
WEATHER = json.loads((CACHE / "ludhiana_actual_2021_22.json").read_text())

# crop, sowing date, (Boond irrigations, mm, stress days), (baseline irrigations, mm, stress days)
LOAM_RESULTS = [
    ("wheat", date(2021, 11, 5), (3, 162.1, 0), (2, 125.0, 14)),
    ("wheat_late", date(2021, 12, 1), (5, 265.1, 0), (2, 125.0, 30)),
    ("paddy", date(2021, 6, 25), (7, 527.9, 7), (7, 525.0, 8)),
    ("cotton", date(2021, 5, 1), (6, 250.5, 0), (6, 450.0, 8)),
    ("sugarcane", date(2021, 3, 1), (13, 753.8, 0), (20, 1500.0, 8)),
]


def totals(summary):
    return summary["irrigation_events"], summary["irrigation_mm"], summary["stress_days"]


@pytest.mark.parametrize("crop, sowing, boond, baseline", LOAM_RESULTS, ids=[row[0] for row in LOAM_RESULTS])
def test_pinned_loam_results(crop, sowing, boond, baseline):
    result = replay(WEATHER, crop, sowing, "loam")

    assert totals(result["boond"]) == boond
    assert totals(result["baseline"]) == baseline


def test_replay_is_labelled_honestly():
    result = replay(WEATHER, "wheat", date(2021, 11, 5), "loam")

    assert result["label"].startswith("SIMULATION")
    assert result["boond_forecast"] == "actual weather used as forecast (perfect foresight)"
    assert result["boond_rain_probability"] is None
    assert all(row["action"] != "SKIP" for row in result["boond_days"])


def test_wheat_irrigation_dates():
    result = replay(WEATHER, "wheat", date(2021, 11, 5), "loam")

    boond = [(row["date"], row["reason_code"]) for row in result["boond_days"] if row["irrigation_mm"] > 0]
    baseline = [row["date"] for row in result["baseline_days"] if row["irrigation_mm"] > 0]

    assert boond == [
        ("2021-12-02", "CRITICAL_STAGE_IRRIGATION"),
        ("2022-02-28", "CROSSES_RAW_IN_2D"),
        ("2022-03-17", "HEAT_RISK"),
    ]
    assert baseline == ["2021-12-02", "2022-02-16"]


def test_boond_has_no_upland_stress_days_on_any_soil():
    for crop, sowing, _, _ in LOAM_RESULTS:
        if crop == "paddy":
            continue

        for soil in ("sandy", "loam", "clay"):
            assert replay(WEATHER, crop, sowing, soil)["boond"]["stress_days"] == 0, (crop, soil)
