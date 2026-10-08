from engine.data import get_setting, max_advised_depth
from engine.kc import get_stage
from engine.paddy import decide_paddy, update_paddy_day
from engine.water_balance import (
    calculate_daily_balance,
    forecast_water_balance
)
from engine.heat_rules import assess_heat_risk
from engine.advisor import make_daily_decision
from engine.resources import (
    gross_depth_mm,
    irrigation_volume_litres,
    irrigation_volume_m3,
    pump_energy_kwh,
    electricity_cost,
    co2_emissions
)


def calculate_resources(
    net_depth_mm,
    area_acres,
    lift_m,
    pump_efficiency=None,
    electricity_tariff=None,
    grid_factor=None
):
    """
    Water, energy, cost and CO2e for one irrigation.

    Volumes and energy use the gross (pumped) depth =
    net depth / config irrigation.application_efficiency.
    The cost is the cost to the power system, not the
    farmer's bill (config cost._why).
    """
    if pump_efficiency is None:
        pump_efficiency = get_setting("energy", "default_pump_efficiency")

    if electricity_tariff is None:
        electricity_tariff = get_setting("cost", "electricity_tariff_inr_per_kwh")

    if grid_factor is None:
        # t CO2 per MWh is the same number as kg CO2 per kWh.
        grid_factor = get_setting("carbon", "grid_emission_factor_t_per_mwh")

    gross_mm = gross_depth_mm(net_depth_mm)

    litres = irrigation_volume_litres(gross_mm, area_acres)
    volume_m3 = irrigation_volume_m3(gross_mm, area_acres)
    energy_kwh = pump_energy_kwh(volume_m3, lift_m, pump_efficiency)

    return {
        "gross_depth_mm": round(gross_mm, 2),
        "litres": round(litres, 2),
        "volume_m3": round(volume_m3, 3),
        "kwh": round(energy_kwh, 3),
        "cost_inr": round(electricity_cost(energy_kwh, electricity_tariff), 2),
        "co2_kg": round(co2_emissions(energy_kwh, grid_factor), 3)
    }


def generate_daily_decision(
    day_after_sowing,
    soil,
    et0,
    rain,
    irrigation,
    previous_depletion,
    future_et0,
    future_rain,
    rain_probability,
    forecast_tmax,
    area_acres,
    lift_m,
    pump_efficiency=None,
    electricity_tariff=None,
    grid_factor=None,
    maximum_irrigation_depth=None,
    crop="wheat"
):
    """
    Generate one complete daily irrigation decision.

    et0 and rain are the values for day_after_sowing. future_et0,
    future_rain, forecast_tmax and a per-day rain_probability list
    start on the next day (day_after_sowing + 1).

    In the 06:00 daily job, call it for YESTERDAY:
        day_after_sowing = (yesterday - sowing_date).days + 1
        et0, rain        = yesterday's observed values (forecast API past_days)
        irrigation       = yesterday's WATERED check-ins (mm)
        future_*         = the forecast starting TODAY
    The returned action is then today's advice. This matches
    engine/simulate.py, which decides each morning from yesterday's
    ending depletion. Passing today's forecast as et0/rain instead
    would shift every decision by a day.

    The growth stage and heat window are derived from the
    crop day. Settings left as None come from config.json.

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
    # STEP 0: Fill in configured defaults
    # -------------------------------------------------

    if maximum_irrigation_depth is None:
        maximum_irrigation_depth = max_advised_depth(crop)

    # -------------------------------------------------
    # STEP 1: Calculate today's water balance
    # -------------------------------------------------

    balance = calculate_daily_balance(
        day_after_sowing=day_after_sowing,
        soil=soil,
        et0=et0,
        rain=rain,
        irrigation=irrigation,
        previous_depletion=previous_depletion,
        crop=crop
    )
    forecast_balances = forecast_water_balance(
        start_day_after_sowing=day_after_sowing,
        soil=soil,
        future_et0=future_et0,
        future_rain=future_rain,
        initial_depletion=balance["depletion_mm"],
        crop=crop
    )

    # -------------------------------------------------
    # STEP 2: Calculate heat risk
    # -------------------------------------------------

    heat_result = assess_heat_risk(
        first_day_after_sowing=day_after_sowing + 1,
        forecast_tmax=forecast_tmax,
        crop=crop
    )

    # -------------------------------------------------
    # STEP 3: Make irrigation decision
    # -------------------------------------------------

    decision = make_daily_decision(
        current_depletion=balance["depletion_mm"],
        raw=balance["raw_mm"],
        future_etc=[],
        future_rain=future_rain,
        rain_probability=rain_probability,
        heat_result=heat_result,
        maximum_depth=maximum_irrigation_depth,
        forecast_balances=forecast_balances
    )

    # -------------------------------------------------
    # STEP 4: Calculate water and energy
    # -------------------------------------------------

    depth_mm = decision["depth_mm"]

    resources = calculate_resources(
        depth_mm,
        area_acres,
        lift_m,
        pump_efficiency,
        electricity_tariff,
        grid_factor
    )

    # -------------------------------------------------
    # STEP 5: Build final engine output
    # -------------------------------------------------

    return {
        "day_after_sowing": day_after_sowing,
        "crop": crop,

        "action": decision["action"],
        "depth_mm": round(depth_mm, 2),

        "stage": get_stage(day_after_sowing, crop),
        "heat_stage": heat_result["stage"],
        "heat_risk": heat_result["heat_risk"],

        "rain_probability": rain_probability,
        "rain_next_3d_mm": round(
            sum(future_rain[:get_setting("advisor", "rain_skip_window_days")]),
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

        **resources
    }


def generate_daily_decision_paddy(
    day_after_transplanting,
    soil,
    et0,
    rain,
    irrigation,
    state,
    future_rain,
    rain_probability,
    forecast_tmax,
    area_acres,
    lift_m,
    pump_efficiency=None,
    electricity_tariff=None,
    grid_factor=None,
    crop="paddy"
):
    """
    Daily decision for transplanted paddy (DATA_GUIDE 4.6).

    state is yesterday's {"pond_mm", "depletion_mm", "dry_days"}
    (engine.paddy.initial_paddy_state() at transplanting).
    Today's weather is applied, then the PAU rule decides.
    The returned "state" is stored for tomorrow.
    """

    state, details = update_paddy_day(
        day=day_after_transplanting,
        soil=soil,
        et0=et0,
        rain=rain,
        irrigation=irrigation,
        state=state,
        crop=crop
    )

    heat_result = assess_heat_risk(
        first_day_after_sowing=day_after_transplanting + 1,
        forecast_tmax=forecast_tmax,
        crop=crop
    )

    decision = decide_paddy(
        day=day_after_transplanting,
        state=state,
        future_rain=future_rain,
        rain_probability=rain_probability,
        heat_result=heat_result,
        crop=crop
    )

    return {
        "day_after_transplanting": day_after_transplanting,
        "crop": crop,

        "action": decision["action"],
        "depth_mm": round(decision["depth_mm"], 2),
        "reason_code": decision["reason_code"],

        "stage": get_stage(day_after_transplanting, crop),
        "heat_stage": heat_result["stage"],
        "heat_risk": heat_result["heat_risk"],

        "pond_mm": round(state["pond_mm"], 2),
        "depletion_mm": round(state["depletion_mm"], 2),
        "dry_days": state["dry_days"],
        "kc": round(details["kc"], 3),
        "etc_mm": round(details["actual_etc_mm"], 2),
        "percolation_mm": round(details["percolation_mm"], 2),

        "state": state,

        **calculate_resources(
            decision["depth_mm"],
            area_acres,
            lift_m,
            pump_efficiency,
            electricity_tariff,
            grid_factor
        )
    }