# from src.graph.graph import graph
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import SystemMessage, HumanMessage
# from datetime import datetime
# import json

# # =========================
# # LLM SETUP
# # =========================
# llm = ChatOpenAI(temperature=0)

# # =========================
# # SYSTEM PROMPT (BRAIN)
# # =========================
# SYSTEM_PROMPT = """
# You are a smart AI assistant for supply chain operations.

# Your job:
# 1. Understand user query
# 2. Classify into one of 3 modes:

# ----------------------------------------

# 1. ASK MODE:
# If information is missing

# Return:
# {
#   "action": "ask",
#   "question": "your question"
# }

# ----------------------------------------

# 2. EXECUTE MODE:
# If it's a structured business query (report OR modifying previous result)

# Return:
# {
#   "action": "execute",
#   "intent": "...",
#   "report_type": "...",
#   "date": "..."
# }

# ----------------------------------------

# 3. DIRECT MODE:
# If user asks:
# - calculations
# - comparisons
# - general knowledge

# Return:
# {
#   "action": "direct",
#   "query": "original user query"
# }

# ----------------------------------------

# IMPORTANT RULE:
# - If user refers to previous result (filter, show, change, update), ALWAYS use EXECUTE mode

# Examples:

# User: what is difference between invoice 1 and 2
# → direct

# User: calculate total billed amount
# → direct

# User: I need report
# → ask

# User: truck plan
# → ask

# User: truck plan for 2025-10-01
# → execute

# User: show only 16MT
# → execute

# User: filter Bangalore
# → execute

# User: change truck type
# → execute

# ONLY return JSON
# """

# # =========================
# # LLM DECISION FUNCTION
# # =========================
# def process_with_llm(user_input, memory):

#     messages = [
#         SystemMessage(content=SYSTEM_PROMPT),
#         HumanMessage(content=f"""
# Conversation so far:
# {memory}

# User: {user_input}
# """)
#     ]

#     response = llm.invoke(messages)
#     content = response.content.strip()

#     # clean json
#     content = content.replace("```json", "").replace("```", "").strip()

#     try:
#         return json.loads(content)
#     except:
#         return {
#             "action": "ask",
#             "question": "Sorry, I didn’t understand. Can you clarify?"
#         }

# # =========================
# # GRAPH CALL (SAFE)
# # =========================
# def run_graph_agent(user_input: str):

#     try:
#         result = graph.invoke({
#             "user_input": user_input,
#             "intent": "",
#             "result": "",
#             "data": []
#         })

#         return result.get("result", "No result generated.")

#     except Exception as e:
#         return f"Error: {str(e)}"

# # =========================
# # GREETING
# # =========================
# def get_greeting():
#     hour = datetime.now().hour
#     if hour < 12:
#         return "Good morning ☀️"
#     elif hour < 17:
#         return "Good afternoon 🌤️"
#     else:
#         return "Good evening "

# # =========================
# # MAIN LOOP
# # =========================
# if __name__ == "__main__":

#     print("🤖 AI Agent Ready!\n")

#     memory = ""

#     while True:
#         user_input = input("Ask: ").strip()

#         # store memory
#         memory += f"\nUser: {user_input}"

#         # 🔥 LLM decides
#         decision = process_with_llm(user_input, memory)

#         # =========================
#         # ASK FLOW
#         # =========================
#         if decision["action"] == "ask":

#             question = decision["question"]

#             if "hello" in user_input.lower() or "hi" in user_input.lower():
#                 print(f"\n{get_greeting()}! How can I help you today?\n")
#             else:
#                 print("\n" + question + "\n")

#             memory += f"\nAI: {question}"
#             continue

#         # =========================
#         # EXECUTE FLOW
#         # =========================
#         elif decision["action"] == "execute":

#             # 🔥 If it's filter/modify → use original query
#             if any(word in user_input.lower() for word in ["show", "filter", "only", "change", "update"]):
#                 output = run_graph_agent(user_input)

#             else:
#                 intent = decision.get("intent", "")
#                 report_type = decision.get("report_type", "")
#                 date = decision.get("date", "")

#                 final_query = f"{intent} {report_type} report for {date}"
#                 output = run_graph_agent(final_query)

#             print("\n" + str(output) + "\n")
#             memory += f"\nAI: {output}"

#         # =========================
#         # DIRECT FLOW
#         # =========================
#         elif decision["action"] == "direct":

#             query = decision.get("query", user_input)
#             response = llm.invoke(query)

#             print("\n" + response.content + "\n")
#             memory += f"\nAI: {response.content}"

#         else:
#             print("\nSomething went wrong.\n")


# from src.graph.graph import graph
# from src.intent_classifier import classify_intent   # ✅ IMPORTANT

# from langchain_openai import ChatOpenAI
# from langchain_core.messages import SystemMessage, HumanMessage
# from datetime import datetime
# import json

# # =========================
# # LLM SETUP
# # =========================
# llm = ChatOpenAI(temperature=0)

# # =========================
# # SYSTEM PROMPT (ONLY FOR ASK/DIRECT)
# # =========================
# SYSTEM_PROMPT = """
# You are a smart AI assistant for supply chain operations.

# Your job:
# 1. Understand user query
# 2. Be DECISIVE — avoid unnecessary questions

# ----------------------------------------

# RULES:

# 1. If user asks for a report WITHOUT date:
#    → Assume latest available data
#    → DO NOT ASK

# 2. If user asks:
#    "truck plan"
#    → Directly return latest truck schedule

# 3. If user asks:
#    "truck utilization"
#    → Directly return utilization report

# 4. Ask ONLY if:
#    - Query is completely unclear
#    - Missing critical info (rare)

# ----------------------------------------

# MODES:

# EXECUTE → default (MOST IMPORTANT)
# ASK → only if absolutely required
# DIRECT → calculations

# ----------------------------------------

# IMPORTANT:
# - NEVER ask multiple follow-up questions
# - ALWAYS try to answer in first attempt
# - Prefer EXECUTE over ASK

# Return JSON only
# """

# # =========================
# # LLM DECISION FUNCTION
# # =========================
# def process_with_llm(user_input, memory):

#     messages = [
#         SystemMessage(content=SYSTEM_PROMPT),
#         HumanMessage(content=f"""
# Conversation:
# {memory}

# User: {user_input}
# """)
#     ]

#     response = llm.invoke(messages)
#     content = response.content.strip()

#     content = content.replace("```json", "").replace("```", "").strip()

#     try:
#         return json.loads(content)
#     except:
#         return {"action": "execute"}   # 🔥 default to execute


# # =========================
# # GRAPH CALL (FIXED)
# # =========================
# def run_graph_agent(user_input: str):

#     try:
#         # 🔥 FORCE CORRECT INTENT
#         intent = classify_intent(user_input)

#         result = graph.invoke({
#             "user_input": user_input,
#             "intent": intent,
#             "result": "",
#             "data": []
#         })

#         return result.get("result", "No result generated.")

#     except Exception as e:
#         return f"Error: {str(e)}"


# # =========================
# # GREETING
# # =========================
# def get_greeting():
#     hour = datetime.now().hour
#     if hour < 12:
#         return "Good morning ☀️"
#     elif hour < 17:
#         return "Good afternoon 🌤️"
#     else:
#         return "Good evening 🌙"


# # =========================
# # MAIN LOOP
# # =========================
# if __name__ == "__main__":

#     print("🤖 AI Agent Ready!\n")

#     memory = ""

#     while True:
#         user_input = input("Ask: ").strip()

#         memory += f"\nUser: {user_input}"

#         decision = process_with_llm(user_input, memory)

#         # =========================
#         # ASK FLOW
#         # =========================
#         if decision["action"] == "ask":

#             question = decision["question"]

#             if "hi" in user_input.lower() or "hello" in user_input.lower():
#                 print(f"\n{get_greeting()}! How can I help you today?\n")
#             else:
#                 print("\n" + question + "\n")

#             memory += f"\nAI: {question}"
#             continue

#         # =========================
#         # EXECUTE FLOW (FIXED)
#         # =========================
#         elif decision["action"] == "execute":

#             # 🔥 ALWAYS USE USER INPUT DIRECTLY
#             output = run_graph_agent(user_input)

#             print("\n" + str(output) + "\n")
#             memory += f"\nAI: {output}"

#         # =========================
#         # DIRECT FLOW
#         # =========================
#         elif decision["action"] == "direct":

#             query = decision.get("query", user_input)
#             response = llm.invoke(query)

#             print("\n" + response.content + "\n")
#             memory += f"\nAI: {response.content}"

#         else:
#             print("\nSomething went wrong.\n")




from src.graph.graph import graph
from src.intent_classifier import classify_intent

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import datetime
import json

from dotenv import load_dotenv
load_dotenv()

# =========================
# LLM SETUP
# =========================
llm = ChatOpenAI(temperature=0)

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
You are a smart AI assistant for supply chain operations.

Rules:
- Always try to answer directly
- Avoid unnecessary questions
- Prefer execution over asking
- Only ask if absolutely unclear

Return JSON only:
{
  "action": "execute" | "ask" | "direct",
  "question": "...",
  "query": "..."
}
"""

# =========================
# LLM DECISION FUNCTION (SAFE)
# =========================
def process_with_llm(user_input, memory):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
Conversation:
{memory}

User: {user_input}
""")
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip()
        content = content.replace("```json", "").replace("```", "").strip()

        parsed = json.loads(content)

        if "action" not in parsed:
            parsed["action"] = "execute"

        return parsed

    except:
        return {"action": "execute"}   # fallback


# =========================
# GRAPH CALL
# =========================
def run_graph_agent(user_input: str):

    try:
        intent = classify_intent(user_input)

        result = graph.invoke({
            "user_input": user_input,
            "intent": intent,
            "result": "",
            "data": []
        })

        return result.get("result", "No result generated.")

    except Exception as e:
        return f"Error: {str(e)}"


# =========================
# GREETING
# =========================
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning ☀️"
    elif hour < 17:
        return "Good afternoon 🌤️"
    else:
        return "Good evening 🌙"


# =========================
# MAIN LOOP
# =========================
if __name__ == "__main__":

    print("🤖 AI Agent Ready!\n")

    memory = ""

    while True:
        try:
            user_input = input("Ask: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        memory += f"\nUser: {user_input}"

        lower = user_input.lower()

        # =========================
        # 🔥 OPTIMIZATION MODE (SMART AI)
        # =========================
        if any(word in lower for word in ["underutilized", "optimize", "improve", "change truck size"]):

            print("\n🤖 I found some trucks may be underutilized.")

            route = input("👉 Which route (source → destination)? ").strip()

            print("\n🔍 Analyzing...\n")

            # 🔥 Replace later with real data
            print(f"Route: {route}")
            print("Load carried: ~520 cases")
            print("16MT capacity: ~1500 cases")
            print("9MT capacity: ~700 cases\n")

            print("✅ Recommendation: Use 9MT instead of 16MT (cost saving)")

            confirm = input("\n👉 Do you want to update truck plan? (yes/no): ")

            if confirm.lower() == "yes":
                print("\n🚀 Updating truck plan...\n")

                output = run_graph_agent(f"change truck for {route} to 9MT")

                print("\n" + str(output) + "\n")
                memory += f"\nAI: {output}"

            else:
                print("\n👍 No changes applied.\n")
                memory += "\nAI: No changes applied."

            continue

        # =========================
        # 🔥 FAST PATH (NO LLM DELAY)
        # =========================
        if any(word in lower for word in ["truck plan", "truck schedule"]):
            output = run_graph_agent("truck schedule")
            print("\n" + str(output) + "\n")
            memory += f"\nAI: {output}"
            continue

        if "truck utilization" in lower:
            output = run_graph_agent("truck utilization report")
            print("\n" + str(output) + "\n")
            memory += f"\nAI: {output}"
            continue

        if "reconciliation" in lower:
            output = run_graph_agent("reconciliation report")
            print("\n" + str(output) + "\n")
            memory += f"\nAI: {output}"
            continue

        if "adherence" in lower:
            output = run_graph_agent("adherence report")
            print("\n" + str(output) + "\n")
            memory += f"\nAI: {output}"
            continue

        # =========================
        # LLM DECISION
        # =========================
        decision = process_with_llm(user_input, memory)
        action = decision.get("action", "execute")

        # =========================
        # ASK FLOW
        # =========================
        if action == "ask":

            question = decision.get("question", "Can you clarify?")

            if "hi" in lower or "hello" in lower:
                print(f"\n{get_greeting()}! How can I help you today?\n")
            else:
                print("\n" + question + "\n")

            memory += f"\nAI: {question}"
            continue

        # =========================
        # EXECUTE FLOW
        # =========================
        elif action == "execute":

            output = run_graph_agent(user_input)

            print("\n" + str(output) + "\n")
            memory += f"\nAI: {output}"

        # =========================
        # DIRECT FLOW
        # =========================
        elif action == "direct":

            query = decision.get("query", user_input)
            response = llm.invoke(query)

            print("\n" + response.content + "\n")
            memory += f"\nAI: {response.content}"

        else:
            print("\nSomething went wrong.\n")