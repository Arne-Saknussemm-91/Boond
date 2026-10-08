from engine.advisor import decide_irrigation


def run_test(
    name,
    current_depletion,
    raw,
    future_etc,
    future_rain,
    rain_probability
):

    result = decide_irrigation(
        current_depletion=current_depletion,
        raw=raw,
        future_etc=future_etc,
        future_rain=future_rain,
        rain_probability=rain_probability
    )

    print()
    print("=" * 50)
    print(name)
    print("=" * 50)

    print(f"Action:        {result['action']}")
    print(f"Crossing day:  {result['crossing_day']}")
    print(f"Reason:        {result['reason_code']}")


def main():

    # -----------------------------------------
    # TEST 1: Healthy field
    # -----------------------------------------

    run_test(
        name="TEST 1: HEALTHY FIELD",
        current_depletion=20.0,
        raw=35.0,
        future_etc=[5.0, 5.0, 5.0],
        future_rain=[0.0, 0.0, 0.0],
        rain_probability=0.0
    )

    # -----------------------------------------
    # TEST 2: Needs irrigation soon
    # -----------------------------------------

    run_test(
        name="TEST 2: IRRIGATION NEEDED",
        current_depletion=30.0,
        raw=35.0,
        future_etc=[5.0, 5.0, 5.0],
        future_rain=[0.0, 0.0, 0.0],
        rain_probability=0.0
    )

    # -----------------------------------------
    # TEST 3: Rain is expected
    # -----------------------------------------

    run_test(
        name="TEST 3: RAIN EXPECTED",
        current_depletion=30.0,
        raw=35.0,
        future_etc=[5.0, 5.0, 5.0],
        future_rain=[0.0, 10.0, 0.0],
        rain_probability=0.90
    )

    # -----------------------------------------
    # TEST 4: Rain uncertain
    # -----------------------------------------

    run_test(
        name="TEST 4: UNCERTAIN RAIN",
        current_depletion=30.0,
        raw=35.0,
        future_etc=[5.0, 5.0, 5.0],
        future_rain=[0.0, 10.0, 0.0],
        rain_probability=0.40
    )

    # -----------------------------------------
    # TEST 5: Rain before RAW crossing
    # -----------------------------------------

    run_test(
        name="TEST 5: RAIN BEFORE RAW CROSSING",
        current_depletion=25.0,
        raw=35.0,
        future_etc=[5.0, 5.0, 5.0],
        future_rain=[0.0, 15.0, 0.0],
        rain_probability=0.90
    )

    # -----------------------------------------
    # TEST 6: Rain after RAW crossing
    # -----------------------------------------

    run_test(
        name="TEST 6: RAIN AFTER RAW CROSSING",
        current_depletion=30.0,
        raw=35.0,
        future_etc=[5.0, 5.0, 5.0],
        future_rain=[0.0, 0.0, 15.0],
        rain_probability=0.90
    )


if __name__ == "__main__":
    main()