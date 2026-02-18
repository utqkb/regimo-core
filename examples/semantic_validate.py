from datetime import datetime, date
import sys
import yaml

def fail(msg):
    print(f"[SEMANTIC ERROR] {msg}")
    sys.exit(1)

data_file = sys.argv[1]

with open(data_file) as f:
    data = yaml.safe_load(f)

project_start = date.fromisoformat(data["project_start_date"])

for idx, record in enumerate(data["records"], start=1):
    record_id = record.get("sample_unique_id", f"record {idx}")

    # --- Temporal rules ---
    measurement_time = datetime.fromisoformat(
        record["measurement_time"].replace("Z", "+00:00")
    )
    calibration_date = date.fromisoformat(record["instrument_calibration_date"])

    if measurement_time.date() < project_start:
        fail(
            f"{record_id}: measurement time {measurement_time.date()} "
            f"is before project start date {project_start}"
        )

    if calibration_date > measurement_time.date():
        fail(
            f"{record_id}: calibration date {calibration_date} "
            f"is after measurement date {measurement_time.date()}"
        )

    # --- Unit-aware realism ---
    value = record["temperature_value"]
    unit = record["temperature_unit"]

    if unit == "Celsius":
        if not (10 <= value <= 40):
            fail(
                f"{record_id}: {value} °C outside realistic room range (10–40 °C)"
            )

    elif unit == "Kelvin":
        if not (283.15 <= value <= 313.15):
            fail(
                f"{record_id}: {value} K outside realistic room range (283.15–313.15 K)"
            )

print("No semantic violations found")
