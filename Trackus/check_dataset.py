
import pandas as pd
from pathlib import Path

file_path = Path("data/bus_trip_dataset.csv")

if not file_path.exists():
    print("ERROR: Dataset file not found.")
else:
    df = pd.read_csv(file_path)

    print("\n--- TRACKUS DATASET VALIDATION ---")
    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    print("\nMissing values:")
    print(df.isnull().sum().to_string())

    print("\nDuplicate rows:", df.duplicated().sum())

    print("\nTraffic condition counts:")
    print(df["traffic_condition"].value_counts().to_string())

    print("\nData type counts:")
    print(df["data_type"].value_counts().to_string())

    expected_rows = 300
    valid = (
        len(df) == expected_rows
        and df.isnull().sum().sum() == 0
        and df["bus_id"].nunique() == 10
    )

    print("\nValidation result:", "PASSED" if valid else "CHECK REQUIRED")
