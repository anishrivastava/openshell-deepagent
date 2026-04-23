# """OpenShell Deep Agent.

# General-purpose coding and analysis agent using OpenShell as the on-prem
# sandbox provider. Executes code inside a policy-governed OpenShell sandbox
# with local filesystem persistence for memory and skills.

# Quick start:
#   1. Start or select a gateway: openshell gateway start
#   2. (Optional) Pre-create a sandbox: openshell sandbox create --name my-sandbox --keep
#      Then set: export OPENSHELL_SANDBOX_NAME=my-sandbox
#   3. Run: deepagents run src/agent.py:agent
# """

# import os
# from datetime import datetime

# from deepagents import create_deep_agent
# from langchain.chat_models import init_chat_model

# from src.backend import create_backend
# from langchain_nvidia_ai_endpoints import ChatNVIDIA
# from src.prompts import AGENT_INSTRUCTIONS

# current_date = datetime.now().strftime("%Y-%m-%d")

# model = ChatNVIDIA(
#     model="nvidia/nemotron-3-super-120b-a12b",
#     api_key=os.getenv("NVIDIA_API_KEY"),
#     temperature=0.1,
#     max_tokens=16384,
# )

# # model = init_chat_model(
# #    os.environ.get("AGENT_MODEL", "anthropic:claude-sonnet-4-6")
# # )

# agent = create_deep_agent(
#     model=model,
#     system_prompt=AGENT_INSTRUCTIONS.format(date=current_date),
#     memory=["/memory/AGENTS.md"],
#     backend=create_backend,
# )
# from langchain_openai import ChatOpenAI
# from langchain_core.tools import tool
# from langchain_core.messages import HumanMessage
# from langchain_core.runnables import RunnableLambda

# from src.tools.planning_tools import run_planning_tool


# # 🔹 LLM
# llm = ChatOpenAI(temperature=0)


# # 🔹 Bind tools to LLM
# tools = [run_planning_tool]
# llm_with_tools = llm.bind_tools(tools)


# def run_agent(user_input: str):
#     # Step 1: Send input to LLM
#     response = llm_with_tools.invoke([HumanMessage(content=user_input)])

#     # Step 2: If tool is called → execute it
#     if response.tool_calls:
#         tool_call = response.tool_calls[0]
#         tool_name = tool_call["name"]

#         if tool_name == "run_planning_tool":
#             result = run_planning_tool.invoke({})

#             return f"✅ Planning executed:\n{result}"

#     # Step 3: fallback (normal response)
#     return response.content
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.tools.utilization.utilization_tools import get_underutilized_plants

from src.tools.planning.planning_tools import run_planning_tool
from src.tools.dispatch.dispatch_tools import get_top_5_cities_by_dispatch
from src.prompts import SYSTEM_PROMPT
from langchain_experimental.tools import PythonREPLTool
python_tool = PythonREPLTool()
llm = ChatOpenAI(temperature=0)


tools = [run_planning_tool, get_top_5_cities_by_dispatch, get_underutilized_plants,python_tool]
llm_with_tools = llm.bind_tools(tools)


def run_agent(user_input: str):
    response = llm_with_tools.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input)
    ])

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]

        if tool_name == "run_planning_tool":
            result = run_planning_tool.invoke({})

            if result["status"] == "success":
                return (
                    "Planning completed successfully.\n\n"
                    f"Pipeline output:\n{result['output']}"
                )
            else:
                return (
                    "Planning execution failed.\n\n"
                    f"Error:\n{result['error']}"
                )

        elif tool_name == "get_top_5_cities_by_dispatch":
            result = get_top_5_cities_by_dispatch.invoke({})

            if result["status"] == "success":
                lines = []
                metric_col = result["metric_column"]

                for i, row in enumerate(result["top_5_cities"], start=1):
                    city = row["city"]
                    value = row[metric_col]
                    lines.append(f"{i}. {city} - {value:.2f}")

                return (
                    "Top 5 cities by dispatch:\n\n"
                    + "\n".join(lines)
                )
            else:
                return f"Error: {result['message']}"

        elif tool_name == "get_underutilized_plants":
            result = get_underutilized_plants.invoke({})

            if result["status"] == "success":
                lines = []
                plant_col = result["plant_column"]
                util_col = result["utilization_column"]

                for i, row in enumerate(result["underutilized_plants"], start=1):
                    plant = row[plant_col]
                    utilization = row[util_col]
                    lines.append(f"{i}. {plant} - {utilization:.2f}%")

                return (
                    "Most underutilized plants:\n\n"
                    + "\n".join(lines)
                )
            else:
                return f"Error: {result['message']}"

    return response.content