
import pandas as pd
import joblib

from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# File paths
DATA_FILE = Path("data/bus_trip_dataset.csv")
MODEL_DIR = Path("models")
MODEL_FILE = MODEL_DIR / "eta_model.pkl"


def main():
    # 1. Load dataset
    if not DATA_FILE.exists():
        print("ERROR: Dataset not found. Run prepare_dataset.py first.")
        return

    df = pd.read_csv(DATA_FILE)

    # 2. Select input features and prediction target
    features = [
        "bus_id",
        "starting_place",
        "distance_km",
        "departure_hour",
        "traffic_condition",
        "assumed_speed_kmh",
    ]

    X = df[features]
    y = df["trip_duration_minutes"]

    # 3. Separate training and testing data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # 4. Prepare categorical and numerical features
    categorical_features = [
        "bus_id",
        "starting_place",
        "traffic_condition",
    ]

    numerical_features = [
        "distance_km",
        "departure_hour",
        "assumed_speed_kmh",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            ("numerical", "passthrough", numerical_features),
        ]
    )

    # 5. Build the ML pipeline
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=100,
                    random_state=42,
                ),
            ),
        ]
    )

    # 6. Train the model
    model.fit(X_train, y_train)

    # 7. Evaluate on the test split
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    print("\n--- TRACKUS ETA MODEL RESULTS ---")
    print("Training rows:", len(X_train))
    print("Testing rows:", len(X_test))
    print(f"MAE: {mae:.2f} minutes")
    print(f"RMSE: {rmse:.2f} minutes")
    print(f"R² score: {r2:.3f}")

    # 8. Save the trained model
    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    print("\nModel saved to:", MODEL_FILE.resolve())
    print("NOTE: Results are based on synthetic sample data only.")


if __name__ == "__main__":
    main()
