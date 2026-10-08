import json
from pathlib import Path

from engine.kc import get_kc


BASE_DIR = Path(__file__).parent


def load_json(filename):
    with open(BASE_DIR / filename, "r") as file:
        return json.load(file)


def get_root_depth(day_after_sowing):
    """
    Calculate root depth for wheat.

    Root depth:
        0.30 m at sowing
        grows linearly to 1.00 m by the end of the crop
    """

    crop = load_json("crops.json")["wheat"]

    initial_depth = crop["root_depth"]["initial_m"]
    maximum_depth = crop["root_depth"]["maximum_m"]
    total_days = crop["total_days"]

    if day_after_sowing <= 1:
        return initial_depth

    if day_after_sowing >= total_days:
        return maximum_depth

    fraction = (day_after_sowing - 1) / (total_days - 1)

    return initial_depth + (
        maximum_depth - initial_depth
    ) * fraction


def get_soil_parameters(soil):
    """
    Return field capacity and wilting point
    for the selected soil.
    """

    soils = load_json("soils.json")

    if soil not in soils:
        raise ValueError(
            f"Unknown soil type: {soil}"
        )

    return soils[soil]


def calculate_taw(soil, root_depth_m):
    """
    Calculate Total Available Water (TAW) in mm.

    TAW = 1000 * (theta_FC - theta_WP) * Zr
    """

    params = get_soil_parameters(soil)

    theta_fc = params["theta_fc"]
    theta_wp = params["theta_wp"]

    return 1000 * (
        theta_fc - theta_wp
    ) * root_depth_m


def calculate_p(etc, p_table=0.55):
    """
    Calculate depletion fraction p.

    p = p_table + 0.04 * (5 - ETc)

    The result is limited to [0.1, 0.8].
    """

    p = p_table + 0.04 * (5 - etc)

    return max(0.1, min(0.8, p))


def calculate_raw(taw, p):
    """
    Calculate Readily Available Water (RAW).
    """

    return p * taw

def calculate_ks(depletion, taw, p):
    """
    Calculate the water-stress coefficient Ks.

    If depletion is within RAW:
        Ks = 1

    If depletion is greater than RAW:
        Ks decreases as the soil becomes drier.

    Ks is limited between 0 and 1.
    """
    raw = calculate_raw(taw, p)

    if depletion <= raw:
        return 1.0

    denominator = (1 - p) * taw

    if denominator <= 0:
        return 0.0

    ks = (taw - depletion) / denominator

    return max(0.0, min(1.0, ks))

def calculate_actual_etc(etc, ks):
    """
    Calculate stress-adjusted crop evapotranspiration.
    """
    return ks * etc

def calculate_kc_etc(day_after_sowing, et0):
    """
    Calculate Kc and crop evapotranspiration ETc.
    """

    kc = get_kc(day_after_sowing)

    etc = kc * et0

    return kc, etc


def effective_rainfall(rain, et0):
    """
    Rain below 0.2 * ET0 does not count as effective
    rainfall according to the specification.
    """

    threshold = 0.2 * et0

    if rain < threshold:
        return 0.0

    return rain


def update_depletion(
    previous_depletion,
    effective_rain,
    irrigation,
    actual_etc,
    taw
):
    """
    Update daily soil-water depletion.

    D(i) = D(i-1) - P_eff - I + actual_ETc

    Result is clamped between 0 and TAW.
    """
    depletion = (
        previous_depletion
        - effective_rain
        - irrigation
        + actual_etc
    )

    return max(0.0, min(taw, depletion))

def calculate_daily_balance(
    day_after_sowing,
    soil,
    et0,
    rain,
    irrigation,
    previous_depletion
):
    """
    Calculate the complete daily soil-water balance.

    Returns all important intermediate values so that
    the advisor can later use them for irrigation decisions.
    """

    # -------------------------
    # Crop calculations
    # -------------------------

    root_depth = get_root_depth(day_after_sowing)

    kc, potential_etc = calculate_kc_etc(
        day_after_sowing,
        et0
    )

    # -------------------------
    # Soil water capacity
    # -------------------------

    taw = calculate_taw(
        soil,
        root_depth
    )

    # -------------------------
    # Allowable depletion
    # -------------------------

    p = calculate_p(
        potential_etc
    )

    raw = calculate_raw(
        taw,
        p
    )

    # -------------------------
    # Water stress
    # -------------------------

    ks = calculate_ks(
        previous_depletion,
        taw,
        p
    )

    actual_etc = calculate_actual_etc(
        potential_etc,
        ks
    )

    # -------------------------
    # Rainfall
    # -------------------------

    effective_rain = effective_rainfall(
        rain,
        et0
    )

    # -------------------------
    # New depletion
    # -------------------------

    new_depletion = update_depletion(
        previous_depletion,
        effective_rain,
        irrigation,
        actual_etc,
        taw
    )

    return {
        "day_after_sowing": day_after_sowing,
        "soil": soil,
        "root_depth_m": root_depth,
        "kc": kc,
        "et0_mm": et0,
        "potential_etc_mm": potential_etc,
        "taw_mm": taw,
        "p": p,
        "raw_mm": raw,
        "previous_depletion_mm": previous_depletion,
        "ks": ks,
        "actual_etc_mm": actual_etc,
        "rain_mm": rain,
        "effective_rain_mm": effective_rain,
        "irrigation_mm": irrigation,
        "depletion_mm": new_depletion
    }