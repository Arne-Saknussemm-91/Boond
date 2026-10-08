import json
from pathlib import Path


BASE_DIR = Path(__file__).parent


def load_crop_config():
    with open(BASE_DIR / "crops.json", "r") as file:
        return json.load(file)


def get_wheat_stage(day_after_sowing):
    """
    Return the wheat growth stage for a given day.

    day_after_sowing:
        1 = first day after sowing
    """

    if day_after_sowing < 1:
        raise ValueError("day_after_sowing must be >= 1")

    crop = load_crop_config()["wheat"]

    stages = crop["stages"]

    initial_end = stages["initial"]["days"]

    development_end = (
        initial_end +
        stages["development"]["days"]
    )

    mid_end = (
        development_end +
        stages["mid"]["days"]
    )

    total_days = crop["total_days"]

    if day_after_sowing <= initial_end:
        return "initial"

    if day_after_sowing <= development_end:
        return "development"

    if day_after_sowing <= mid_end:
        return "mid"

    if day_after_sowing <= total_days:
        return "late"

    return "post_harvest"


def linear_interpolation(start, end, fraction):
    return start + (end - start) * fraction


def get_kc(day_after_sowing):
    """
    Calculate crop coefficient Kc for wheat.
    """

    crop = load_crop_config()["wheat"]
    stages = crop["stages"]

    stage = get_wheat_stage(day_after_sowing)

    if stage == "post_harvest":
        return 0.0

    if stage == "initial":
        return stages["initial"]["kc_start"]

    if stage == "mid":
        return stages["mid"]["kc_start"]

    if stage == "development":

        start_day = stages["initial"]["days"] + 1
        stage_length = stages["development"]["days"]

        position = day_after_sowing - start_day

        fraction = position / (stage_length - 1)

        return linear_interpolation(
            stages["development"]["kc_start"],
            stages["development"]["kc_end"],
            fraction
        )

    if stage == "late":

        start_day = (
            stages["initial"]["days"]
            + stages["development"]["days"]
            + stages["mid"]["days"]
            + 1
        )

        stage_length = stages["late"]["days"]

        position = day_after_sowing - start_day

        fraction = position / (stage_length - 1)

        return linear_interpolation(
            stages["late"]["kc_start"],
            stages["late"]["kc_end"],
            fraction
        )

    raise ValueError(f"Unknown stage: {stage}")