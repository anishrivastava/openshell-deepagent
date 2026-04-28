import pandas as pd
from langchain_core.tools import tool
from datetime import datetime, timedelta
from pathlib import Path


# =========================
# 🔥 CONTEXT LOADER
# =========================
def load_truck_context():

    context = {
        "start_date": "2025-10-01"   # fallback (important for demo)
    }

    path = Path("skills/truck_schedule/context.md")

    if not path.exists():
        return context

    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip().lower()

                if "start_date" in line:
                    context["start_date"] = line.split("=")[1].strip()

    except Exception as e:
        print("Context error:", e)

    return context


# =========================
# 🔥 MAIN TOOL
# =========================
@tool
def create_truck_schedule(data: dict):
    """
    Create truck schedule using dispatch plan data (NOW CONTEXT-DRIVEN)
    """

    # =========================
    # VALIDATION
    # =========================
    if not data or "dispatch" not in data:
        return {"status": "failed", "message": "No dispatch data received"}

    df = pd.DataFrame(data.get("dispatch", []))

    # 🔹 Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # =========================
    # 🔥 LOAD CONTEXT
    # =========================
    context = load_truck_context()

    try:
        base_date = datetime.strptime(context["start_date"], "%Y-%m-%d")
    except:
        base_date = datetime(2025, 10, 1)   # fallback

    # =========================
    # COLUMN DETECTION
    # =========================
    col_map = {
        "plant": None,
        "destination": None,
        "truck_type": None,
        "trips": None,
        "cases": None
    }

    for col in df.columns:
        c = col.lower()

        if c == "plant":
            col_map["plant"] = col
        elif c in ["destination", "dest", "city"]:
            col_map["destination"] = col
        elif c in ["truck", "truck_type"]:
            col_map["truck_type"] = col
        elif "trip" in c:
            col_map["trips"] = col
        elif "case" in c:
            col_map["cases"] = col

    for key, val in col_map.items():
        if val is None:
            return {"status": "failed", "message": f"Missing column for {key}"}

    # =========================
    # 🔥 SCHEDULING LOGIC
    # =========================
    schedule = []

    for _, row in df.iterrows():

        plant = row[col_map["plant"]]
        dest = row[col_map["destination"]]
        truck_type = row[col_map["truck_type"]]
        trips = int(row[col_map["trips"]])
        total_cases = row[col_map["cases"]]

        if trips == 0:
            continue

        cases_per_truck = total_cases / trips

        for i in range(1, trips + 1):

            dispatch_date = base_date + timedelta(days=i - 1)

            schedule.append({
                "plant": plant,
                "destination": dest,
                "truck_id": f"{plant}_{dest}_TRUCK_{i}",
                "truck_type": truck_type,
                "load": round(cases_per_truck, 2),
                "planned_date": dispatch_date.strftime("%Y-%m-%d")
            })

    return {
        "status": "success",
        "context_used": context,   # 🔥 show in demo
        "total_trucks": len(schedule),
        "schedule": schedule[:25]
    }