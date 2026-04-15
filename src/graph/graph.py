# from typing import TypedDict

# from langgraph.graph import StateGraph, END

# from src.llm.semantic_router import semantic_classify_intent
# from src.tools.planning.planning_tools import run_planning_tool
# from src.tools.dispatch.dispatch_tools import get_top_5_cities_by_dispatch
# from src.tools.utilization.utilization_tools import get_underutilized_plants
# from src.tools.planning.truck_scheduling_tool import create_truck_schedule
# from src.tools.utilization.adherence_tool import check_dispatch_adherence
# from src.tools.dispatch.truck_utilization_tool import check_truck_utilization
# from src.tools.finance.reconcilation import run_reconciliation
# from src.tools.governance_tool import check_governance
# class AgentState(TypedDict):
#     user_input: str
#     intent: str
#     result: str


# def detect_intent(state: AgentState):
#     intent = semantic_classify_intent(state["user_input"])
#     return {"intent": intent}


# def route_intent(state: AgentState):
#     return state["intent"]


# def run_planning_node(state: AgentState):
#     result = run_planning_tool.invoke({})

#     if result["status"] == "success":
#         return {"result": "Planning completed successfully."}
#     else:
#         return {"result": f"Planning failed: {result['error']}"}


# def top_dispatch_node(state: AgentState):
#     result = get_top_5_cities_by_dispatch.invoke({})

#     if result["status"] == "success":
#         metric_col = result["metric_column"]
#         lines = []

#         for i, row in enumerate(result["top_5_cities"], start=1):
#             city = row["city"]
#             value = row[metric_col]
#             lines.append(f"{i}. {city} - {value:.2f}")

#         return {"result": "Top 5 cities by dispatch:\n" + "\n".join(lines)}
#     else:
#         return {"result": f"Dispatch analysis failed: {result['message']}"}


# def underutilized_plants_node(state: AgentState):
#     result = get_underutilized_plants.invoke({})

#     if result["status"] == "success":
#         plant_col = result["plant_column"]
#         util_col = result["utilization_column"]
#         lines = []

#         for i, row in enumerate(result["underutilized_plants"], start=1):
#             plant = row[plant_col]
#             utilization = row[util_col]
#             lines.append(f"{i}. {plant} - {utilization:.2f}%")

#         return {"result": "Most underutilized plants:\n" + "\n".join(lines)}
#     else:
#         return {"result": f"Utilization analysis failed: {result['message']}"}


# def unknown_node(state: AgentState):
#     return {"result": "Sorry, I could not understand the request."}


# def truck_schedule_node(state: AgentState):
#     result = create_truck_schedule.invoke({})

#     if result["status"] == "success":
#         lines = []

#         for row in result["schedule"]:
#             lines.append(
#                 f"{row['truck_id']} | {row['truck_type']} | "
#                 f"{row['plant']} → {row['destination']} | {row['load']} cases"
#                 f"{row['load']} cases | Date: {row['planned_date']}"
#             )

#         return {"result": "Truck Schedule:\n" + "\n".join(lines)}

#     else:
#         return {"result": result["message"]}

# def adherence_node(state: AgentState):
#     result = check_dispatch_adherence.invoke({})

#     if result["status"] == "success":
#         lines = []

#         for row in result["adherence"]:
#             lines.append(
#                 f"{row['truck_id']} | Planned: {row['planned_date']} | "
#                 f"Actual: {row['actual_date']} | Status: {row['status']}"
#             )

#         return {"result": "Dispatch Adherence:\n" + "\n".join(lines)}

#     else:
#         return {"result": result["message"]}
    
# def truck_utilization_node(state: AgentState):
#     result = check_truck_utilization.invoke({})

#     if result["status"] == "success":
#         lines = []

#         for row in result["truck_utilization"]:
#             lines.append(
#                 f"{row['route']} | {row['truck_type']} | "
#                 f"{row['utilization']}% | {row['status']} | {row['alert']}"
#             )

#         return {"result": "Truck Utilization:\n" + "\n".join(lines)}

#     else:
#         return {"result": result["message"]}
    
# def reconciliation_node(state):
#     result = run_reconciliation.invoke({})

#     # 🔥 HANDLE ERROR FIRST
#     if result["status"] != "success":
#         return {"result": f"Reconciliation failed: {result['message']}"}

#     lines = []

#     for row in result["reconciliation"]:
#         lines.append(
#             f"{row['invoice_id']} | {row['status']} | {row['remark']}"
#         )

#     return {"result": "Reconciliation Report:\n" + "\n".join(lines)}

# # def governance_node(state):
# #     result = run_governance_check.invoke({})

# #     if result["status"] == "success":
# #         lines = []
# #         for row in result["governance"]:
# #             lines.append(f"{row['truck_id']} | {row['status']} | {row['remark']}")

# #         return {"result": "Governance Check:\n" + "\n".join(lines)}
# #     else:
# #         return {"result": f"Governance failed: {result['message']}"}

# def governance_node(state):
#     result = check_governance.invoke({})

#     if result["status"] != "success":
#         return {"messages": ["Governance failed"]}

#     lines = ["Governance Report:"]

#     for row in result["governance"]:
#         lines.append(
#             f"{row['truck_id']} | {row['stage']} | {row['status']} | {row['remark']}"
#         )

#     return {"messages": ["\n".join(lines)]}

# graph_builder = StateGraph(AgentState)

# graph_builder.add_node("detect_intent", detect_intent)
# graph_builder.add_node("run_planning_node", run_planning_node)
# graph_builder.add_node("top_dispatch_node", top_dispatch_node)
# graph_builder.add_node("underutilized_plants_node", underutilized_plants_node)
# graph_builder.add_node("unknown_node", unknown_node)
# graph_builder.add_node("truck_schedule_node", truck_schedule_node)
# graph_builder.add_node("adherence_node", adherence_node)
# graph_builder.add_node("truck_utilization_node", truck_utilization_node)
# graph_builder.add_node("reconciliation_node", reconciliation_node)
# graph_builder.add_node("governance_node", governance_node)
# graph_builder.set_entry_point("detect_intent")

# graph_builder.add_conditional_edges(
#     "detect_intent",
#     route_intent,
#     {
#         "run_planning": "run_planning_node",
#         "top_dispatch": "top_dispatch_node",
#         "underutilized_plants": "underutilized_plants_node",
#         "truck_schedule": "truck_schedule_node",
#         "dispatch_adherence": "adherence_node",  # ✅ FIXED
#         "reconciliation": "reconciliation_node",
#         "governance": "governance_node",
#         "unknown": "unknown_node",
#     }
# )

# graph_builder.add_edge("run_planning_node", END)
# graph_builder.add_edge("top_dispatch_node", END)
# graph_builder.add_edge("underutilized_plants_node", END)
# graph_builder.add_edge("unknown_node", END)

# graph = graph_builder.compile()




#02-0402206

from typing import TypedDict
from langgraph.graph import StateGraph, END

# ✅ Intent
from src.intent_classifier import classify_intent

# ✅ Tools
from src.tools.planning.planning_tools import run_planning_tool
from src.tools.dispatch.dispatch_tools import get_top_5_cities_by_dispatch
from src.tools.utilization.utilization_tools import get_underutilized_plants
from src.tools.planning.truck_scheduling_tool import create_truck_schedule
from src.tools.utilization.adherence_tool import check_dispatch_adherence
from src.tools.dispatch.truck_utilization_tool import check_truck_utilization
from src.tools.finance.reconcilation import run_reconciliation
from src.tools.governance_tool import check_governance


# =========================
# STATE
# =========================
class AgentState(TypedDict):
    user_input: str
    intent: str
    result: str
    data: list
    finance_data: dict   # 🔥 ADD THIS# 🔥 NEW (store truck plan)


# =========================
# INTENT
# =========================
def detect_intent(state: AgentState):
    return {"intent": state.get("intent", "unknown")}


def route_intent(state: AgentState):
    return state["intent"]


# =========================
# NODES
# =========================

def run_planning_node(state: AgentState):
    result = run_planning_tool.invoke({})
    if result["status"] == "success":
        return {"result": "Planning completed successfully."}
    return {"result": f"Planning failed: {result.get('error', 'Unknown error')}"}


def top_dispatch_node(state: AgentState):
    result = get_top_5_cities_by_dispatch.invoke({})
    if result["status"] != "success":
        return {"result": result["message"]}

    metric_col = result["metric_column"]
    lines = []

    for i, row in enumerate(result["top_5_cities"], start=1):
        lines.append(f"{i}. {row['city']} - {row[metric_col]:.2f}")

    return {"result": "Top 5 cities by dispatch:\n" + "\n".join(lines)}


# def underutilized_plants_node(state: AgentState):
#     result = get_underutilized_plants.invoke({})
#     if result["status"] != "success":
#         return {"result": result["message"]}

#     plant_col = result["plant_column"]
#     util_col = result["utilization_column"]

#     lines = []
#     for i, row in enumerate(result["underutilized_plants"], start=1):
#         lines.append(f"{i}. {row[plant_col]} - {row[util_col]:.2f}%")

#     return {"result": "Most underutilized plants:\n" + "\n".join(lines)}

def underutilized_plants_node(state: AgentState):

    # 🔥 FIXED LINE
    result = get_underutilized_plants.invoke({
        "data": state.get("data")
    })

    if result["status"] != "success":
        return {"result": result["message"]}

    plant_col = result["plant_column"]
    util_col = result["utilization_column"]

    lines = []
    for i, row in enumerate(result["underutilized_plants"], start=1):
        lines.append(f"{i}. {row[plant_col]} - {row[util_col]:.2f}%")

    return {
        "result": "Hi 👋, here are the most underutilized plants:\n\n" + "\n".join(lines)
    }

# def truck_schedule_node(state: AgentState):
#     result = create_truck_schedule.invoke({})
#     if result["status"] != "success":
#         return {"result": result["message"]}

#     lines = []
#     for row in result["schedule"]:
#         lines.append(
#             f"{row['truck_id']} | {row['truck_type']} | "
#             f"{row['plant']} → {row['destination']} | "
#             f"{row['load']} cases | Date: {row['planned_date']}"
#         )

#     return {
#     "result": "Truck Schedule:\n" + "\n".join(lines),
#     "data": result["schedule"]   # 🔥 STORE DATA
# }
def truck_schedule_node(state: AgentState):

    # 🔥 FIXED LINE
    result = create_truck_schedule.invoke({
        "data": state.get("data")
    })

    if result["status"] != "success":
        return {"result": result["message"]}

    lines = []
    for row in result["schedule"]:
        lines.append(
            f"{row['truck_id']} | {row['truck_type']} | "
            f"{row['plant']} → {row['destination']} | "
            f"{row['load']} cases | Date: {row['planned_date']}"
        )

    return {
        "result": "Truck Schedule:\n" + "\n".join(lines),
        "data": result["schedule"]
    }

def adherence_node(state: AgentState):
    result = check_dispatch_adherence.invoke({})
    if result["status"] != "success":
        return {"result": result["message"]}

    lines = []
    for row in result["adherence"]:
        lines.append(
            f"{row['truck_id']} | Planned: {row['planned_date']} | "
            f"Actual: {row['actual_date']} | Status: {row['status']}"
        )

    return {"result": "Dispatch Adherence:\n" + "\n".join(lines)}


def truck_utilization_node(state: AgentState):
    result = check_truck_utilization.invoke({})
    if result["status"] != "success":
        return {"result": result["message"]}

    lines = []
    for row in result["truck_utilization"]:
        lines.append(
            f"{row['route']} | {row['truck_type']} | "
            f"{row['utilization']}% | {row['status']} | {row['alert']}"
        )

    return {"result": "Truck Utilization:\n" + "\n".join(lines)}


# def reconciliation_node(state: AgentState):
#     result = run_reconciliation.invoke({})
#     if result["status"] != "success":
#         return {"result": result["message"]}

#     lines = []
#     for row in result["reconciliation"]:
#         lines.append(
#             f"{row['invoice_id']} | {row['status']} | {row['remark']}"
#         )

#     return {"result": "Reconciliation Report:\n" + "\n".join(lines)}

def reconciliation_node(state: AgentState):

    result = run_reconciliation.invoke({
        "data": state.get("finance_data")   # 🔥 FIX
    })

    if result["status"] != "success":
        return {"result": result["message"]}

    lines = []
    for row in result["reconciliation"]:
        lines.append(
            f"{row['invoice_id']} | {row['status']} | {row['remark']}"
        )

    return {
        "result": "Reconciliation Report:\n" + "\n".join(lines)
    }

# def governance_node(state: AgentState):
#     result = check_governance.invoke({
#     "image": state.get("image"),
#     "stage": "loading"   # later dynamic karenge
# })
#     if result["status"] != "success":
#         return {"result": result["message"]}

#     lines = ["Governance Report:"]
#     for row in result["governance"]:
#         lines.append(
#             f"{row['truck_id']} | {row['stage']} | {row['status']} | {row['remark']}"
#         )

#     return {"result": "\n".join(lines)}


def governance_node(state: AgentState):

    result = check_governance.invoke({
        "image": state.get("image"),
        "stage": "loading"
    })

    if result["status"] != "success":
        return {"result": result["message"]}

    lines = ["Hi 👋, here is your governance report:\n"]

    for row in result["governance"]:
        lines.append(
            f"{row['stage']} | {row['status']} | {row['remark']}"
        )

    return {"result": "\n".join(lines)}

def filter_plan_node(state: AgentState):

    schedule = state.get("data", [])
    user_input = state.get("user_input", "").lower()

    if not schedule:
        return {"result": "No existing plan found. Please create a truck plan first."}

    filtered = []

    for row in schedule:

        plant = row["plant"].lower()
        dest = row["destination"].lower()
        truck = row["truck_type"].lower()

        # 🔥 dynamic match (no hardcoding)
        if plant in user_input or dest in user_input or truck in user_input:
            filtered.append(row)

    # 🔥 fallback: partial matching
    if not filtered:
        for row in schedule:
            if any(word in row["destination"].lower() for word in user_input.split()):
                filtered.append(row)

    if not filtered:
        return {"result": "No matching data found for your filter."}

    lines = []
    for row in filtered:
        lines.append(
            f"{row['truck_id']} | {row['truck_type']} | "
            f"{row['plant']} → {row['destination']} | "
            f"{row['load']} cases | Date: {row['planned_date']}"
        )

    return {
        "result": "Filtered Truck Plan:\n" + "\n".join(lines),
        "data": filtered
    }


def unknown_node(state: AgentState):
    return {"result": "Sorry, I could not understand the request."}


# =========================
# GRAPH
# =========================

graph_builder = StateGraph(AgentState)

graph_builder.add_node("detect_intent", detect_intent)
graph_builder.add_node("run_planning_node", run_planning_node)
graph_builder.add_node("top_dispatch_node", top_dispatch_node)
graph_builder.add_node("underutilized_plants_node", underutilized_plants_node)
graph_builder.add_node("truck_schedule_node", truck_schedule_node)
graph_builder.add_node("adherence_node", adherence_node)
graph_builder.add_node("truck_utilization_node", truck_utilization_node)
graph_builder.add_node("reconciliation_node", reconciliation_node)
graph_builder.add_node("governance_node", governance_node)
graph_builder.add_node("filter_plan_node", filter_plan_node)
graph_builder.add_node("unknown_node", unknown_node)

graph_builder.set_entry_point("detect_intent")

graph_builder.add_conditional_edges(
    "detect_intent",
    route_intent,
    {
        "run_planning": "run_planning_node",
        "top_dispatch": "top_dispatch_node",
        "underutilized_plants": "underutilized_plants_node",
        "truck_schedule": "truck_schedule_node",
        "truck_utilization": "truck_utilization_node",
        "dispatch_adherence": "adherence_node",
        "reconciliation": "reconciliation_node",
        "governance": "governance_node",
        "unknown": "unknown_node",
        "filter_plan": "filter_plan_node", 
    }
)

graph_builder.add_edge("run_planning_node", END)
graph_builder.add_edge("top_dispatch_node", END)
graph_builder.add_edge("underutilized_plants_node", END)
graph_builder.add_edge("truck_schedule_node", END)
graph_builder.add_edge("adherence_node", END)
graph_builder.add_edge("truck_utilization_node", END)
graph_builder.add_edge("reconciliation_node", END)
graph_builder.add_edge("governance_node", END)
graph_builder.add_edge("unknown_node", END)

graph = graph_builder.compile()