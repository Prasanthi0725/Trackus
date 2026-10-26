
import folium
import streamlit as st
from datetime import datetime, timedelta
from folium.plugins import PolyLineTextPath
from streamlit_folium import st_folium


BUS_STOPS = [
    {
        "bus_id": "BUS-01", "place": "Eluru",
        "lat": 16.7107, "lon": 81.0952,
        "distance_km": 60.0, "departure": "06:30",
    },
    {
        "bus_id": "BUS-02", "place": "Gudivada",
        "lat": 16.4355, "lon": 80.9950,
        "distance_km": 56.3, "departure": "07:00",
    },
    {
        "bus_id": "BUS-03", "place": "Guntur",
        "lat": 16.3067, "lon": 80.4365,
        "distance_km": 68.0, "departure": "06:00",
    },
    {
        "bus_id": "BUS-04", "place": "Kankipadu",
        "lat": 16.4530, "lon": 80.7670,
        "distance_km": 40.0, "departure": "07:30",
    },
    {
        "bus_id": "BUS-05", "place": "IBM",
        "lat": 16.5100, "lon": 80.6500,
        "distance_km": 35.0, "departure": "07:30",
    },
    {
        "bus_id": "BUS-06", "place": "Gannavaram",
        "lat": 16.5400, "lon": 80.8000,
        "distance_km": 26.0, "departure": "08:00",
    },
    {
        "bus_id": "BUS-07", "place": "Nuzvid",
        "lat": 16.7880, "lon": 80.8450,
        "distance_km": 20.0, "departure": "08:15",
    },
    {
        "bus_id": "BUS-08", "place": "Enikepadu",
        "lat": 16.5000, "lon": 80.6800,
        "distance_km": 24.0, "departure": "08:30",
    },
    {
        "bus_id": "BUS-09", "place": "Singh Nagar",
        "lat": 16.5400, "lon": 80.6400,
        "distance_km": 20.0, "departure": "08:30",
    },
    {
        "bus_id": "BUS-10", "place": "Nunna",
        "lat": 16.5700, "lon": 80.5800,
        "distance_km": 13.0, "departure": "08:45",
    },
]

# Approximate university-area coordinates.
# Verify the exact campus coordinates before real-world use.
COLLEGE = {
    "name": "Dr. RVR NRI University",
    "lat": 16.4400,
    "lon": 80.6200,
}

ROUTE_COLORS = [
    "blue", "green", "purple", "orange", "darkred",
    "cadetblue", "darkblue", "darkgreen", "pink", "gray",
]


def show_bus_map():
    """Display bus routes with directional arrows and journey details."""

    st.subheader("🗺️ Trackus - Bus Route Tracking")

    st.caption(
        "Demo routes with directional arrows. Lines are illustrative, "
        "not verified road routes. Bus GPS is not connected."
    )

    traffic_speeds = {
        "Light": 40.0,
        "Moderate": 30.0,
        "Heavy": 20.0,
    }

    traffic = st.selectbox(
        "Select traffic condition",
        list(traffic_speeds.keys()),
        index=1,
        key="map_traffic",
    )

    speed = traffic_speeds[traffic]

    bus_map = folium.Map(
        location=[COLLEGE["lat"], COLLEGE["lon"]],
        zoom_start=9,
        tiles="OpenStreetMap",
    )

    # University destination
    folium.Marker(
        location=[COLLEGE["lat"], COLLEGE["lon"]],
        tooltip="University Destination",
        popup=folium.Popup(
            f"<b>Destination:</b> {COLLEGE['name']}",
            max_width=300,
        ),
        icon=folium.Icon(
            color="red",
            icon="graduation-cap",
            prefix="fa",
        ),
    ).add_to(bus_map)

    # Draw each bus route toward the university.
    for index, bus in enumerate(BUS_STOPS):
        color = ROUTE_COLORS[index % len(ROUTE_COLORS)]

        duration = round(bus["distance_km"] / speed * 60)

        departure_time = datetime.strptime(
            bus["departure"], "%H:%M"
        )
        arrival_time = departure_time + timedelta(minutes=duration)

        departure_text = departure_time.strftime("%I:%M %p")
        arrival_text = arrival_time.strftime("%I:%M %p")

        start_point = [bus["lat"], bus["lon"]]
        end_point = [COLLEGE["lat"], COLLEGE["lon"]]

        # Illustrative straight-line connection.
        route = folium.PolyLine(
            locations=[start_point, end_point],
            color=color,
            weight=4,
            opacity=0.8,
            tooltip=(
                f"{bus['bus_id']}: {bus['distance_km']} km | "
                f"Assumed speed: {speed:.0f} km/h"
            ),
        ).add_to(bus_map)

        # Add repeating arrow symbols along the route.
        PolyLineTextPath(
            route,
            "➤",
            repeat=True,
            offset=7,
            attributes={
                "fill": color,
                "font-weight": "bold",
                "font-size": "18",
            },
        ).add_to(bus_map)

        # Add a distance and speed label near the route midpoint.
        midpoint = [
            (bus["lat"] + COLLEGE["lat"]) / 2,
            (bus["lon"] + COLLEGE["lon"]) / 2,
        ]

        label_html = f"""
        <div style="
            background:white;
            border:2px solid {color};
            border-radius:6px;
            padding:4px 7px;
            width:100px;
            text-align:center;
            font-family:Arial;
            font-size:11px;
            font-weight:bold;
            box-shadow:1px 1px 4px #777;
        ">
            {bus['distance_km']} km<br>
            {speed:.0f} km/h
        </div>
        """

        folium.Marker(
            location=midpoint,
            icon=folium.DivIcon(
                html=label_html,
                icon_size=(110, 45),
                icon_anchor=(55, 22),
            ),
            interactive=False,
        ).add_to(bus_map)

        # Clickable bus starting marker with full details.
        popup_html = f"""
        <div style="width:250px;font-family:Arial;">
            <h3 style="color:{color};">
                🚌 {bus['bus_id']} - {bus['place']}
            </h3>
            <hr>
            <b>Starting place:</b> {bus['place']}<br>
            <b>Destination:</b> {COLLEGE['name']}<br>
            <b>Distance:</b> {bus['distance_km']} km<br>
            <b>Departure:</b> {departure_text}<br>
            <b>Traffic:</b> {traffic}<br>
            <b>Assumed speed:</b> {speed:.0f} km/h<br>
            <b>Estimated duration:</b> {duration} minutes<br>
            <b>Estimated arrival:</b> {arrival_text}
            <hr>
            <small>Illustrative route; not live GPS data.</small>
        </div>
        """

        folium.Marker(
            location=start_point,
            tooltip=f"{bus['bus_id']} - {bus['place']}",
            popup=folium.Popup(
                popup_html,
                max_width=320,
            ),
            icon=folium.Icon(
                color="blue",
                icon="bus",
                prefix="fa",
            ),
        ).add_to(bus_map)

    st_folium(
        bus_map,
        width=None,
        height=600,
        use_container_width=True,
        key="trackus_bus_map",
    )

    st.markdown(
        "**Map legend:** 🔵 Bus starting points · "
        "🔴 University · ➤ Route direction"
    )

    st.info(
        f"Selected scenario: {traffic} traffic, "
        f"assumed speed {speed:.0f} km/h. "
        "Speed and route labels are illustrative estimates."
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Trackus Bus Route Map",
        page_icon="🚌",
        layout="wide",
    )
    st.title("Trackus - Intelligent Bus Tracking")
    show_bus_map()
