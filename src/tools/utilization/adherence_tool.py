from pathlib import Path
import pandas as pd
from langchain_core.tools import tool
from datetime import datetime, timedelta


@tool
def check_dispatch_adherence():
    """
    Check if trucks were dispatched on planned date.
    """

    outputs_dir = Path(r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT\outputs")

    files = list(outputs_dir.glob("fsd_planning_output_*.xlsx"))
    if not files:
        return {"status": "failed", "message": "No planning output found"}

    latest_file = max(files, key=lambda x: x.stat().st_mtime)

    try:
        df = pd.read_excel(latest_file, sheet_name="dispatch_plan")
    except Exception as e:
        return {"status": "failed", "message": str(e)}

    df.columns = df.columns.str.strip().str.lower()

    # 🔹 Map columns
    col_map = {
        "plant": None,
        "destination": None,
        "trips": None,
        "cases": None
    }

    for col in df.columns:
        c = col.lower()

        if c == "plant":
            col_map["plant"] = col
        elif c in ["destination", "city"]:
            col_map["destination"] = col
        elif "trip" in c:
            col_map["trips"] = col
        elif "case" in c:
            col_map["cases"] = col

    for key, val in col_map.items():
        if val is None:
            return {"status": "failed", "message": f"Missing column for {key}"}

    base_date = datetime(2025, 10, 1)

    results = []

    for _, row in df.iterrows():
        plant = row[col_map["plant"]]
        dest = row[col_map["destination"]]
        trips = int(row[col_map["trips"]])

        for i in range(1, trips + 1):
            planned_date = base_date + timedelta(days=i - 1)

            # 🔥 Simulate actual date (some delayed)
            if i % 3 == 0:
                actual_date = planned_date + timedelta(days=2)  # delay
            else:
                actual_date = planned_date

            status = "ON_TIME" if actual_date == planned_date else "DELAYED"

            results.append({
                "truck_id": f"{plant}_{dest}_TRUCK_{i}",
                "planned_date": planned_date.strftime("%Y-%m-%d"),
                "actual_date": actual_date.strftime("%Y-%m-%d"),
                "status": status
            })

    return {
        "status": "success",
        "adherence": results[:25]
    }