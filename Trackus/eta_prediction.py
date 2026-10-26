
from datetime import datetime, timedelta

COLLEGE = "Dr. RVR NRI University"
AVERAGE_SPEED_KMH = 30

BUSES = [
    {
        "bus_id": "BUS-01",
        "starting_place": "Eluru",
        "distance_km": 60.0,
        "departure_time": "06:30",
    },
    {
        "bus_id": "BUS-02",
        "starting_place": "Gudivada",
        "distance_km": 56.3,
        "departure_time": "07:00",
    },
    {
        "bus_id": "BUS-03",
        "starting_place": "Guntur",
        "distance_km": 68.0,
        "departure_time": "06:00",
    },
    {
        "bus_id": "BUS-04",
        "starting_place": "Kankipadu",
        "distance_km": 40.0,
        "departure_time": "07:30",
    },
    {
        "bus_id": "BUS-05",
        "starting_place": "IBM",
        "distance_km": 35.0,
        "departure_time": "07:30",
    },
    {
        "bus_id": "BUS-06",
        "starting_place": "Gannavaram",
        "distance_km": 26.0,
        "departure_time": "08:00",
    },
    {
        "bus_id": "BUS-07",
        "starting_place": "Nuzvid",
        "distance_km": 20.0,
        "departure_time": "08:15",
    },
    {
        "bus_id": "BUS-08",
        "starting_place": "Enikepadu",
        "distance_km": 24.0,
        "departure_time": "08:30",
    },
    {
        "bus_id": "BUS-09",
        "starting_place": "Singh Nagar",
        "distance_km": 20.0,
        "departure_time": "08:30",
    },
    {
        "bus_id": "BUS-10",
        "starting_place": "Nunna",
        "distance_km": 13.0,
        "departure_time": "08:45",
    },
]


def predict_eta(bus, average_speed=AVERAGE_SPEED_KMH):
    """Calculate a baseline travel-time estimate."""
    if average_speed <= 0:
        raise ValueError("Average speed must be positive.")

    travel_minutes = round(
        bus["distance_km"] / average_speed * 60
    )

    departure = datetime.strptime(
        bus["departure_time"], "%H:%M"
    )

    arrival = departure + timedelta(minutes=travel_minutes)

    return {
        **bus,
        "estimated_minutes": travel_minutes,
        "estimated_arrival": arrival.strftime("%I:%M %p"),
        "destination": COLLEGE,
        "prediction_type": "Baseline estimate",
    }


def predict_all_buses():
    """Calculate ETA estimates for all buses."""
    return [predict_eta(bus) for bus in BUSES]


if __name__ == "__main__":
    print("Destination:", COLLEGE)
    print("Assumed average speed:", AVERAGE_SPEED_KMH, "km/h")
    print("-" * 60)

    for bus in predict_all_buses():
        print(
            f"{bus['bus_id']} | "
            f"{bus['starting_place']} | "
            f"{bus['distance_km']} km | "
            f"Travel: {bus['estimated_minutes']} min | "
            f"Arrival: {bus['estimated_arrival']}"
        )
