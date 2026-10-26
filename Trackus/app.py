
import math
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
import folium
import matplotlib.pyplot as plt

from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Trackus - Intelligent Bus Tracking",
    page_icon="🚌",
    layout="wide",
)

st.title("🚌 Trackus")
st.subheader("Intelligent Bus Tracking & Commute Route Optimization System")

st.write(
    "Track college buses, simulate their movement toward the college, "
    "monitor bus status, and estimate journey duration using a machine "
    "learning model."
)

st.caption(
    "Demo application: bus locations and movement are simulated. "
    "They are not live GPS locations."
)


# =========================================================
# 2. PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "eta_model.pkl"


# =========================================================
# 3. BUS INFORMATION
# =========================================================

BUS_CONFIG = {
    "BUS-01": {
        "starting_place": "Eluru",
        "distance_km": 60.0,
        "departure": "6:30 AM",
    },
    "BUS-02": {
        "starting_place": "Gudivada",
        "distance_km": 56.3,
        "departure": "7:00 AM",
    },
    "BUS-03": {
        "starting_place": "Guntur",
        "distance_km": 68.0,
        "departure": "6:00 AM",
    },
    "BUS-04": {
        "starting_place": "Kankipadu",
        "distance_km": 40.0,
        "departure": "7:30 AM",
    },
    "BUS-05": {
        "starting_place": "IBM",
        "distance_km": 35.0,
        "departure": "7:30 AM",
    },
    "BUS-06": {
        "starting_place": "Gannavaram",
        "distance_km": 26.0,
        "departure": "8:00 AM",
    },
    "BUS-07": {
        "starting_place": "Nuzvid",
        "distance_km": 20.0,
        "departure": "8:15 AM",
    },
    "BUS-08": {
        "starting_place": "Enikepadu",
        "distance_km": 24.0,
        "departure": "8:30 AM",
    },
    "BUS-09": {
        "starting_place": "Singh Nagar",
        "distance_km": 20.0,
        "departure": "8:30 AM",
    },
    "BUS-10": {
        "starting_place": "Nunna",
        "distance_km": 13.0,
        "departure": "8:45 AM",
    },
}

BUS_COORDINATES = {
    "BUS-01": (16.7107, 81.0952),
    "BUS-02": (16.4355, 80.9950),
    "BUS-03": (16.3067, 80.4365),
    "BUS-04": (16.4530, 80.7670),
    "BUS-05": (16.5100, 80.6500),
    "BUS-06": (16.5400, 80.8000),
    "BUS-07": (16.7880, 80.8450),
    "BUS-08": (16.5000, 80.6800),
    "BUS-09": (16.5400, 80.6400),
    "BUS-10": (16.5700, 80.5800),
}

# Approximate illustrative college location.
COLLEGE_COORDINATES = (16.4400, 80.6200)

TRAFFIC_SPEEDS = {
    "Light": 40.0,
    "Moderate": 30.0,
    "Heavy": 20.0,
}


# =========================================================
# 4. LOAD MACHINE LEARNING MODEL
# =========================================================

@st.cache_resource
def load_eta_model(model_path):
    return joblib.load(model_path)


model = None

if MODEL_PATH.exists():
    try:
        model = load_eta_model(str(MODEL_PATH))
    except Exception as error:
        st.error(f"Could not load the ETA model: {error}")
else:
    st.warning(
        "ETA model file was not found. Make sure "
        "'models/eta_model.pkl' exists inside your project folder."
    )


# =========================================================
# 5. INITIALIZE SESSION STATE
# =========================================================

def initialize_simulated_positions():
    if "simulated_positions" not in st.session_state:
        st.session_state["simulated_positions"] = dict(
            BUS_COORDINATES
        )

    if "started_buses" not in st.session_state:
        st.session_state["started_buses"] = set()

    if "last_auto_tick" not in st.session_state:
        st.session_state["last_auto_tick"] = None


initialize_simulated_positions()


# =========================================================
# 6. DISTANCE CALCULATION
# =========================================================

def calculate_distance_km(position1, position2):
    """Calculate straight-line distance using the Haversine formula."""

    lat1, lon1 = position1
    lat2, lon2 = position2

    radius = 6371.0

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    a = max(0.0, min(1.0, a))

    return 2 * radius * math.asin(math.sqrt(a))


# =========================================================
# 7. BUS STATUS
# =========================================================

def get_bus_status(bus_id, current_position):
    if bus_id not in st.session_state["started_buses"]:
        return "🟡 Not Started"

    distance = calculate_distance_km(
        current_position,
        COLLEGE_COORDINATES,
    )

    if distance <= 1.0:
        return "🟢 Arrived"

    if distance <= 5.0:
        return "🟠 Arriving Soon"

    return "🔵 On Track"


# =========================================================
# 8. START SELECTED BUSES
# =========================================================

def start_selected_buses(bus_ids):
    started_count = 0
    already_started_count = 0
    arrived_count = 0

    for bus_id in bus_ids:
        position = st.session_state[
            "simulated_positions"
        ][bus_id]

        distance = calculate_distance_km(
            position,
            COLLEGE_COORDINATES,
        )

        if distance <= 1.0:
            st.session_state["started_buses"].add(bus_id)
            arrived_count += 1

        elif bus_id in st.session_state["started_buses"]:
            already_started_count += 1

        else:
            st.session_state["started_buses"].add(bus_id)
            started_count += 1

    return started_count, already_started_count, arrived_count


# =========================================================
# 9. SIMULATE BUS MOVEMENT
# =========================================================

def simulate_bus_movement(bus_ids):
    """
    Move each started bus 10% closer to the college.
    This is illustrative movement, not road-based navigation.
    """

    if isinstance(bus_ids, str):
        bus_ids = [bus_ids]

    moved_count = 0
    arrived_count = 0
    not_started = 0

    positions = st.session_state["simulated_positions"]

    for bus_id in bus_ids:
        if bus_id not in st.session_state["started_buses"]:
            not_started += 1
            continue

        current_lat, current_lon = positions[bus_id]

        college_lat, college_lon = COLLEGE_COORDINATES

        current_position = (current_lat, current_lon)

        distance = calculate_distance_km(
            current_position,
            COLLEGE_COORDINATES,
        )

        # Stop movement for buses already at the college.
        if distance <= 1.0:
            positions[bus_id] = COLLEGE_COORDINATES
            arrived_count += 1
            continue

        # Move 10% of the remaining coordinate difference.
        new_lat = current_lat + (
            college_lat - current_lat
        ) * 0.10

        new_lon = current_lon + (
            college_lon - current_lon
        ) * 0.10

        new_position = (new_lat, new_lon)

        new_distance = calculate_distance_km(
            new_position,
            COLLEGE_COORDINATES,
        )

        # Snap the bus to the destination when close enough.
        if new_distance <= 1.0:
            positions[bus_id] = COLLEGE_COORDINATES
            arrived_count += 1
        else:
            positions[bus_id] = new_position
            moved_count += 1

    st.session_state["simulated_positions"] = positions

    return moved_count, arrived_count, not_started


# =========================================================
# 10. ETA MODEL FUNCTIONS
# =========================================================

def parse_departure_hour(departure):
    parsed_time = datetime.strptime(
        departure,
        "%I:%M %p",
    )

    return parsed_time.hour + parsed_time.minute / 60.0


def predict_trip_duration(
    bus_id,
    traffic_condition,
    assumed_speed_kmh,
):
    if model is None:
        return None

    config = BUS_CONFIG[bus_id]

    features = pd.DataFrame(
        [
            {
                "bus_id": bus_id,
                "starting_place": config["starting_place"],
                "distance_km": config["distance_km"],
                "departure_hour": parse_departure_hour(
                    config["departure"]
                ),
                "traffic_condition": traffic_condition,
                "assumed_speed_kmh": assumed_speed_kmh,
            }
        ]
    )

    prediction = model.predict(features)

    return max(0.0, float(prediction[0]))


def get_estimated_arrival(
    bus_id,
    traffic_condition,
    assumed_speed_kmh,
):
    duration = predict_trip_duration(
        bus_id,
        traffic_condition,
        assumed_speed_kmh,
    )

    if duration is None:
        return None, None

    config = BUS_CONFIG[bus_id]

    departure_time = datetime.strptime(
        config["departure"],
        "%I:%M %p",
    )

    # Display today's schedule-based estimated arrival time.
    today = datetime.now().date()

    departure_datetime = datetime.combine(
        today,
        departure_time.time(),
    )

    arrival_datetime = departure_datetime + timedelta(
        minutes=duration
    )

    return duration, arrival_datetime


# =========================================================
# 11. SEARCH AND TRAFFIC SETTINGS
# =========================================================

st.sidebar.header("🔎 Search and Settings")

search_text = st.sidebar.text_input(
    "Search by bus ID or starting place",
    placeholder="Example: BUS-01 or Eluru",
)

traffic_condition = st.sidebar.selectbox(
    "Assumed traffic condition",
    ["Light", "Moderate", "Heavy"],
    index=1,
)

assumed_speed = TRAFFIC_SPEEDS[traffic_condition]

all_bus_ids = list(BUS_CONFIG.keys())

if search_text.strip():
    search_lower = search_text.strip().lower()

    filtered_bus_ids = [
        bus_id
        for bus_id, config in BUS_CONFIG.items()
        if search_lower in bus_id.lower()
        or search_lower in config["starting_place"].lower()
    ]
else:
    filtered_bus_ids = all_bus_ids.copy()


# =========================================================
# 12. INDIVIDUAL BUS CONTROLS
# =========================================================

st.header("🎮 Individual Bus Controls")

if not filtered_bus_ids:
    st.warning("No buses match your search.")
else:
    selected_bus = st.selectbox(
        "Select a bus",
        filtered_bus_ids,
        key="individual_bus_select",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "▶️ Start This Bus",
            use_container_width=True,
        ):
            started, already_started, arrived = (
                start_selected_buses([selected_bus])
            )

            if started:
                st.success(f"{selected_bus} started.")

            if already_started:
                st.info(f"{selected_bus} has already started.")

            if arrived:
                st.info(f"{selected_bus} has already arrived.")

    with col2:
        if st.button(
            "➡️ Move This Bus 10%",
            use_container_width=True,
        ):
            if selected_bus not in st.session_state["started_buses"]:
                st.warning("Start this bus before moving it.")
            else:
                moved, arrived, _ = simulate_bus_movement(
                    [selected_bus]
                )

                if moved:
                    st.success(f"{selected_bus} moved closer to the college.")

                if arrived:
                    st.success(f"{selected_bus} has arrived at the college.")


# =========================================================
# 13. MULTI-BUS CONTROLS
# =========================================================

st.header("🚌 Multiple Bus Controls")

selected_buses = st.multiselect(
    "Select two or more buses",
    options=filtered_bus_ids,
    default=[],
    key="multiple_bus_select",
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(
        "▶️ Start Selected Buses",
        use_container_width=True,
    ):
        if not selected_buses:
            st.warning("Please select at least one bus.")
        else:
            started, already_started, arrived = (
                start_selected_buses(selected_buses)
            )

            st.success(
                f"Newly started: {started} | "
                f"Already started: {already_started} | "
                f"Already arrived: {arrived}"
            )

with col2:
    if st.button(
        "➡️ Move Selected 10%",
        use_container_width=True,
    ):
        if not selected_buses:
            st.warning("Please select at least one bus.")
        else:
            moved, arrived, not_started = (
                simulate_bus_movement(selected_buses)
            )

            st.info(
                f"Moved: {moved} | Arrived: {arrived} | "
                f"Not started: {not_started}"
            )

with col3:
    if st.button(
        "🔄 Reset All Buses",
        use_container_width=True,
    ):
        st.session_state["simulated_positions"] = dict(
            BUS_COORDINATES
        )

        st.session_state["started_buses"] = set()
        st.session_state["last_auto_tick"] = None

        st.rerun()


# =========================================================
# 14. AUTOMATIC MOVEMENT AND LIVE REFRESH
# =========================================================

st.header("⏱️ Automatic Bus Tracking")

auto_mode = st.checkbox(
    "Enable automatic bus movement and live dashboard refresh",
    value=False,
    key="auto_bus_mode",
)

if auto_mode:
    st.info(
        "Automatic refresh is enabled. Every 5 seconds, "
        "started buses move toward the college."
    )

    # This counter changes on each timed refresh.
    auto_tick = st_autorefresh(
        interval=5000,
        limit=None,
        key="trackus_auto_refresh",
    )

    previous_tick = st.session_state.get("last_auto_tick")

    # Initialize the counter without moving buses immediately.
    if previous_tick is None:
        st.session_state["last_auto_tick"] = auto_tick

    # Only move buses when the timed refresh counter changes.
    elif auto_tick != previous_tick:
        st.session_state["last_auto_tick"] = auto_tick

        active_bus_ids = list(
            st.session_state["started_buses"]
        )

        if active_bus_ids:
            simulate_bus_movement(active_bus_ids)

else:
    st.session_state["last_auto_tick"] = None
    st.caption("Automatic movement is paused.")


# =========================================================
# 15. DASHBOARD SUMMARY METRICS
# =========================================================

st.header("📊 Live Dashboard")

positions = st.session_state["simulated_positions"]

statuses = {
    bus_id: get_bus_status(bus_id, positions[bus_id])
    for bus_id in all_bus_ids
}

total_buses = len(all_bus_ids)

not_started_count = sum(
    status == "🟡 Not Started"
    for status in statuses.values()
)

on_track_count = sum(
    status == "🔵 On Track"
    for status in statuses.values()
)

arriving_soon_count = sum(
    status == "🟠 Arriving Soon"
    for status in statuses.values()
)

arrived_count = sum(
    status == "🟢 Arrived"
    for status in statuses.values()
)

m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Total Buses", total_buses)
m2.metric("Not Started", not_started_count)
m3.metric("On Track", on_track_count)
m4.metric("Arriving Soon", arriving_soon_count)
m5.metric("Arrived", arrived_count)

st.caption(
    f"Last dashboard render: {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}"
)


# =========================================================
# 16. MAP DISPLAY
# =========================================================

st.header("🗺️ Bus Tracking Map")

map_options = ["All Buses"] + all_bus_ids

map_selection = st.selectbox(
    "Choose which buses to display on the map",
    map_options,
    key="map_bus_selection",
)

bus_map = folium.Map(
    location=COLLEGE_COORDINATES,
    zoom_start=10,
    control_scale=True,
)

# College destination marker.
folium.Marker(
    location=COLLEGE_COORDINATES,
    popup="Dr. RVR NRI University - Destination",
    tooltip="College Destination",
    icon=folium.Icon(
        color="red",
        icon="flag",
    ),
).add_to(bus_map)

folium.Circle(
    location=COLLEGE_COORDINATES,
    radius=1000,
    color="red",
    fill=True,
    fill_opacity=0.10,
    tooltip="Illustrative 1 km arrival zone",
).add_to(bus_map)

if map_selection == "All Buses":
    buses_to_display = all_bus_ids
else:
    buses_to_display = [map_selection]

for bus_id in buses_to_display:
    position = positions[bus_id]
    config = BUS_CONFIG[bus_id]

    status = statuses[bus_id]

    distance_to_college = calculate_distance_km(
        position,
        COLLEGE_COORDINATES,
    )

    # Offset arrived bus markers slightly so they do not overlap.
    marker_position = position

    if status == "🟢 Arrived":
        offset = all_bus_ids.index(bus_id)

        marker_position = (
            COLLEGE_COORDINATES[0] + 0.001 * (offset + 1),
            COLLEGE_COORDINATES[1] + 0.001 * (offset + 1),
        )

    if status == "🟢 Arrived":
        marker_color = "green"
    elif status == "🟠 Arriving Soon":
        marker_color = "orange"
    elif status == "🟡 Not Started":
        marker_color = "gray"
    else:
        marker_color = "blue"

    popup_text = (
        f"<b>{bus_id}</b><br>"
        f"Starting Place: {config['starting_place']}<br>"
        f"Status: {status}<br>"
        f"Distance to College (straight line): "
        f"{distance_to_college:.2f} km<br>"
        f"Scheduled Journey Distance: "
        f"{config['distance_km']:.1f} km<br>"
        f"Departure: {config['departure']}"
    )

    folium.Marker(
        location=marker_position,
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"{bus_id} - {status}",
        icon=folium.Icon(
            color=marker_color,
            icon="bus",
            prefix="fa",
        ),
    ).add_to(bus_map)

    # Illustrative straight-line connection, not a road route.
    folium.PolyLine(
        locations=[
            position,
            COLLEGE_COORDINATES,
        ],
        color=marker_color,
        weight=2,
        opacity=0.55,
        dash_array="5, 8",
    ).add_to(bus_map)

st_folium(
    bus_map,
    use_container_width=True,
    height=550,
    key="trackus_bus_map",
)


# =========================================================
# 17. BUS STATUS AND LOCATION TABLE
# =========================================================

st.header("📍 Bus Status and Locations")

bus_rows = []

for bus_id in all_bus_ids:
    config = BUS_CONFIG[bus_id]
    lat, lon = positions[bus_id]

    distance_to_college = calculate_distance_km(
        positions[bus_id],
        COLLEGE_COORDINATES,
    )

    bus_rows.append(
        {
            "Bus ID": bus_id,
            "Starting Place": config["starting_place"],
            "Scheduled Distance (km)": config["distance_km"],
            "Departure": config["departure"],
            "Status": statuses[bus_id],
            "Latitude": round(lat, 6),
            "Longitude": round(lon, 6),
            "Straight-Line Distance to College (km)": round(
                distance_to_college,
                2,
            ),
        }
    )

bus_df = pd.DataFrame(bus_rows)

if search_text.strip():
    search_lower = search_text.strip().lower()

    bus_df = bus_df[
        bus_df["Bus ID"].str.lower().str.contains(
            search_lower,
            regex=False,
        )
        | bus_df["Starting Place"].str.lower().str.contains(
            search_lower,
            regex=False,
        )
    ]

st.dataframe(
    bus_df,
    use_container_width=True,
    hide_index=True,
)


# =========================================================
# 18. MACHINE LEARNING ETA PREDICTIONS
# =========================================================

st.header("🤖 Machine Learning ETA Predictions")

st.write(
    "The model estimates total journey duration using the "
    "configured starting place, scheduled distance, departure time, "
    "assumed traffic condition, and assumed speed."
)

st.caption(
    "Predictions are based on synthetic training data. "
    "They are not verified live GPS arrival times."
)

if model is not None:
    eta_rows = []

    for bus_id in all_bus_ids:
        config = BUS_CONFIG[bus_id]

        duration, estimated_arrival = get_estimated_arrival(
            bus_id,
            traffic_condition,
            assumed_speed,
        )

        eta_rows.append(
            {
                "Bus ID": bus_id,
                "Starting Place": config["starting_place"],
                "Traffic": traffic_condition,
                "Assumed Speed (km/h)": assumed_speed,
                "Predicted Trip Duration (minutes)": (
                    round(duration, 1)
                    if duration is not None
                    else None
                ),
                "Scheduled Departure": config["departure"],
                "Estimated Arrival (schedule-based)": (
                    estimated_arrival.strftime("%I:%M %p")
                    if estimated_arrival is not None
                    else "Unavailable"
                ),
            }
        )

    eta_df = pd.DataFrame(eta_rows)

    st.dataframe(
        eta_df,
        use_container_width=True,
        hide_index=True,
    )

    # Plot predicted journey duration.
    if not eta_df.empty:
        chart_df = eta_df.set_index("Bus ID")[
            "Predicted Trip Duration (minutes)"
        ]

        st.subheader("Predicted Journey Duration by Bus")

        fig, ax = plt.subplots(figsize=(10, 4))

        chart_df.plot(
            kind="bar",
            ax=ax,
        )

        ax.set_xlabel("Bus ID")
        ax.set_ylabel("Predicted Duration (minutes)")
        ax.set_title("Model-Predicted Total Journey Duration")
        ax.tick_params(axis="x", rotation=45)

        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

else:
    st.warning(
        "ETA predictions are unavailable because the model "
        "could not be loaded."
    )


# =========================================================
# 19. PROJECT LIMITATIONS
# =========================================================

with st.expander("ℹ️ About the simulation and its limitations"):
    st.markdown(
        """
        - **Simulated locations:** Bus coordinates are illustrative,
          not actual GPS readings.
        - **Illustrative movement:** Buses move in a straight line
          toward the college when movement is triggered.
        - **Map lines:** Dashed lines are straight-line connections,
          not verified road routes.
        - **Distance values:** Scheduled journey distances are
          supplied configuration values and do not change when
          simulated bus markers move.
        - **ETA predictions:** The machine learning model was trained
          on synthetic data. Real-world accuracy has not been verified.
        - **Traffic:** Traffic condition and speed are user-selected
          assumptions, not live traffic measurements.
        - **Arrival estimates:** These are schedule-based estimates,
          not GPS-based live ETAs.
        """
    )

st.caption(
    "Trackus | Academic project prototype | "
    "Real-time GPS integration can be added in a future version."
)
