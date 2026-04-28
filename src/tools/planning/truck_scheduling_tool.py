# import pandas as pd
# from langchain_core.tools import tool
# from datetime import datetime, timedelta
# from pathlib import Path


# # =========================
# # 🔥 CONTEXT LOADER
# # =========================
# def load_truck_context():

#     context = {
#         "start_date": "2025-10-01"   # fallback (important for demo)
#     }

#     path = Path("skills/truck_schedule/context.md")

#     if not path.exists():
#         return context

#     try:
#         with open(path, "r") as f:
#             for line in f:
#                 line = line.strip().lower()

#                 if "start_date" in line:
#                     context["start_date"] = line.split("=")[1].strip()

#     except Exception as e:
#         print("Context error:", e)

#     return context


# # =========================
# # 🔥 MAIN TOOL
# # =========================
# @tool
# def create_truck_schedule(data: dict):
#     """
#     Create truck schedule using dispatch plan data (NOW CONTEXT-DRIVEN)
#     """

#     # =========================
#     # VALIDATION
#     # =========================
#     if not data or "dispatch" not in data:
#         return {"status": "failed", "message": "No dispatch data received"}

#     df = pd.DataFrame(data.get("dispatch", []))

#     # 🔹 Clean column names
#     df.columns = df.columns.str.strip().str.lower()

#     # =========================
#     # 🔥 LOAD CONTEXT
#     # =========================
#     context = load_truck_context()

#     try:
#         base_date = datetime.strptime(context["start_date"], "%Y-%m-%d")
#     except:
#         base_date = datetime(2025, 10, 1)   # fallback

#     # =========================
#     # COLUMN DETECTION
#     # =========================
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

#     for key, val in col_map.items():
#         if val is None:
#             return {"status": "failed", "message": f"Missing column for {key}"}

#     # =========================
#     # 🔥 SCHEDULING LOGIC
#     # =========================
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
#         "context_used": context,   # 🔥 show in demo
#         "total_trucks": len(schedule),
#         "schedule": schedule[:25]
#     }

import pandas as pd
from langchain_core.tools import tool
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
import json

# =========================
# LLM SETUP
# =========================
llm = ChatOpenAI(temperature=0)


# =========================
# RULE GENERATOR (LLM)
# =========================
def generate_rules(user_query: str):

    if not user_query:
        return {}

    prompt = f"""
    You are a logistics AI.

    Extract structured rules from the user query.

    Return JSON ONLY in this format:

    {{
      "start_date": "YYYY-MM-DD",
      "high_load_truck": "16MT",
      "low_load_truck": "9MT",
      "load_threshold": 1000,
      "route_rules": [
        {{
          "plant": "...",
          "destination": "...",
          "truck_type": "9MT"
        }}
      ]
    }}

    Rules:
    - Do NOT assume city names
    - Use EXACT text from user
    - If not present, keep fields empty

    User Query:
    {user_query}
    """

    try:
        response = llm.invoke(prompt)
        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except:
        return {}


# =========================
# MAIN TOOL
# =========================
@tool
def create_truck_schedule(data: dict):

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

        if "plant" in c:
            col_map["plant"] = col
        elif "dest" in c or "city" in c:
            col_map["destination"] = col
        elif "truck" in c:
            col_map["truck_type"] = col
        elif "trip" in c:
            col_map["trips"] = col
        elif "case" in c:
            col_map["cases"] = col

    for key, val in col_map.items():
        if val is None:
            return {"status": "failed", "message": f"Missing column: {key}"}

    # =========================
    # GET USER QUERY
    # =========================
    user_query = data.get("query", "")

    # =========================
    # LLM RULES
    # =========================
    rules = generate_rules(user_query)

    # =========================
    # DATE LOGIC
    # =========================
    try:
        if "start_date" in rules and rules["start_date"]:
            base_date = datetime.strptime(rules["start_date"], "%Y-%m-%d")
        else:
            base_date = datetime(2025, 10, 1)
    except:
        base_date = datetime(2025, 10, 1)

    # =========================
    # LOAD RULES
    # =========================
    high_truck = rules.get("high_load_truck", "16MT")
    low_truck = rules.get("low_load_truck", "9MT")
    threshold = rules.get("load_threshold", 1000)

    route_rules = rules.get("route_rules", [])

    schedule = []

    # =========================
    # MAIN LOOP
    # =========================
    for _, row in df.iterrows():

        try:
            plant = str(row[col_map["plant"]])
            dest = str(row[col_map["destination"]])
            truck_type = str(row[col_map["truck_type"]])

            trips = int(row[col_map["trips"]])
            total_cases = float(row[col_map["cases"]])

            if trips <= 0:
                continue

            cases_per_truck = total_cases / trips

            # =========================
            # ROUTE BASED OVERRIDE
            # =========================
            matched = False

            for rule in route_rules:
                rule_plant = rule.get("plant", "")
                rule_dest = rule.get("destination", "")

                if (
                    rule_plant.lower() in plant.lower()
                    and rule_dest.lower() in dest.lower()
                ):
                    truck_type = rule.get("truck_type", truck_type)
                    matched = True
                    break

            # =========================
            # LOAD BASED LOGIC
            # =========================
            if not matched:
                if cases_per_truck > threshold:
                    truck_type = high_truck
                else:
                    truck_type = low_truck

            # =========================
            # BUILD SCHEDULE
            # =========================
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

        except Exception:
            continue

    # =========================
    # FINAL OUTPUT
    # =========================
    if not schedule:
        return {"status": "failed", "message": "No schedule generated"}

    lines = []

    for row in schedule[:25]:
        lines.append(
            f"{row['plant']} → {row['destination']} | "
            f"{row['truck_type']} | "
            f"{row['load']} cases | "
            f"{row['planned_date']}"
        )

    return {
        "status": "success",
        "total_trucks": len(schedule),
        "schedule": schedule,
        "result": "\n".join(lines)
    }