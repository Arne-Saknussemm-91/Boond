def predict_depletion(current_depletion, daily_etc_values, daily_rain_values):
    """
    Predict future depletion using forecast ETc and effective rain.
    """
    depletion = current_depletion
    predictions = []

    for i in range(len(daily_etc_values)):
        etc = daily_etc_values[i]
        rain = daily_rain_values[i]

        depletion = depletion + etc - rain
        predictions.append(depletion)

    return predictions


def find_raw_crossing_day(current_depletion, raw, daily_etc_values):
    """
    Find the first forecast day on which depletion
    reaches or exceeds RAW.
    """
    depletion = current_depletion

    for i, etc in enumerate(daily_etc_values):
        depletion = depletion + etc

        if depletion >= raw:
            return i + 1

    return None


def decide_irrigation(
    current_depletion,
    raw,
    future_etc,
    future_rain,
    rain_probability,
    rain_probability_threshold=0.70
):
    """
    Decide whether irrigation is required based on
    soil-water depletion and forecast rainfall.
    """

    crossing_day = find_raw_crossing_day(
        current_depletion,
        raw,
        future_etc
    )

    # Soil is expected to remain within RAW.
    if crossing_day is None:
        return {
            "action": "WAIT",
            "crossing_day": None,
            "reason_code": "HEALTHY_WATER_BALANCE"
        }

    # Only trust rainfall when forecast confidence
    # reaches our configured threshold.
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

    # If water stress is approaching within two days,
    # irrigation is required.
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

    We refill approximately the current depletion,
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
    rain_probability_threshold=0.70
):
    """
    Combine heat risk and water-balance logic into
    one daily irrigation decision.

    Decision priority:

        1. Heat protection
        2. Rain-supported skip
        3. Irrigation required soon
        4. Wait
    """

    # -------------------------------------------------
    # 1. HEAT PROTECTION HAS HIGHEST PRIORITY
    # -------------------------------------------------

    if heat_result["heat_risk"] == "HIGH":

        # We don't want to irrigate for heat protection
        # if meaningful rain is already expected.
        if rain_probability < rain_probability_threshold:

            return {
                "action": "HEAT_PROTECTION",
                "depth_mm": min(
                    15.0,
                    maximum_depth
                ),
                "reason_code": "HEAT_RISK",
                "crossing_day": None
            }

    # -------------------------------------------------
    # 2-4. NORMAL WATER-BALANCE DECISION
    # -------------------------------------------------

    irrigation_result = decide_irrigation(
        current_depletion=current_depletion,
        raw=raw,
        future_etc=future_etc,
        future_rain=future_rain,
        rain_probability=rain_probability,
        rain_probability_threshold=rain_probability_threshold
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