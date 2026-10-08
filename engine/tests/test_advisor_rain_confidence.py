from engine.advisor import decide_irrigation_from_forecast


def make_balance(previous, actual_etc, raw):
    return {
        "previous_depletion_mm": previous,
        "actual_etc_mm": actual_etc,
        "raw_mm": raw
    }


def test_high_confidence_rain_prevents_irrigation():
    forecast = [
        make_balance(40.0, 5.0, 50.0),
        make_balance(45.0, 5.0, 50.0),
        make_balance(50.0, 5.0, 50.0),
    ]

    result = decide_irrigation_from_forecast(
        forecast_balances=forecast,
        future_rain=[0.0, 20.0, 0.0],
        rain_probability=[0.20, 0.90, 0.20]
    )

    assert result["action"] == "SKIP"
    assert result["reason_code"] == "RAINFALL_EXPECTED"


def test_low_confidence_rain_is_not_trusted():
    forecast = [
        make_balance(45.0, 5.0, 48.0),
        make_balance(50.0, 5.0, 48.0),
        make_balance(55.0, 5.0, 48.0),
    ]

    result = decide_irrigation_from_forecast(
        forecast_balances=forecast,
        future_rain=[20.0, 0.0, 0.0],
        rain_probability=[0.30, 0.20, 0.20]
    )

    assert result["action"] == "IRRIGATE"
    assert result["reason_code"] == "CROSSES_RAW_IN_2D"


def test_rain_after_raw_crossing_does_not_prevent_irrigation():
    forecast = [
        make_balance(46.0, 5.0, 48.0),
        make_balance(51.0, 5.0, 48.0),
        make_balance(56.0, 5.0, 48.0),
    ]

    result = decide_irrigation_from_forecast(
        forecast_balances=forecast,
        future_rain=[0.0, 0.0, 30.0],
        rain_probability=[0.20, 0.20, 0.90]
    )

    assert result["action"] == "IRRIGATE"
    assert result["crossing_day"] == 1


def test_high_confidence_rain_that_is_insufficient_does_not_skip():
    forecast = [
        make_balance(45.0, 5.0, 48.0),
        make_balance(49.0, 5.0, 48.0),
        make_balance(54.0, 5.0, 48.0),
    ]

    result = decide_irrigation_from_forecast(
        forecast_balances=forecast,
        future_rain=[0.0, 2.0, 0.0],
        rain_probability=[0.20, 0.90, 0.20]
    )

    assert result["action"] == "IRRIGATE"


def test_no_rain_behaves_normally():
    forecast = [
        make_balance(40.0, 5.0, 50.0),
        make_balance(45.0, 5.0, 50.0),
        make_balance(50.0, 5.0, 50.0),
    ]

    result = decide_irrigation_from_forecast(
        forecast_balances=forecast,
        future_rain=[0.0, 0.0, 0.0],
        rain_probability=[0.0, 0.0, 0.0]
    )

    assert result["action"] == "IRRIGATE"
    assert result["crossing_day"] == 2