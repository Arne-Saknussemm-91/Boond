from engine.resources import (
    irrigation_volume_litres,
    irrigation_volume_m3,
    pump_energy_kwh,
    electricity_cost,
    co2_emissions
)


def main():

    depth = 18.0
    area = 1.0
    lift = 30.0
    pump_efficiency = 0.40
    tariff = 8.0
    grid_factor = 0.70

    litres = irrigation_volume_litres(
        depth,
        area
    )

    volume = irrigation_volume_m3(
        depth,
        area
    )

    energy = pump_energy_kwh(
        volume,
        lift,
        pump_efficiency
    )

    cost = electricity_cost(
        energy,
        tariff
    )

    emissions = co2_emissions(
        energy,
        grid_factor
    )

    print("----- BOOND RESOURCE TEST -----")
    print(f"Irrigation depth:    {depth:.2f} mm")
    print(f"Area:                {area:.2f} acre")
    print(f"Water volume:        {litres:.2f} litres")
    print(f"Water volume:        {volume:.3f} m3")
    print(f"Pump lift:           {lift:.2f} m")
    print(f"Pump efficiency:     {pump_efficiency:.2f}")
    print(f"Energy:              {energy:.3f} kWh")
    print(f"Electricity cost:    Rs {cost:.2f}")
    print(f"CO2e:                {emissions:.3f} kg")


if __name__ == "__main__":
    main()