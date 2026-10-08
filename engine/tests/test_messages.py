import re
from pathlib import Path

import pytest

from engine.daily_engine import generate_daily_decision, generate_daily_decision_paddy
from engine.data import entries, load_json
from engine.messages import LANGUAGES, render


ENGINE = Path(__file__).resolve().parents[1]
ACTIONS = {"IRRIGATE", "WAIT", "SKIP", "HEAT_PROTECTION", "HIGH", "LOW"}


def reason_codes_in(source_file):
    text = (ENGINE / source_file).read_text()
    return set(re.findall(r'"([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+)"', text)) - ACTIONS


def test_every_reason_code_has_english_and_hindi_text():
    codes = reason_codes_in("advisor.py") | reason_codes_in("paddy.py")
    reasons = load_json("messages.json")["reasons"]

    assert {"HEAT_RISK_SOIL_MOIST", "HEAT_RISK_RAIN_EXPECTED"} <= codes
    assert codes - set(reasons) == set()

    for code, text in reasons.items():
        assert set(text) == set(LANGUAGES), code


def test_every_heat_window_has_a_stage_name():
    stages = load_json("messages.json")["stages"]

    for crop in entries(load_json("crops.json")).values():
        for window in crop.get("heat_windows", []):
            assert set(stages[window["name"]]) == set(LANGUAGES)


def wheat_heat_day(**overrides):
    # Punjab wheat, day 95: days 96-98 are in the flowering window.
    inputs = {
        "day_after_sowing": 95,
        "soil": "loam",
        "et0": 5.0,
        "rain": 0.0,
        "irrigation": 0.0,
        "previous_depletion": 5.0,
        "future_et0": [5.0, 5.0, 5.0],
        "future_rain": [0.0, 0.0, 0.0],
        "rain_probability": 0.1,
        "forecast_tmax": [36.4, 35.0, 34.0],
        "area_acres": 1.0,
        "lift_m": 30.0,
    }
    inputs.update(overrides)

    return generate_daily_decision(**inputs)


def test_heat_on_moist_soil_message():
    result = wheat_heat_day()

    assert result["reason_code"] == "HEAT_RISK_SOIL_MOIST"
    assert render(result, "hi") == (
        "गर्मी की चेतावनी: फूल आने के समय तापमान 36.4°C तक जा सकता है। "
        "मिट्टी में अभी नमी है, इसलिए आज सिंचाई न करें। बूंद कल फिर जाँच करेगा।"
    )
    assert render(result, "en").startswith("Heat alert: up to 36.4°C expected during flowering.")


def test_heat_with_rain_expected_message():
    result = wheat_heat_day(future_rain=[0.0, 20.0, 0.0], rain_probability=[0.1, 0.9, 0.1])

    assert result["reason_code"] == "HEAT_RISK_RAIN_EXPECTED"
    assert render(result, "hi") == (
        "गर्मी की चेतावनी: फूल आने के समय तापमान 36.4°C तक जा सकता है, "
        "लेकिन अगले 3 दिनों में बारिश की संभावना है (20 मिमी का अनुमान)। "
        "गर्मी से बचाव के लिए सिंचाई की ज़रूरत नहीं है।"
    )


def test_heat_protection_message_shows_whole_mm():
    result = wheat_heat_day(previous_depletion=45.0)

    assert result["action"] == "HEAT_PROTECTION"
    assert "लगभग 40 मिमी हल्की सिंचाई करें" in render(result, "hi")


def test_paddy_message():
    result = generate_daily_decision_paddy(
        day_after_transplanting=30,
        soil="loam",
        et0=5.0,
        rain=0.0,
        irrigation=0.0,
        state={"pond_mm": 40.0, "depletion_mm": 0.0, "dry_days": 0},
        future_rain=[0.0, 0.0, 0.0],
        rain_probability=0.1,
        forecast_tmax=[30.0, 30.0, 30.0],
        area_acres=1.0,
        lift_m=30.0
    )

    assert result["reason_code"] == "POND_PRESENT"
    assert "खेत में अभी पानी खड़ा है" in render(result, "hi")


def test_unknown_language_or_code_raises():
    with pytest.raises(ValueError):
        render({"reason_code": "HEALTHY_WATER_BALANCE"}, "pa")

    with pytest.raises(ValueError):
        render({"reason_code": "NOT_A_CODE"}, "hi")
