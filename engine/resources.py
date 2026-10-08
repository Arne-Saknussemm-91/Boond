def irrigation_volume_litres(
    depth_mm,
    area_acres
):
    """
    Convert irrigation depth over an area into litres.

    1 mm over 1 acre ≈ 4046.86 litres.
    """

    litres_per_mm_per_acre = 4046.86

    return depth_mm * area_acres * litres_per_mm_per_acre


def irrigation_volume_m3(
    depth_mm,
    area_acres
):
    """
    Convert irrigation depth over an area into cubic metres.
    """

    return irrigation_volume_litres(
        depth_mm,
        area_acres
    ) / 1000.0


def pump_energy_kwh(
    volume_m3,
    lift_m,
    pump_efficiency
):
    """
    Estimate electrical energy required to pump water.

    Energy = volume * g * lift / (3600 * efficiency)
    """

    if pump_efficiency <= 0:
        raise ValueError("pump_efficiency must be greater than 0")

    gravity = 9.81

    return (
        volume_m3
        * gravity
        * lift_m
        / (3600 * pump_efficiency)
    )


def electricity_cost(
    energy_kwh,
    tariff_inr_per_kwh
):
    """
    Estimate electricity cost.
    """

    return energy_kwh * tariff_inr_per_kwh


def co2_emissions(
    energy_kwh,
    grid_factor_kg_per_kwh
):
    """
    Estimate CO2e emissions from electricity consumption.
    """

    return energy_kwh * grid_factor_kg_per_kwh