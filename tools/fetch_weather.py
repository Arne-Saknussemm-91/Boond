"""
Download daily weather from Open-Meteo once and save it for the
season simulator (engine/simulate.py).

    python tools/fetch_weather.py --lat 30.90 --lon 75.85 \
        --start 2021-11-01 --end 2022-04-30 --out weather/ludhiana_2021_22.json

--source archive             ERA5 reanalysis (what actually happened)
--source historical-forecast archived forecasts (what the advisor would have seen)
"""

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path


URLS = {
    "archive": "https://archive-api.open-meteo.com/v1/archive",
    "historical-forecast": "https://historical-forecast-api.open-meteo.com/v1/forecast",
}

DAILY_FIELDS = {
    "et0_mm": "et0_fao_evapotranspiration",
    "rain_mm": "precipitation_sum",
    "tmax_c": "temperature_2m_max",
}


def fetch(lat, lon, start, end, source="archive"):
    query = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ",".join(DAILY_FIELDS.values()),
        "timezone": "Asia/Kolkata",
    })

    with urllib.request.urlopen(f"{URLS[source]}?{query}", timeout=60) as response:
        payload = json.load(response)

    daily = payload["daily"]

    return {
        "latitude": payload["latitude"],
        "longitude": payload["longitude"],
        "source": f"Open-Meteo {source}",
        "daily": {
            "date": daily["time"],
            **{
                key: [0.0 if value is None else value for value in daily[field]]
                for key, field in DAILY_FIELDS.items()
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--source", choices=URLS, default="archive")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    weather = fetch(args.lat, args.lon, args.start, args.end, args.source)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(weather, indent=2))

    print(f"Saved {len(weather['daily']['date'])} days to {out}")


if __name__ == "__main__":
    main()
