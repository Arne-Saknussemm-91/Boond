from engine.water_balance import forecast_water_balance


def predict_depletion(current_depletion, daily_etc_values, daily_rain_values):
    """
    Legacy/simple forecast helper.

    current_depletion is the depletion at the end of today.
    The first forecast value represents tomorrow.

    This function is retained for compatibility with existing tests.
    The production advisor should use forecast_water_balance().
    """
    if len(daily_etc_values) != len(daily_rain_values):
        raise ValueError("daily_etc_values and daily_rain_values must have equal lengths")

    depletion = current_depletion
    predictions = []

    for etc, rain in zip(daily_etc_values, daily_rain_values):
        depletion = depletion + etc - rain
        predictions.append(depletion)

    return predictions


def find_raw_crossing_day(current_depletion, raw, daily_etc_values):
    """
    Legacy/simple RAW crossing helper.

    current_depletion is the depletion at the end of today.
    daily_etc_values[0] represents tomorrow.
    """
    depletion = current_depletion

    for i, etc in enumerate(daily_etc_values):
        depletion = depletion + etc

        if depletion >= raw:
            return i + 1

    return None


def find_raw_crossing_day_from_forecast(forecast_balances):
    """
    Find the first forecast day on which depletion reaches
    or exceeds that day's RAW.

    forecast_balances must be the output of
    forecast_water_balance().
    """

    for index, balance in enumerate(forecast_balances, start=1):
        if balance["depletion_mm"] >= balance["raw_mm"]:
            return index

    return None


def decide_irrigation(
    current_depletion,
    raw,
    future_etc,
    future_rain,
    rain_probability,
    rain_probability_threshold=0.70,
    forecast_balances=None
):
    """
    Decide whether irrigation is required.

    If forecast_balances is supplied, it is the preferred
    source for future depletion and RAW crossing.

    The older future_etc calculation is retained for
    backward compatibility with existing tests.
    """

    if forecast_balances is not None:
        return decide_irrigation_from_forecast(
            forecast_balances=forecast_balances,
            future_rain=future_rain,
            rain_probability=rain_probability,
            rain_probability_threshold=rain_probability_threshold
        )

    # Backward-compatible path.
    crossing_day = find_raw_crossing_day(
        current_depletion,
        raw,
        future_etc
    )

    if crossing_day is None:
        return {
            "action": "WAIT",
            "crossing_day": None,
            "reason_code": "HEALTHY_WATER_BALANCE"
        }

    if rain_probability >= rain_probability_threshold:
        predicted_with_rain = predict_depletion(
            current_depletion,
            future_etc,
            future_rain
        )

        rain_prevents_crossing = True

        for depletion in predicted_with_rain:
            if depletion >= raw:
                rain_prevents_crossing = False
                break

        if rain_prevents_crossing:
            return {
                "action": "SKIP",
                "crossing_day": crossing_day,
                "reason_code": "RAINFALL_EXPECTED"
            }

    if crossing_day <= 2:
        return {
            "action": "IRRIGATE",
            "crossing_day": crossing_day,
            "reason_code": "CROSSES_RAW_IN_2D"
        }

    return {
        "action": "WAIT",
        "crossing_day": crossing_day,
        "reason_code": "CROSSES_RAW_LATER"
    }


def calculate_irrigation_depth(current_depletion, maximum_depth):
    """
    Calculate irrigation depth.

    Current prototype:
    refill approximately the current depletion,
    subject to the configured practical maximum.
    """
    if current_depletion <= 0:
        return 0.0

    return min(current_depletion, maximum_depth)


def make_daily_decision(
    current_depletion,
    raw,
    future_etc,
    future_rain,
    rain_probability,
    heat_result,
    maximum_depth,
    rain_probability_threshold=0.70,
    forecast_balances=None
):
    """
    Combine heat risk and water-balance logic.

    Decision priority:
        1. Heat protection
        2. Rain-supported skip
        3. Irrigation required soon
        4. Wait
    """

    if heat_result["heat_risk"] == "HIGH":
        if rain_probability < rain_probability_threshold:
            return {
                "action": "HEAT_PROTECTION",
                "depth_mm": min(15.0, maximum_depth),
                "reason_code": "HEAT_RISK",
                "crossing_day": None
            }

    irrigation_result = decide_irrigation(
        current_depletion=current_depletion,
        raw=raw,
        future_etc=future_etc,
        future_rain=future_rain,
        rain_probability=rain_probability,
        rain_probability_threshold=rain_probability_threshold,
        forecast_balances=forecast_balances
    )

    if irrigation_result["action"] == "IRRIGATE":
        depth = calculate_irrigation_depth(
            current_depletion,
            maximum_depth
        )

        return {
            "action": "IRRIGATE",
            "depth_mm": depth,
            "reason_code": irrigation_result["reason_code"],
            "crossing_day": irrigation_result["crossing_day"]
        }

    if irrigation_result["action"] == "SKIP":
        return {
            "action": "SKIP",
            "depth_mm": 0.0,
            "reason_code": irrigation_result["reason_code"],
            "crossing_day": irrigation_result["crossing_day"]
        }

    return {
        "action": "WAIT",
        "depth_mm": 0.0,
        "reason_code": irrigation_result["reason_code"],
        "crossing_day": irrigation_result["crossing_day"]
    }



def decide_irrigation_from_forecast(
    forecast_balances,
    future_rain,
    rain_probability,
    rain_probability_threshold=0.70
):
    """
    Decide irrigation using forecast balances and per-day
    rain probabilities.

    Forecast balances must contain:
        previous_depletion_mm
        actual_etc_mm
        raw_mm

    Rain is trusted only when its probability reaches the threshold.
    """

    if len(forecast_balances) != len(future_rain):
        raise ValueError(
            "forecast_balances and future_rain must have equal lengths"
        )

    # Support both a single probability and a probability per day.
    if isinstance(rain_probability, (int, float)):
        probabilities = [rain_probability] * len(forecast_balances)
    else:
        probabilities = list(rain_probability)

    if len(forecast_balances) != len(probabilities):
        raise ValueError(
            "forecast_balances and rain_probability must have equal lengths"
        )

    if not forecast_balances:
        return {
            "action": "WAIT",
            "crossing_day": None,
            "reason_code": "NO_FORECAST_DATA"
        }

    # Track two scenarios independently:
    # 1. No rain occurs.
    # 2. Only sufficiently reliable forecast rain occurs.
    depletion_without_rain = forecast_balances[0]["previous_depletion_mm"]
    depletion_with_trusted_rain = depletion_without_rain

    crossing_without_rain = None
    crossing_with_trusted_rain = None

    for index, balance in enumerate(forecast_balances):
        etc = balance["actual_etc_mm"]
        raw = balance["raw_mm"]

        # The first forecast day starts from today's ending depletion.
        # Later days carry forward the previous simulated day's result.
        depletion_without_rain += etc
        depletion_with_trusted_rain += etc

        probability = probabilities[index]
        rainfall = future_rain[index]

        if probability >= rain_probability_threshold:
            depletion_with_trusted_rain -= rainfall

        # This helper works with depletion values, so keep them
        # within the physically meaningful range of zero or more.
        depletion_without_rain = max(0.0, depletion_without_rain)
        depletion_with_trusted_rain = max(0.0, depletion_with_trusted_rain)

        day = index + 1

        if crossing_without_rain is None and depletion_without_rain >= raw:
            crossing_without_rain = day

        if (
            crossing_with_trusted_rain is None
            and depletion_with_trusted_rain >= raw
        ):
            crossing_with_trusted_rain = day

    # Irrigate if trusted rain does not prevent RAW being reached
    # within the next two days.
    if crossing_with_trusted_rain is not None and crossing_with_trusted_rain <= 2:
        return {
            "action": "IRRIGATE",
            "crossing_day": crossing_with_trusted_rain,
            "reason_code": "CROSSES_RAW_IN_2D"
        }

    # Skip only when irrigation would otherwise be needed within
    # three days, but trusted rain prevents the crossing throughout
    # the forecast period.
    trusted_rain_exists = any(
        rainfall > 0 and probability >= rain_probability_threshold
        for rainfall, probability in zip(future_rain, probabilities)
    )

    if (
        trusted_rain_exists
        and crossing_without_rain is not None
        and crossing_without_rain <= 3
        and crossing_with_trusted_rain is None
    ):
        return {
            "action": "SKIP",
            "crossing_day": crossing_without_rain,
            "reason_code": "RAINFALL_EXPECTED"
        }

    # If the threshold is reached later, reassess on the next day.
    if crossing_with_trusted_rain is not None:
        return {
            "action": "WAIT",
            "crossing_day": crossing_with_trusted_rain,
            "reason_code": "CROSSES_RAW_LATER"
        }

    # No crossing and no reliable rain: this is a healthy balance,
    # not a reason to skip irrigation because of rainfall.
    return {
        "action": "WAIT",
        "crossing_day": None,
        "reason_code": "HEALTHY_WATER_BALANCE"
    }