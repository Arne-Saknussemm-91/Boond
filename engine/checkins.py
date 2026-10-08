"""
Convert farmer check-ins into millimetres (DATA_GUIDE 4.5).

    WATERED light / normal / heavy  -> crops[profile].irrigation.checkin_depth_mm
                                       (fallback config.checkin.watered_mm_default)
    RAIN    little / moderate / heavy -> config.checkin.rain_mm

Store the farmer's words and the assumed mm on the EVENT item.
"""

from engine.data import get_crop, get_setting


def watered_mm(level, crop="wheat"):
    level = level.lower()
    depths = get_crop(crop).get("irrigation", {}).get("checkin_depth_mm")

    if not depths:
        depths = get_setting("checkin", "watered_mm_default")

    if level not in depths:
        raise ValueError(f"Unknown watering level: {level}")

    return float(depths[level])


def rain_mm(level):
    level = level.lower()
    amounts = get_setting("checkin", "rain_mm")

    if level not in amounts:
        raise ValueError(f"Unknown rain level: {level}")

    return float(amounts[level])


def apply_checkins(gridded_rain_mm, events, crop="wheat"):
    """
    Return (rain_mm, irrigation_mm) for one day.

    events is a list of {"type": "WATERED" | "RAIN", "level": ...}
    for that day. A RAIN check-in replaces the gridded rain
    rather than adding to it, so the same rain is not counted
    twice. If there are several RAIN check-ins, the largest wins.
    WATERED check-ins add up.
    """
    rain = gridded_rain_mm
    reported_rain = [
        rain_mm(event["level"])
        for event in events
        if event["type"].upper() == "RAIN"
    ]

    if reported_rain:
        rain = max(reported_rain)

    irrigation = sum(
        watered_mm(event["level"], crop)
        for event in events
        if event["type"].upper() == "WATERED"
    )

    return rain, irrigation
