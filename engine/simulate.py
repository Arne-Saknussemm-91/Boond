"""
Season simulator: run an irrigation policy over a whole season of
daily weather.

    python -m engine.simulate --weather weather.json --sow 2021-11-10 --soil loam --crop wheat

Each morning the policy decides from yesterday's ending state.
Any irrigation is applied that day, then the day's balance is
computed with the actual weather.

Forecast seen by the Boond policy:
  * with --forecast FILE: the archived forecast in FILE (from
    tools/fetch_weather.py --source historical-forecast), using its
    own rain_prob values when present;
  * otherwise the next forecast_days of the actual weather
    (perfect foresight). Rain then counts for SKIP only if you pass
    --rain-probability; by default (None) forecast rain is NOT
    trusted, so savings are not overstated. Always report the
    setting used.

Weather files are the JSON written by tools/fetch_weather.py:
    {"daily": {"date": [...], "et0_mm": [...], "rain_mm": [...],
               "tmax_c": [...], "rain_prob": [...] (optional, 0-1)}}
"""

import argparse
import json
from datetime import date

from engine.advisor import make_daily_decision
from engine.critical import critical_irrigation_due
from engine.daily_engine import calculate_resources
from engine.data import get_setting, is_paddy, max_advised_depth
from engine.heat_rules import assess_heat_risk
from engine.kc import get_kc, get_season_length
from engine.paddy import decide_paddy, initial_paddy_state, update_paddy_day
from engine.water_balance import (
    calculate_daily_balance,
    calculate_p,
    calculate_raw,
    calculate_taw,
    forecast_water_balance,
    get_root_depth
)


def starting_depletion(soil, et0, crop="wheat"):
    """
    Depletion at sowing: 0 after a pre-sowing irrigation,
    otherwise RAW (config root_zone.assume_full_at_sowing).
    """
    if get_setting("root_zone", "assume_full_at_sowing"):
        return 0.0

    taw = calculate_taw(soil, get_root_depth(1, crop))
    p = calculate_p(get_kc(1, crop) * et0, crop=crop, day_after_sowing=1)

    return calculate_raw(taw, p)


def _forecast_window(context, forecast_days, forecast, rain_probability):
    """
    Return (et0, rain, tmax, probability) lists for the forecast that
    starts today. From the archived forecast file when given (matched
    by date), otherwise from the actual weather.
    """
    if forecast is None:
        daily = context["weather"]
        start = context["index"]
    else:
        daily = forecast["daily"]
        today = context["date"].isoformat()

        if today not in daily["date"]:
            raise ValueError(f"Forecast file has no row for {today}")

        start = daily["date"].index(today)

    window = slice(start, min(start + forecast_days, len(daily["date"])))
    et0 = daily["et0_mm"][window]

    if rain_probability is None and "rain_prob" in daily:
        probability = daily["rain_prob"][window]
    else:
        probability = [rain_probability] * len(et0)

    return et0, daily["rain_mm"][window], daily["tmax_c"][window], probability


def boond_policy(rain_probability=None, forecast_days=3, forecast=None):
    """
    The Boond advisor as a simulation policy.

    rain_probability=None means forecast rain is not trusted (unless
    the forecast file carries its own rain_prob). Pass 1.0 only for
    a labelled "perfect rain forecast" sensitivity run.
    """

    def decide(context):
        day = context["day"]
        crop = context["crop"]

        future_et0, future_rain, future_tmax, probability = _forecast_window(
            context, forecast_days, forecast, rain_probability
        )
        heat_result = assess_heat_risk(day, future_tmax, crop)

        if context["paddy"]:
            return decide_paddy(
                day=day,
                state=context["state"],
                future_rain=future_rain,
                rain_probability=probability,
                heat_result=heat_result,
                crop=crop
            )

        forecast_balances = forecast_water_balance(
            start_day_after_sowing=day - 1,
            soil=context["soil"],
            future_et0=future_et0,
            future_rain=future_rain,
            initial_depletion=context["state"],
            crop=crop
        )

        return make_daily_decision(
            current_depletion=context["state"],
            raw=forecast_balances[0]["raw_mm"],
            future_etc=[],
            future_rain=future_rain,
            rain_probability=probability,
            heat_result=heat_result,
            maximum_depth=max_advised_depth(crop),
            forecast_balances=forecast_balances,
            critical=critical_irrigation_due(
                crop,
                day,
                context["water_since_sowing_mm"],
                context["sow_date"]
            )
        )

    return decide


def simulate_season(
    weather,
    sow_date,
    soil,
    crop="wheat",
    policy=None,
    area_acres=1.0,
    lift_m=30.0,
    pump_efficiency=None
):
    """
    policy(context) returns {"action", "depth_mm", "reason_code"}.
    context has weather, index (today's row), day, date, crop,
    soil, paddy and state (yesterday's depletion for upland
    crops, the pond state for paddy).
    """
    daily = weather["daily"]
    dates = [date.fromisoformat(value) for value in daily["date"]]

    if sow_date not in dates:
        raise ValueError(f"Weather does not include the sowing date {sow_date}")

    first = dates.index(sow_date)
    season_length = get_season_length(crop)

    if first + season_length > len(dates):
        raise ValueError("Weather does not cover the whole season")

    if policy is None:
        policy = boond_policy()

    paddy = is_paddy(crop)

    if paddy:
        state = initial_paddy_state(crop)
    else:
        state = starting_depletion(soil, daily["et0_mm"][first], crop)

    days = []
    seasonal_etc = 0.0
    water_since_sowing = 0.0  # effective rain + irrigation after sowing

    for day in range(1, season_length + 1):
        today = first + day - 1

        decision = policy({
            "weather": daily,
            "index": today,
            "day": day,
            "date": dates[today],
            "sow_date": sow_date,
            "crop": crop,
            "soil": soil,
            "paddy": paddy,
            "state": state,
            "water_since_sowing_mm": water_since_sowing
        })

        irrigation = decision["depth_mm"]

        if paddy:
            state, balance = update_paddy_day(
                day=day,
                soil=soil,
                et0=daily["et0_mm"][today],
                rain=daily["rain_mm"][today],
                irrigation=irrigation,
                state=state,
                crop=crop
            )
            losses = balance["percolation_mm"] + balance["overflow_mm"]
        else:
            balance = calculate_daily_balance(
                day_after_sowing=day,
                soil=soil,
                et0=daily["et0_mm"][today],
                rain=daily["rain_mm"][today],
                irrigation=irrigation,
                previous_depletion=state,
                crop=crop
            )
            state = balance["depletion_mm"]
            losses = balance["deep_percolation_mm"]
            water_since_sowing += balance["effective_rain_mm"] + irrigation

        seasonal_etc += balance["actual_etc_mm"]

        days.append({
            "date": daily["date"][today],
            "day": day,
            "action": decision["action"],
            "reason_code": decision["reason_code"],
            "irrigation_mm": round(irrigation, 2),
            "rain_mm": daily["rain_mm"][today],
            "depletion_mm": round(balance["depletion_mm"], 2),
            "ks": round(balance["ks"], 3),
            "losses_mm": round(losses, 2),
            **({"pond_mm": round(balance["pond_mm"], 2)} if paddy else {})
        })

    irrigation_mm = sum(row["irrigation_mm"] for row in days)
    resources = calculate_resources(irrigation_mm, area_acres, lift_m, pump_efficiency)

    summary = {
        "crop": crop,
        "soil": soil,
        "sow_date": sow_date.isoformat(),
        "irrigation_events": sum(1 for row in days if row["irrigation_mm"] > 0),
        "irrigation_mm": round(irrigation_mm, 1),
        "gross_pumped_mm": resources["gross_depth_mm"],
        "pump_kwh": round(resources["kwh"], 1),
        "co2_kg": round(resources["co2_kg"], 1),
        "stress_days": sum(1 for row in days if row["ks"] < 1.0),
        "seasonal_etc_mm": round(seasonal_etc, 1),
        "rain_mm": round(sum(row["rain_mm"] for row in days), 1),
        "drainage_mm": round(sum(row["losses_mm"] for row in days), 1)
    }

    return {"summary": summary, "days": days}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--weather", required=True)
    parser.add_argument("--sow", required=True, type=date.fromisoformat)
    parser.add_argument("--soil", default="loam")
    parser.add_argument("--crop", default="wheat")
    parser.add_argument("--forecast-days", type=int, default=3)
    parser.add_argument("--rain-probability", type=float, default=None,
                        help="trust forecast rain at this probability (default: not trusted)")
    parser.add_argument("--forecast", help="archived forecast file (historical-forecast)")
    parser.add_argument("--out")
    args = parser.parse_args()

    with open(args.weather, "r") as file:
        weather = json.load(file)

    forecast = None

    if args.forecast:
        with open(args.forecast, "r") as file:
            forecast = json.load(file)

    result = simulate_season(
        weather,
        args.sow,
        args.soil,
        crop=args.crop,
        policy=boond_policy(args.rain_probability, args.forecast_days, forecast)
    )

    print(json.dumps(result["summary"], indent=2))

    if args.out:
        with open(args.out, "w") as file:
            json.dump(result, file, indent=2)


if __name__ == "__main__":
    main()
