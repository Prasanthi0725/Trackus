
import csv
import random
from pathlib import Path

random.seed(42)

# Output folder and dataset file
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "bus_trip_dataset.csv"

# Known bus route information
BUSES = [
    ("BUS-01", "Eluru", 60.0, "06:30"),
    ("BUS-02", "Gudivada", 56.3, "07:00"),
    ("BUS-03", "Guntur", 68.0, "06:00"),
    ("BUS-04", "Kankipadu", 40.0, "07:30"),
    ("BUS-05", "IBM", 35.0, "07:30"),
    ("BUS-06", "Gannavaram", 26.0, "08:00"),
    ("BUS-07", "Nuzvid", 20.0, "08:15"),
    ("BUS-08", "Enikepadu", 24.0, "08:30"),
    ("BUS-09", "Singh Nagar", 20.0, "08:30"),
    ("BUS-10", "Nunna", 13.0, "08:45"),
]

# Illustrative assumptions for sample-data development only.
TRAFFIC_SPEEDS = {
    "Light": 40,
    "Moderate": 30,
    "Heavy": 20,
}

FIELDS = [
    "bus_id",
    "starting_place",
    "distance_km",
    "departure_time",
    "departure_hour",
    "traffic_condition",
    "assumed_speed_kmh",
    "trip_duration_minutes",
    "data_type",
]


def main():
    rows = []

    # Generate sample scenarios for code development.
    for bus_id, place, distance, departure in BUSES:
        hour, minute = map(int, departure.split(":"))
        departure_hour = hour + minute / 60

        for traffic, speed in TRAFFIC_SPEEDS.items():
            for _ in range(10):
                # Add illustrative variation to assumed speed.
                actual_speed = speed * random.uniform(0.85, 1.15)
                duration = round(distance / actual_speed * 60)

                rows.append({
                    "bus_id": bus_id,
                    "starting_place": place,
                    "distance_km": distance,
                    "departure_time": departure,
                    "departure_hour": round(departure_hour, 2),
                    "traffic_condition": traffic,
                    "assumed_speed_kmh": round(actual_speed, 2),
                    "trip_duration_minutes": duration,
                    "data_type": "SYNTHETIC_SAMPLE_NOT_REAL_TRIP",
                })

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("Dataset created successfully.")
    print("File:", OUTPUT_FILE.resolve())
    print("Number of sample rows:", len(rows))
    print("Data type: synthetic sample data, not real bus records.")


if __name__ == "__main__":
    main()
