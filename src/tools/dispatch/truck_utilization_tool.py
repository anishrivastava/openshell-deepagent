# from pathlib import Path
# import pandas as pd
# from langchain_core.tools import tool


# @tool
# def check_truck_utilization():
#     """
#     Calculate truck-level utilization and flag inefficient trucks.
#     """

#     outputs_dir = Path(r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT\outputs")

#     files = list(outputs_dir.glob("fsd_planning_output_*.xlsx"))
#     if not files:
#         return {"status": "failed", "message": "No planning output found"}

#     latest_file = max(files, key=lambda x: x.stat().st_mtime)

#     try:
#         df = pd.read_excel(latest_file, sheet_name="dispatch_plan")
#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     df.columns = df.columns.str.strip().str.lower()

#     # 🔹 Column mapping
#     col_map = {
#         "plant": None,
#         "destination": None,
#         "truck": None,
#         "trips": None,
#         "cases": None
#     }

#     for col in df.columns:
#         c = col.lower()

#         if c == "plant":
#             col_map["plant"] = col
#         elif c in ["destination", "city"]:
#             col_map["destination"] = col
#         elif "truck" in c:
#             col_map["truck"] = col
#         elif "trip" in c:
#             col_map["trips"] = col
#         elif "case" in c:
#             col_map["cases"] = col

#     for key, val in col_map.items():
#         if val is None:
#             return {"status": "failed", "message": f"Missing column for {key}"}

#     # 🔹 Truck capacity mapping
#     truck_capacity_map = {
#         "9mt": 900,
#         "16mt": 1600
#     }

#     results = []

#     for _, row in df.iterrows():
#         plant = row[col_map["plant"]]
#         dest = row[col_map["destination"]]
#         truck_type = str(row[col_map["truck"]]).lower()
#         trips = int(row[col_map["trips"]])
#         total_cases = row[col_map["cases"]]

#         if trips == 0:
#             continue

#         load_per_truck = total_cases / trips

#         capacity = None
#         for key in truck_capacity_map:
#             if key in truck_type:
#                 capacity = truck_capacity_map[key]
#                 break

#         if capacity is None:
#             continue

#         utilization = (load_per_truck / capacity) * 100

#         # 🔥 Alert logic
#         if utilization < 50:
#             status = "LOW_UTILIZATION 🚨"
#             alert = "Truck underfilled → cost wastage"
#         elif utilization < 80:
#             status = "MEDIUM ⚠️"
#             alert = "Optimize load planning"
#         else:
#             status = "GOOD ✅"
#             alert = "Efficient usage"

#         results.append({
#             "route": f"{plant} → {dest}",
#             "truck_type": truck_type,
#             "utilization": round(utilization, 2),
#             "status": status,
#             "alert": alert
#         })

#     return {
#         "status": "success",
#         "truck_utilization": results[:25]
#     }


import pandas as pd
from langchain_core.tools import tool


@tool
def check_truck_utilization(data: dict):
    """
    Calculate truck-level utilization and flag inefficient trucks.
    """

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

    # =========================
    # DEFAULT TRUCK CAPACITY MAP
    # =========================
    truck_capacity_map = {
        "mini": 300,
        "7mt": 700,
        "9mt": 900,
        "12mt": 1200,
        "16mt": 1600,
        "20ft": 1800,
        "32ft": 3000
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

            # Use uploaded capacity if provided
            if col_map["capacity"] is not None:
                try:
                    uploaded_capacity = row[col_map["capacity"]]

                    if pd.notna(uploaded_capacity):
                        capacity = float(uploaded_capacity)
                except:
                    capacity = None

            # Fallback to truck type mapping
            if capacity is None:
                for key in truck_capacity_map:
                    if key in truck_type:
                        capacity = truck_capacity_map[key]
                        break

            # Skip if still not found
            if capacity is None or capacity <= 0:
                continue

            # =========================
            # UTILIZATION CALCULATION
            # =========================
            utilization = (load_per_truck / capacity) * 100

            # =========================
            # ALERT LOGIC
            # =========================
            if utilization < 50:
                status = "LOW_UTILIZATION 🚨"
                alert = "Truck underfilled → cost wastage"
            elif utilization < 80:
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
        "truck_utilization": results[:25]
    }