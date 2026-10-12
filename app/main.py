
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

# API URL
url = "https://data.tmd.go.th/api/WeatherToday/V2/?uid=api&ukey=api12345"

# Output directory inside the Docker container
OUTPUT_DIR = "/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    # Retrieve XML data from API
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    # Parse XML
    root = ET.fromstring(response.content)

    # Extract station data
    rows = []

    for station in root.findall(".//Station"):
        obs = station.find("Observation")

        rows.append({
            "WmoStationNumber": station.findtext("WmoStationNumber"),
            "StationNameThai": station.findtext("StationNameThai"),
            "StationNameEnglish": station.findtext("StationNameEnglish"),
            "Province": station.findtext("Province"),
            "Latitude": float(station.findtext("Latitude", default="0")),
            "Longitude": float(station.findtext("Longitude", default="0")),
            "DateTime": obs.findtext("DateTime") if obs is not None else None,
            "MeanSeaLevelPressure": obs.findtext("MeanSeaLevelPressure") if obs is not None else None,
            "Temperature": obs.findtext("Temperature") if obs is not None else None,
            "MaxTemperature": obs.findtext("MaxTemperature") if obs is not None else None,
            "DifferentFromMaxTemperature": obs.findtext("DifferentFromMaxTemperature") if obs is not None else None,
            "MinTemperature": obs.findtext("MinTemperature") if obs is not None else None,
            "DifferentFromMinTemperature": obs.findtext("DifferentFromMinTemperature") if obs is not None else None,
            "RelativeHumidity": obs.findtext("RelativeHumidity") if obs is not None else None,
            "WindDirection": obs.findtext("WindDirection") if obs is not None else None,
            "WindSpeed": obs.findtext("WindSpeed") if obs is not None else None,
            "Rainfall": obs.findtext("Rainfall") if obs is not None else None,
            "Source": url
        })

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Convert numeric columns safely
    numeric_cols = [
        "Latitude", "Longitude", "MeanSeaLevelPressure", "Temperature",
        "MaxTemperature", "DifferentFromMaxTemperature",
        "MinTemperature", "DifferentFromMinTemperature",
        "RelativeHumidity", "WindSpeed", "Rainfall"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Generate date-based filename using container local time
    weather_date = datetime.now().strftime("%Y%m%d")
    output_file = os.path.join(
        OUTPUT_DIR, f"Weather{weather_date}.xlsx"
    )

    # Export to Excel
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            sheet_name=weather_date,
            index=False
        )

    print(
        f"Successfully exported {len(df)} records to {output_file}",
        flush=True
    )

if __name__ == "__main__":
    main()
