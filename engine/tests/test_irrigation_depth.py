from engine.advisor import calculate_irrigation_depth


def main():

    # Normal case
    depth_1 = calculate_irrigation_depth(
        current_depletion=18.0,
        maximum_depth=60.0
    )

    print("Test 1")
    print(f"Depletion: 18.0 mm")
    print(f"Irrigation: {depth_1:.2f} mm")

    # Capped case
    depth_2 = calculate_irrigation_depth(
        current_depletion=75.0,
        maximum_depth=60.0
    )

    print()
    print("Test 2")
    print(f"Depletion: 75.0 mm")
    print(f"Irrigation: {depth_2:.2f} mm")

    # Already full
    depth_3 = calculate_irrigation_depth(
        current_depletion=0.0,
        maximum_depth=60.0
    )

    print()
    print("Test 3")
    print(f"Depletion: 0.0 mm")
    print(f"Irrigation: {depth_3:.2f} mm")


if __name__ == "__main__":
    main()