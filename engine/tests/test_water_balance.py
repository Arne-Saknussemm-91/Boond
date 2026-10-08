from engine.water_balance import (
    get_root_depth,
    calculate_taw,
    calculate_p,
    calculate_raw,
    calculate_kc_etc,
    calculate_ks,
    calculate_actual_etc,
    effective_rainfall,
    update_depletion
)


def main():

    day = 40
    soil = "loam"
    et0 = 5.0

    # -------------------------
    # Crop and soil calculations
    # -------------------------

    root_depth = get_root_depth(day)

    kc, etc = calculate_kc_etc(
        day,
        et0
    )

    taw = calculate_taw(
        soil,
        root_depth
    )

    p = calculate_p(etc)

    raw = calculate_raw(
        taw,
        p
    )

    # -------------------------
    # Start with HIGH depletion
    # -------------------------

    previous_depletion = 45.0

    rain = 0.0
    irrigation = 0.0

    effective_rain = effective_rainfall(
        rain,
        et0
    )

    # -------------------------
    # Calculate water stress
    # -------------------------

    ks = calculate_ks(
        previous_depletion,
        taw,
        p
    )

    actual_etc = calculate_actual_etc(
        etc,
        ks
    )

    # -------------------------
    # Update depletion
    # -------------------------

    depletion = update_depletion(
        previous_depletion,
        effective_rain,
        irrigation,
        actual_etc,
        taw
    )

    # -------------------------
    # Print results
    # -------------------------

    print("----- BOOND WATER STRESS TEST -----")
    print(f"Day:                 {day}")
    print(f"Soil:                {soil}")
    print(f"Root depth:          {root_depth:.3f} m")
    print(f"Kc:                  {kc:.3f}")
    print(f"ET0:                 {et0:.2f} mm")
    print(f"Potential ETc:       {etc:.2f} mm")
    print(f"TAW:                 {taw:.2f} mm")
    print(f"p:                   {p:.3f}")
    print(f"RAW:                 {raw:.2f} mm")
    print(f"Previous depletion:  {previous_depletion:.2f} mm")
    print(f"Ks:                  {ks:.3f}")
    print(f"Actual ETc:          {actual_etc:.2f} mm")
    print(f"Effective rain:      {effective_rain:.2f} mm")
    print(f"Irrigation:          {irrigation:.2f} mm")
    print(f"New depletion:       {depletion:.2f} mm")


if __name__ == "__main__":
    main()