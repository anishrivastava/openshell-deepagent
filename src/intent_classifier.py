from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(temperature=0)
 
INTENT_PROMPT = """
You are an intent classifier for a supply chain AI assistant.

Your job is to classify the user's request into exactly one of these labels:

1. run_planning
   - when user wants to execute planning pipeline

2. top_dispatch
   - when user asks about top cities or dispatch summary

3. underutilized_plants
   - when user asks about plant utilization

4. truck_schedule
   - when user asks to create or view truck schedule
   - when user ask to give a truck schedule for a specific date 

5. dispatch_adherence
   - when user asks about delay, adherence, or tracking

6. reconciliation
   - when user asks about invoice check, billing mismatch, finance validation

7. governance
   - when user asks about validation, compliance, images, proof, process checking

8. unknown
   - when none apply

Rules:
- Return ONLY the label
- No explanation
- No punctuation
- Output must match exactly one label from the list

Allowed outputs:
run_planning
top_dispatch
underutilized_plants
truck_schedule
dispatch_adherence
reconciliation
governance
unknown



6. truck_utilization
   - when user asks about:
     * truck utilization
     * truck efficiency
     * truck load %
     * capacity usage
     * utilization report
     * underutilized trucks
     
Examples:

User: truck utilization report
→ truck_utilization

User: show truck efficiency
→ truck_utilization

User: which trucks are underutilized
→ truck_utilization
"""


# def classify_intent(user_input: str) -> str:
   
#     response = llm.invoke([
#         SystemMessage(content=INTENT_PROMPT),
#         HumanMessage(content=user_input)
#     ])


#     intent = response.content.strip()

#     allowed = {
#         "run_planning",
#         "top_dispatch",
#         "underutilized_plants",
#         "truck_schedule",
#         "dispatch_adherence",
#         "reconciliation",
#         "governance",
#         "unknown"
#     }

#     if intent not in allowed:
#         return "unknown"

#     return intent

# def classify_intent(user_input: str) -> str:

#     user_input_lower = user_input.lower()
#     if "plant" in user_input_lower and "utilization" in user_input_lower:
#        return "underutilized_plants"
#     if any(word in user_input_lower for word in ["truck utilization", "truck efficiency"]):
#        return "truck_utilization"
#     if any(word in user_input_lower for word in ["reconcile", "invoice", "billing"]):
#        return "reconciliation"
#     if "schedule" in user_input_lower or "truck plan" in user_input_lower:
#        return "truck_schedule"
#     if any(word in user_input_lower for word in ["reconcile", "reconciliation", "invoice", "billing", "mismatch"]):
#         return "reconciliation"

#     if "schedule" in user_input_lower or "truck plan" in user_input_lower:
#         return "truck_schedule"

#     # =========================
#     # LLM fallback
#     # =========================
#     response = llm.invoke([
#         SystemMessage(content=INTENT_PROMPT),
#         HumanMessage(content=user_input)
#     ])

#     intent = response.content.strip()

#     allowed = {
#         "run_planning",
#         "top_dispatch",
#         "underutilized_plants",
#         "truck_schedule",
#         "dispatch_adherence",
#         "reconciliation",
#         "governance",
#         "truck_utilization",
#         "unknown"
#     }

#     if intent not in allowed:
#         return "unknown"

#     return intent    

def classify_intent(user_input: str) -> str:

    user_input_lower = user_input.lower()

    # 🔥 HARD RULES (FAST + ACCURATE)

    # Plant Utilization
    if "plant" in user_input_lower and "utilization" in user_input_lower:
        return "underutilized_plants"

    # Truck Utilization
    if any(word in user_input_lower for word in [
        "truck utilization", "truck efficiency", "utilization report", "capacity usage"
    ]):
        return "truck_utilization"

    # Truck Plan
    if "schedule" in user_input_lower or "truck plan" in user_input_lower:
        return "truck_schedule"

    # Adherence
    if any(word in user_input_lower for word in ["adherence", "delay", "tracking"]):
        return "dispatch_adherence"

    # Finance
    if any(word in user_input_lower for word in [
        "reconcile", "reconciliation", "invoice", "billing", "mismatch"
    ]):
        return "reconciliation"

    # Governance 🔥 (ADD THIS)
    if any(word in user_input_lower for word in [
        "governance", "check image", "validate", "compliance", "proof"
    ]):
        return "governance"

    # =========================
    # LLM fallback
    # =========================
    response = llm.invoke([
        SystemMessage(content=INTENT_PROMPT),
        HumanMessage(content=user_input)
    ])

    intent = response.content.strip()

    allowed = {
        "run_planning",
        "top_dispatch",
        "underutilized_plants",
        "truck_schedule",
        "dispatch_adherence",
        "reconciliation",
        "governance",
        "truck_utilization",
        "unknown"
    }

    if intent not in allowed:
        return "unknown"

    return intent
