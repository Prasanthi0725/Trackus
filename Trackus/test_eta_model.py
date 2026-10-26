
import joblib
import pandas as pd
from pathlib import Path

MODEL_FILE = Path("models/eta_model.pkl")

if not MODEL_FILE.exists():
    print("ERROR: Trained model file not found.")
else:
    model = joblib.load(MODEL_FILE)

    sample_bus = pd.DataFrame([{
        "bus_id": "BUS-01",
        "starting_place": "Eluru",
        "distance_km": 60.0,
        "departure_hour": 6.5,  
        "traffic_condition": "Moderate",
        "assumed_speed_kmh": 30.0,
    }])

    predicted_minutes = model.predict(sample_bus)[0]

    print("\n--- TRACKUS MODEL TEST ---")
    print("Bus: BUS-01")
    print("Starting place: Eluru")
    print("Distance: 60 km")
    print("Traffic: Moderate")
    print(f"Predicted travel duration: {predicted_minutes:.1f} minutes")
    print("Model loading and prediction: SUCCESS")
