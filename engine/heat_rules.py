import json
from pathlib import Path


BASE_DIR = Path(__file__).parent


def load_crop_config():
    with open(BASE_DIR / "crops.json", "r") as file:
        return json.load(file)


def get_heat_threshold(stage):
    crop = load_crop_config()["wheat"]
    thresholds = crop.get("heat_thresholds", {})

    return thresholds.get(stage)


def check_heat_risk(stage, forecast_tmax):
    """
    Check whether forecast Tmax exceeds the configured
    heat threshold for a sensitive wheat stage.
    """

    threshold = get_heat_threshold(stage)

    if threshold is None:
        return {
            "heat_risk": "LOW",
            "stage": stage,
            "threshold_c": None,
            "max_forecast_tmax_c": (
                max(forecast_tmax)
                if forecast_tmax
                else None
            ),
            "reason_code": "STAGE_NOT_HEAT_SENSITIVE"
        }

    if not forecast_tmax:
        return {
            "heat_risk": "UNKNOWN",
            "stage": stage,
            "threshold_c": threshold,
            "max_forecast_tmax_c": None,
            "reason_code": "NO_FORECAST_DATA"
        }

    maximum_temperature = max(forecast_tmax)

    if maximum_temperature >= threshold:
        return {
            "heat_risk": "HIGH",
            "stage": stage,
            "threshold_c": threshold,
            "max_forecast_tmax_c": maximum_temperature,
            "reason_code": "HEAT_THRESHOLD_EXCEEDED"
        }

    return {
        "heat_risk": "LOW",
        "stage": stage,
        "threshold_c": threshold,
        "max_forecast_tmax_c": maximum_temperature,
        "reason_code": "HEAT_THRESHOLD_NOT_EXCEEDED"
    }