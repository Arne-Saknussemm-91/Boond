from datetime import date, timedelta

import pytest

from engine.check_data import seasonal_etc, validate
from engine.kc import get_kc
from engine.replay import replay
from engine.simulate import simulate_season


def test_data_files_are_consistent():
    assert validate() == []


def make_weather(days, start=date(2021, 11, 10), et0=4.0, rain=None, tmax=25.0):
    return {
        "daily": {
            "date": [(start + timedelta(days=i)).isoformat() for i in range(days)],
            "et0_mm": [et0] * days,
            "rain_mm": rain or [0.0] * days,
            "tmax_c": [tmax] * days,
        }
    }


def test_dry_season_irrigates_without_stress():
    result = simulate_season(make_weather(160), date(2021, 11, 10), "loam")
    summary = result["summary"]

    assert len(result["days"]) == 145
    assert summary["irrigation_events"] > 0
    assert summary["stress_days"] == 0
    # Every advised depth respects the 40-75 mm flood limits.
    depths = [row["irrigation_mm"] for row in result["days"] if row["irrigation_mm"] > 0]
    assert min(depths) >= 40.0
    assert max(depths) <= 75.0
    assert summary["gross_pumped_mm"] == pytest.approx(summary["irrigation_mm"] / 0.70, abs=0.1)


def test_season_must_be_covered_by_weather():
    with pytest.raises(ValueError):
        simulate_season(make_weather(60), date(2021, 11, 10), "loam")


def test_stress_free_seasonal_etc():
    # Constant ET0 4 mm: sum of Kc over 145 days x 4.
    etc = seasonal_etc(make_weather(160), "wheat", date(2021, 11, 10))

    assert etc == pytest.approx(4.0 * sum(get_kc(day) for day in range(1, 146)))


def test_wheat_replay_follows_the_pau_calendar():
    result = replay(make_weather(160), "wheat", date(2021, 11, 10), "loam")
    baseline_days = [
        row["day"] for row in result["baseline_days"] if row["irrigation_mm"] > 0
    ]

    # Sown in November: day 28, then 5.5 (38.5 days), 5.5 and 4 weeks later.
    assert baseline_days == [28, 67, 106, 134]
    assert result["baseline"]["irrigation_mm"] == 50 + 3 * 75


def test_wheat_baseline_rain_delay_rule():
    rain = [0.0] * 160
    rain[9] = 20.0  # 2 cm on day 10 (19 Nov): 10 days later.

    result = replay(make_weather(160, rain=rain), "wheat", date(2021, 11, 10), "loam")
    first = next(row["day"] for row in result["baseline_days"] if row["irrigation_mm"] > 0)

    assert first == 38


def test_paddy_replay_runs_the_pond_model():
    weather = make_weather(130, start=date(2021, 6, 25), et0=6.0)
    result = replay(weather, "paddy", date(2021, 6, 25), "sandy")

    assert result["baseline"]["irrigation_events"] > 5
    assert result["boond"]["irrigation_events"] > 5
    assert "pond_mm" in result["boond_days"][0]


def test_cotton_baseline_interval():
    weather = make_weather(170, start=date(2021, 5, 1), et0=6.0)
    result = replay(weather, "cotton", date(2021, 5, 1), "loam")
    days = [row["day"] for row in result["baseline_days"] if row["irrigation_mm"] > 0]

    assert days[:3] == [35, 52, 69]
    # Last irrigation by 30 September (day 153).
    assert days[-1] <= 153
