from engine.advisor import make_daily_decision


def test_healthy_field_waits():

    result = make_daily_decision(
        current_depletion=20,
        raw=35,
        future_etc=[5, 5, 5],
        future_rain=[0, 0, 0],
        rain_probability=0.20,
        heat_result={
            "heat_risk": "LOW"
        },
        maximum_depth=60
    )

    assert result["action"] == "WAIT"


def test_irrigation_needed():

    result = make_daily_decision(
        current_depletion=30,
        raw=35,
        future_etc=[5, 5, 5],
        future_rain=[0, 0, 0],
        rain_probability=0.20,
        heat_result={
            "heat_risk": "LOW"
        },
        maximum_depth=60
    )

    assert result["action"] == "IRRIGATE"
    assert result["depth_mm"] == 30


def test_reliable_rain_causes_skip():

    result = make_daily_decision(
        current_depletion=25,
        raw=35,
        future_etc=[5, 5, 5],
        future_rain=[0, 15, 0],
        rain_probability=0.90,
        heat_result={
            "heat_risk": "LOW"
        },
        maximum_depth=60
    )

    assert result["action"] == "SKIP"


def test_uncertain_rain_does_not_cause_skip():

    result = make_daily_decision(
        current_depletion=30,
        raw=35,
        future_etc=[5, 5, 5],
        future_rain=[0, 15, 0],
        rain_probability=0.40,
        heat_result={
            "heat_risk": "LOW"
        },
        maximum_depth=60
    )

    assert result["action"] == "IRRIGATE"


def test_heat_protection_has_priority():

    result = make_daily_decision(
        current_depletion=20,
        raw=35,
        future_etc=[5, 5, 5],
        future_rain=[0, 0, 0],
        rain_probability=0.20,
        heat_result={
            "heat_risk": "HIGH"
        },
        maximum_depth=60
    )

    assert result["action"] == "HEAT_PROTECTION"
    assert result["depth_mm"] == 15


def test_heat_with_reliable_rain_does_not_trigger_protection():

    result = make_daily_decision(
        current_depletion=20,
        raw=35,
        future_etc=[5, 5, 5],
        future_rain=[0, 15, 0],
        rain_probability=0.90,
        heat_result={
            "heat_risk": "HIGH"
        },
        maximum_depth=60
    )

    assert result["action"] == "SKIP"