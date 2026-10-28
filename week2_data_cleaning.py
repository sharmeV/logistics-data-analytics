from pathlib import Path
import pandas as pd

# Input and output files
INPUT_FILE = Path("orders.xlsx")
OUTPUT_FILE = Path("orders_cleaned.csv")
REPORT_FILE = Path("data_quality_report.txt")

# Check that the Excel file exists
if not INPUT_FILE.exists():
    raise FileNotFoundError(
        "Place orders.xlsx in the same folder as this script."
    )

# Read all worksheets from the Excel workbook
sheets = pd.read_excel(INPUT_FILE, sheet_name=None)

all_data = []

for sheet_name, sheet_df in sheets.items():
    # Clean column-name spacing
    sheet_df.columns = [
        str(col).strip() for col in sheet_df.columns
    ]

    # Standardize time-window column name
    sheet_df = sheet_df.rename(
        columns={"TIME_WINDOW": "TIME WINDOW"}
    )

    # Track the original worksheet
    sheet_df["DAY"] = sheet_name
    all_data.append(sheet_df)

# Combine all worksheets
df = pd.concat(all_data, ignore_index=True)

# Initial data-quality checks
initial_rows = len(df)
missing_values = df.isnull().sum()
duplicate_rows = int(df.duplicated().sum())

# Remove exact duplicate records
df = df.drop_duplicates().copy()

# Convert selected columns to numeric where possible
numeric_columns = [
    "NODE_ID",
    "WEIGHT",
    "VOLUME",
    "SERVICE_TIME",
    "EAT",
    "LAT"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

# Flag negative values for investigation
negative_counts = {}

for col in ["WEIGHT", "VOLUME", "SERVICE_TIME"]:
    if col in df.columns:
        negative_counts[col] = int(
            (df[col] < 0).sum()
        )

# Identify potential outliers using IQR
outlier_counts = {}

for col in ["WEIGHT", "VOLUME", "SERVICE_TIME"]:
    if col not in df.columns:
        continue

    values = df[col].dropna()

    if values.empty:
        continue

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outlier_counts[col] = int(
        ((values < lower) | (values > upper)).sum()
    )

# Save cleaned dataset
df.to_csv(OUTPUT_FILE, index=False)

# Generate data-quality report
report = [
    "LOGISTICS DATA QUALITY REPORT",
    f"Worksheets processed: {len(sheets)}",
    f"Rows before duplicate removal: {initial_rows}",
    f"Duplicate rows removed: {duplicate_rows}",
    f"Rows after cleaning: {len(df)}",
    f"Columns: {df.columns.tolist()}",
    "",
    "Missing values before cleaning:",
    missing_values.to_string(),
    "",
    "Negative-value counts:",
    str(negative_counts),
    "",
    "Potential IQR outliers:",
    str(outlier_counts),
]

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("\n".join(report))
print(f"\nSaved: {OUTPUT_FILE}")
print(f"Saved: {REPORT_FILE}")

)

print("\nSaved:", output_file)
print("Saved: data_quality_report.txt")
