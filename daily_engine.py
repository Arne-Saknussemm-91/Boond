from engine.water_balance import calculate_daily_balance
from engine.heat_rules import check_heat_risk
from engine.advisor import make_daily_decision
from engine.resources import (
    irrigation_volume_litres,
    irrigation_volume_m3,
    pump_energy_kwh,
    electricity_cost,
    co2_emissions
)


def generate_daily_decision(
    day_after_sowing,
    soil,
    et0,
    rain,
    irrigation,
    previous_depletion,
    future_etc,
    future_rain,
    rain_probability,
    heat_stage,
    forecast_tmax,
    area_acres,
    lift_m,
    pump_efficiency,
    electricity_tariff,
    grid_factor,
    maximum_irrigation_depth=60
):
    """
    Generate one complete daily irrigation decision.

    This function combines:

        1. Water balance
        2. Heat risk
        3. Irrigation decision
        4. Water volume
        5. Pump energy
        6. Electricity cost
        7. CO2 emissions
    """

    # -------------------------------------------------
    # STEP 1: Calculate today's water balance
    # -------------------------------------------------

    balance = calculate_daily_balance(
        day_after_sowing=day_after_sowing,
        soil=soil,
        et0=et0,
        rain=rain,
        irrigation=irrigation,
        previous_depletion=previous_depletion
    )

    # -------------------------------------------------
    # STEP 2: Calculate heat risk
    # -------------------------------------------------

    heat_result = check_heat_risk(
        stage=heat_stage,
        forecast_tmax=forecast_tmax
    )

    # -------------------------------------------------
    # STEP 3: Make irrigation decision
    # -------------------------------------------------

    decision = make_daily_decision(
        current_depletion=balance["depletion_mm"],
        raw=balance["raw_mm"],
        future_etc=future_etc,
        future_rain=future_rain,
        rain_probability=rain_probability,
        heat_result=heat_result,
        maximum_depth=maximum_irrigation_depth
    )

    # -------------------------------------------------
    # STEP 4: Calculate water and energy
    # -------------------------------------------------

    depth_mm = decision["depth_mm"]

    litres = irrigation_volume_litres(
        depth_mm,
        area_acres
    )

    volume_m3 = irrigation_volume_m3(
        depth_mm,
        area_acres
    )

    energy_kwh = pump_energy_kwh(
        volume_m3,
        lift_m,
        pump_efficiency
    )

    cost_inr = electricity_cost(
        energy_kwh,
        electricity_tariff
    )

    co2_kg = co2_emissions(
        energy_kwh,
        grid_factor
    )

    # -------------------------------------------------
    # STEP 5: Build final engine output
    # -------------------------------------------------

    return {
        "day_after_sowing": day_after_sowing,

        "action": decision["action"],
        "depth_mm": round(depth_mm, 2),

        "stage": heat_stage,
        "heat_risk": heat_result["heat_risk"],

        "rain_probability": rain_probability,
        "rain_next_3d_mm": round(
            sum(future_rain),
            2
        ),

        "kc": round(balance["kc"], 3),
        "et0_mm": round(balance["et0_mm"], 2),
        "etc_mm": round(balance["actual_etc_mm"], 2),

        "depletion_mm": round(
            balance["depletion_mm"],
            2
        ),

        "raw_mm": round(
            balance["raw_mm"],
            2
        ),

        "taw_mm": round(
            balance["taw_mm"],
            2
        ),

        "ks": round(
            balance["ks"],
            3
        ),

        "water_wallet_pct": round(
            max(
                0,
                min(
                    100,
                    100 * (
                        1 -
                        balance["depletion_mm"]
                        / balance["taw_mm"]
                    )
                )
            ),
            1
        ),

        "crossing_day": decision["crossing_day"],

        "reason_code": decision["reason_code"],

        "litres": round(litres, 2),

        "volume_m3": round(volume_m3, 3),

        "kwh": round(energy_kwh, 3),

        "cost_inr": round(cost_inr, 2),

        "co2_kg": round(co2_kg, 3)
    }