import pandas as pd
from langchain_core.tools import tool


@tool
def check_truck_utilization(data: dict, config: dict = None):
    """
    Calculate truck-level utilization and flag inefficient trucks.
    Supports dynamic thresholds and result limits.
    """

    config = config or {}

    low_threshold = config.get("low_utilization_threshold", 50)
    medium_threshold = config.get("medium_utilization_threshold", 80)
    max_results = config.get("max_results", 25)
    truck_capacity_map = config.get(
        "truck_capacity_map",
        {
            "mini": 300,
            "7mt": 700,
            "9mt": 900,
            "12mt": 1200,
            "16mt": 1600,
            "20ft": 1800,
            "32ft": 3000
        }
    )

    # =========================
    # VALIDATION
    # =========================
    if not data or "dispatch" not in data:
        return {"status": "failed", "message": "No dispatch data received"}

    df = pd.DataFrame(data.get("dispatch", []))

    if df.empty:
        return {"status": "failed", "message": "Dispatch data is empty"}

    df.columns = df.columns.str.strip().str.lower()

    # =========================
    # COLUMN MAPPING
    # =========================
    col_map = {
        "plant": None,
        "destination": None,
        "truck": None,
        "trips": None,
        "cases": None,
        "capacity": None
    }

    for col in df.columns:
        c = col.lower().strip()

        if c == "plant":
            col_map["plant"] = col
        elif c in ["destination", "city"]:
            col_map["destination"] = col
        elif "truck" in c:
            col_map["truck"] = col
        elif "trip" in c:
            col_map["trips"] = col
        elif "case" in c:
            col_map["cases"] = col
        elif "capacity" in c:
            col_map["capacity"] = col

    # =========================
    # REQUIRED COLUMN CHECK
    # =========================
    required_fields = ["plant", "destination", "truck", "trips", "cases"]

    for field in required_fields:
        if col_map[field] is None:
            return {
                "status": "failed",
                "message": f"Missing required column: {field}"
            }

    results = []

    # =========================
    # MAIN CALCULATION LOOP
    # =========================
    for _, row in df.iterrows():

        try:
            plant = str(row[col_map["plant"]]).strip()
            dest = str(row[col_map["destination"]]).strip()
            truck_type = str(row[col_map["truck"]]).lower().strip()

            trips = float(row[col_map["trips"]])
            total_cases = float(row[col_map["cases"]])

            if trips <= 0:
                continue

            load_per_truck = total_cases / trips

            # =========================
            # CAPACITY LOGIC
            # =========================
            capacity = None

            if col_map["capacity"] is not None:
                try:
                    uploaded_capacity = row[col_map["capacity"]]

                    if pd.notna(uploaded_capacity):
                        capacity = float(uploaded_capacity)
                except:
                    capacity = None

            if capacity is None:
                for key in truck_capacity_map:
                    if key in truck_type:
                        capacity = truck_capacity_map[key]
                        break

            if capacity is None or capacity <= 0:
                continue

            # =========================
            # UTILIZATION CALCULATION
            # =========================
            utilization = (load_per_truck / capacity) * 100

            # =========================
            # ALERT LOGIC
            # =========================
            if utilization < low_threshold:
                status = "LOW_UTILIZATION 🚨"
                alert = "Truck underfilled → cost wastage"
            elif utilization < medium_threshold:
                status = "MEDIUM ⚠️"
                alert = "Optimize load planning"
            else:
                status = "GOOD ✅"
                alert = "Efficient usage"

            results.append({
                "plant": plant,
                "city": dest,
                "truck_type": truck_type,
                "trips": int(trips),
                "cases": round(total_cases, 2),
                "capacity": round(capacity, 2),
                "utilization": round(utilization, 2),
                "status": status,
                "alert": alert,
                "route": f"{plant} → {dest}"
            })

        except Exception:
            continue

    # =========================
    # FINAL RESPONSE
    # =========================
    if not results:
        return {
            "status": "failed",
            "message": "No valid truck utilization records could be generated"
        }

    return {
        "status": "success",
        "applied_config": {
            "low_utilization_threshold": low_threshold,
            "medium_utilization_threshold": medium_threshold,
            "max_results": max_results
        },
        "truck_utilization": results[:max_results]
    }


