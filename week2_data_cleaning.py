
from pathlib import Path
import pandas as pd

# Load the dataset from the project folder
input_file = Path("deliveries.csv")
output_file = Path("deliveries_cleaned.csv")

if not input_file.exists():
    raise FileNotFoundError(
        "Please add your dataset as deliveries.csv "
        "before running this script."
    )

df = pd.read_csv(input_file)

print("Original dataset shape:", df.shape)
print("\nColumn names:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

# Remove exact duplicate rows
before = len(df)
df = df.drop_duplicates()
print("\nExact duplicate rows removed:", before - len(df))

# Convert timestamp columns if they exist
date_columns = [
    "dispatch_time",
    "promised_delivery_time",
    "actual_delivery_time",
]

for column in date_columns:
    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column], errors="coerce"
        )

# Convert numerical columns if they exist
numeric_columns = ["distance_km", "parcel_weight_kg"]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )
        df.loc[df[column] < 0, column] = float("nan")

# Calculate actual delivery duration when possible
if {"dispatch_time", "actual_delivery_time"}.issubset(df.columns):
    df["delivery_duration_hours"] = (
        df["actual_delivery_time"] - df["dispatch_time"]
    ).dt.total_seconds() / 3600

    df.loc[
        df["delivery_duration_hours"] < 0,
        "delivery_duration_hours"
    ] = float("nan")

# Report potential IQR outliers; do not remove automatically
report_lines = [
    f"Rows after exact duplicate removal: {len(df)}",
    f"Columns: {len(df.columns)}",
    "\nMissing values:\n" + df.isnull().sum().to_string(),
    "\nPotential IQR outliers:",
]

for column in df.select_dtypes(include="number").columns:
    values = df[column].dropna()
    if values.empty:
        continue

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1
    outliers = ((values < q1 - 1.5 * iqr) |
                (values > q3 + 1.5 * iqr)).sum()

    report_lines.append(f"{column}: {outliers}")

df.to_csv(output_file, index=False)
Path("data_quality_report.txt").write_text(
    "\n".join(report_lines), encoding="utf-8"
)

print("\nSaved:", output_file)
print("Saved: data_quality_report.txt")
