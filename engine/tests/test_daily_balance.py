from engine.water_balance import calculate_daily_balance


def print_result(title, result):

    print()
    print("=" * 50)
    print(title)
    print("=" * 50)

    for key, value in result.items():

        if isinstance(value, float):
            print(f"{key:25}: {value:.3f}")
        else:
            print(f"{key:25}: {value}")


def main():

    # --------------------------------
    # Test 1: Healthy soil condition
    # --------------------------------

    healthy = calculate_daily_balance(
        day_after_sowing=40,
        soil="loam",
        et0=5.0,
        rain=10.0,
        irrigation=0.0,
        previous_depletion=20.0
    )

    print_result(
        "TEST 1: HEALTHY FIELD",
        healthy
    )

    # --------------------------------
    # Test 2: Stressed soil condition
    # --------------------------------

    stressed = calculate_daily_balance(
        day_after_sowing=40,
        soil="loam",
        et0=5.0,
        rain=0.0,
        irrigation=0.0,
        previous_depletion=45.0
    )

    print_result(
        "TEST 2: STRESSED FIELD",
        stressed
    )


if __name__ == "__main__":
    main()