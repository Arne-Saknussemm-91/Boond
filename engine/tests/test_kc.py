from engine.kc import get_kc, get_wheat_stage


def main():

    test_days = [
        1,
        15,
        16,
        20,
        40,
        41,
        90,
        91,
        120,
        121
    ]

    for day in test_days:

        stage = get_wheat_stage(day)
        kc = get_kc(day)

        print(
            f"Day {day:3d} | "
            f"Stage: {stage:12s} | "
            f"Kc: {kc:.3f}"
        )


if __name__ == "__main__":
    main()