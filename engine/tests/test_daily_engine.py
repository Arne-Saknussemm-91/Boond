from engine.daily_engine import generate_daily_decision


def test_complete_daily_decision():

    result = generate_daily_decision(
        day_after_sowing=40,

        soil="loam",

        et0=5.0,

        rain=0.0,

        irrigation=0.0,

        previous_depletion=30.0,

        future_et0=[
            5.0,
            5.0,
            5.0
        ],

        future_rain=[
            0.0,
            0.0,
            0.0
        ],

        rain_probability=0.20,

        heat_stage="tillering",

        forecast_tmax=[
            28.0,
            29.0,
            30.0
        ],

        area_acres=1.0,

        lift_m=30.0,

        pump_efficiency=0.40,

        electricity_tariff=8.0,

        grid_factor=0.70,

        maximum_irrigation_depth=60
    )

    print(result)
    assert result["action"] == "WAIT"
    assert result["depth_mm"] == 0.0
    assert result["heat_risk"] == "LOW"

    assert result["depletion_mm"] < result["raw_mm"]

    assert result["taw_mm"] > 0
    assert result["raw_mm"] > 0

    assert result["litres"] == 0.0
    assert result["volume_m3"] == 0.0
    assert result["kwh"] == 0.0
    assert result["cost_inr"] == 0.0
    assert result["co2_kg"] == 0.0

    print("\nFINAL ENGINE OUTPUT:")
    print(result)