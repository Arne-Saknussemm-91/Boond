import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


def load_crop_config():
    with open(BASE_DIR / "crops.json", "r") as file:
        return json.load(file)


def get_wheat_stage(day_after_sowing):
    if day_after_sowing < 1:
        raise ValueError("day_after_sowing must be >= 1")

    crop = load_crop_config()["wheat"]

    phenology = crop["phenology"]

    initial_end = phenology["initial_days"]
    development_end = initial_end + phenology["development_days"]
    mid_end = development_end + phenology["mid_days"]
    total_days = (
        initial_end
        + phenology["development_days"]
        + phenology["mid_days"]
        + phenology["late_days"]
    )

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
    crop = load_crop_config()["wheat"]

    phenology = crop["phenology"]
    kc = crop["kc"]

    stage = get_wheat_stage(day_after_sowing)

    if stage == "post_harvest":
        return 0.0

    if stage == "initial":
        return kc["initial"]

    if stage == "mid":
        return kc["mid"]

    if stage == "development":
        stage_length = phenology["development_days"]

        start_day = phenology["initial_days"] + 1
        position = day_after_sowing - start_day

        fraction = position / (stage_length - 1)

        return linear_interpolation(
            kc["initial"],
            kc["mid"],
            fraction
        )

    if stage == "late":
        stage_length = phenology["late_days"]

        start_day = (
            phenology["initial_days"]
            + phenology["development_days"]
            + phenology["mid_days"]
            + 1
        )

        position = day_after_sowing - start_day

        fraction = position / (stage_length - 1)

        return linear_interpolation(
            kc["mid"],
            kc["end"],
            fraction
        )

    raise ValueError(f"Unknown stage: {stage}")