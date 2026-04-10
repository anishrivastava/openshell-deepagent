# from pathlib import Path
# import pandas as pd
# from langchain_core.tools import tool
# from datetime import datetime, timedelta


# @tool
# def create_truck_schedule():
#     """
#     Create truck schedule using actual dispatch plan data.
#     Adds planned dispatch dates (October).
#     """

#     # 🔹 Path to your output folder
#     outputs_dir = Path(r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT\outputs")

#     # 🔹 Get latest file
#     files = list(outputs_dir.glob("fsd_planning_output_*.xlsx"))
#     if not files:
#         return {"status": "failed", "message": "No planning output found"}

#     latest_file = max(files, key=lambda x: x.stat().st_mtime)

#     # 🔹 Read dispatch sheet
#     try:
#         df = pd.read_excel(latest_file, sheet_name="dispatch_plan")
#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     # 🔹 Clean column names
#     df.columns = df.columns.str.strip().str.lower()

#     # 🔹 Smart column detection
#     col_map = {
#         "plant": None,
#         "destination": None,
#         "truck_type": None,
#         "trips": None,
#         "cases": None
#     }

#     for col in df.columns:
#         c = col.lower()

#         if c == "plant":
#             col_map["plant"] = col
#         elif c in ["destination", "dest", "city"]:
#             col_map["destination"] = col
#         elif c in ["truck", "truck_type"]:
#             col_map["truck_type"] = col
#         elif "trip" in c:
#             col_map["trips"] = col
#         elif "case" in c:
#             col_map["cases"] = col

#     # 🔹 Validate columns
#     for key, val in col_map.items():
#         if val is None:
#             return {"status": "failed", "message": f"Missing column for {key}"}

#     # 🔹 Base date → October
#     base_date = datetime(2025, 10, 1)

#     # 🔹 Build truck schedule
#     schedule = []

#     for _, row in df.iterrows():
#         plant = row[col_map["plant"]]
#         dest = row[col_map["destination"]]
#         truck_type = row[col_map["truck_type"]]
#         trips = int(row[col_map["trips"]])
#         total_cases = row[col_map["cases"]]

#         if trips == 0:
#             continue

#         cases_per_truck = total_cases / trips

#         for i in range(1, trips + 1):
#             dispatch_date = base_date + timedelta(days=i - 1)

#             schedule.append({
#                 "plant": plant,
#                 "destination": dest,
#                 "truck_id": f"{plant}_{dest}_TRUCK_{i}",
#                 "truck_type": truck_type,
#                 "load": round(cases_per_truck, 2),
#                 "planned_date": dispatch_date.strftime("%Y-%m-%d")
#             })

#     return {
#         "status": "success",
#         "total_trucks": len(schedule),
#         "schedule": schedule[:25]  # limit output
#     }

# import pandas as pd
# from langchain_core.tools import tool
# from datetime import datetime, timedelta


# @tool
# def create_truck_schedule(state: dict):
#     """
#     Create truck schedule using uploaded dispatch plan data
#     """

#     data = state.get("data")

#     if not data:
#         return {"status": "failed", "message": "No data received"}

#     df = pd.DataFrame(data)

#     # 🔹 Clean column names
#     df.columns = df.columns.str.strip().str.lower()

#     # 🔹 Smart column detection
#     col_map = {
#         "plant": None,
#         "destination": None,
#         "truck_type": None,
#         "trips": None,
#         "cases": None
#     }

#     for col in df.columns:
#         c = col.lower()

#         if c == "plant":
#             col_map["plant"] = col
#         elif c in ["destination", "dest", "city"]:
#             col_map["destination"] = col
#         elif c in ["truck", "truck_type"]:
#             col_map["truck_type"] = col
#         elif "trip" in c:
#             col_map["trips"] = col
#         elif "case" in c:
#             col_map["cases"] = col

#     # 🔹 Validate columns
#     for key, val in col_map.items():
#         if val is None:
#             return {"status": "failed", "message": f"Missing column for {key}"}

#     base_date = datetime(2025, 10, 1)
#     schedule = []

#     for _, row in df.iterrows():

#         plant = row[col_map["plant"]]
#         dest = row[col_map["destination"]]
#         truck_type = row[col_map["truck_type"]]
#         trips = int(row[col_map["trips"]])
#         total_cases = row[col_map["cases"]]

#         if trips == 0:
#             continue

#         cases_per_truck = total_cases / trips

#         for i in range(1, trips + 1):
#             dispatch_date = base_date + timedelta(days=i - 1)

#             schedule.append({
#                 "plant": plant,
#                 "destination": dest,
#                 "truck_id": f"{plant}_{dest}_TRUCK_{i}",
#                 "truck_type": truck_type,
#                 "load": round(cases_per_truck, 2),
#                 "planned_date": dispatch_date.strftime("%Y-%m-%d")
#             })

#     return {
#         "status": "success",
#         "total_trucks": len(schedule),
#         "schedule": schedule[:25]
#     }


import pandas as pd
from langchain_core.tools import tool
from datetime import datetime, timedelta


@tool
def create_truck_schedule(data: list):
    """
    Create truck schedule using dispatch plan data
    """

    if not data:
        return {"status": "failed", "message": "No data received"}

    df = pd.DataFrame(data)

    # 🔹 Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # 🔹 Column detection
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

    base_date = datetime(2025, 10, 1)
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
        "total_trucks": len(schedule),
        "schedule": schedule[:25]
    }