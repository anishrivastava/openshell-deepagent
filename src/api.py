# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from pydantic import BaseModel
# import pandas as pd
# from typing import List, Dict, Any
# from langchain_openai import ChatOpenAI
# from src.llama.index import query_engine

# from src.tools.dispatch.truck_utilization_tool import check_truck_utilization
# from src.graph.graph import graph
# from src.intent_classifier import classify_intent

# app = FastAPI()

# llm = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0
# )

# print("🔥 NEW API VERSION LOADED 🔥")

# # =========================
# # 🔥 CHAT MEMORY (SESSION BASED)
# # =========================
# chat_sessions = {}


# # =========================
# # 🔥 DYNAMIC QUERY ENGINE + MEMORY
# # =========================
# def run_dynamic_query(data, user_query, session_id="default"):

#     import pandas as pd
#     import re

#     if not data or "dispatch" not in data:
#         return "No data available"

#     df = pd.DataFrame(data["dispatch"])
#     df.columns = df.columns.str.lower()

#     # 🔥 NORMALIZE
#     if "truck" in df.columns:
#         df["truck"] = df["truck"].astype(str).str.upper().str.replace(" ", "")

#     # =========================================================
#     # 🔥 RULE-BASED ENGINE (FAST + SAFE)
#     # =========================================================

#     query_lower = user_query.lower()

#     # 🔹 MULTI TRUCK (9MT + 16MT)
#     truck_matches = re.findall(r'(\d+\s*mt)', query_lower)
#     truck_list = [t.replace(" ", "").upper() for t in truck_matches]

#     # 🔹 DESTINATION (masked id)
#     dest_match = re.search(r'for\s+([a-zA-Z0-9]+)', user_query)

#     # ✅ CASE 1: MULTIPLE TRUCKS
#     if len(truck_list) >= 2:
#         return f"Total result: {df[df['truck'].isin(truck_list)]['cases'].sum()}"

#     # ✅ CASE 2: DESTINATION + TRUCK
#     if len(truck_list) == 1 and dest_match:
#         truck = truck_list[0]
#         destination = dest_match.group(1)

#         if "destination" in df.columns:
#             result = df[
#                 (df["truck"] == truck) &
#                 (df["destination"] == destination)
#             ]["cases"].sum()

#             return f"Total result: {result}"

#     # =========================================================
#     # 🔥 LLAMAINDEX + LLM FALLBACK
#     # =========================================================

#     context = str(query_engine.query(user_query))

#     prompt = f"""
# You are a Python data analyst.

# STRICTLY follow the business context below.

# Business Context:
# {context}

# DataFrame name: df
# Columns: {list(df.columns)}

# RULES:
# - Return ONLY valid Python code
# - No explanation
# - Single expression only
# - Use .isin() for multiple values
# - Never use 'and' for filtering
# - Always valid pandas syntax

# User Query:
# {user_query}
# """

#     try:
#         code = llm.invoke(prompt).content.strip()
#         code = code.replace("```python", "").replace("```", "").strip()

#         print("🔥 QUERY:", user_query)
#         print("🔥 CONTEXT:", context)
#         print("🔥 CODE:", code)

#         # 🔥 FIX AND → OR
#         if " and " in code and "df[" in code:
#             code = code.replace(" and ", " | ")

#         result = eval(code, {"df": df, "__builtins__": {}})
#         return f"Total result: {result}"

#     except Exception as e:
#         print("❌ BAD CODE:", code)

#         # 🔁 RETRY FIX
#         try:
#             retry_prompt = f"""
# Fix this pandas code.

# Bad Code:
# {code}

# Rules:
# - Must be valid pandas syntax
# - Use .isin() if multiple values
# - Return only corrected code
# """

#             fixed_code = llm.invoke(retry_prompt).content.strip()
#             fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()

#             print("🔁 FIXED CODE:", fixed_code)

#             result = eval(fixed_code, {"df": df})
#             return f"Total result: {result}"

#         except Exception as e2:
#             return f"Error: {str(e2)}"
# # =========================
# # REQUEST SCHEMA
# # =========================
# class QueryRequest(BaseModel):
#     query: str


# class SaveConfigRequest(BaseModel):
#     data: Dict[str, Any]
#     datatype_config: Dict[str, str]
#     parameter_config: Dict[str, Any]


# class RunAgentRequest(BaseModel):
#     data: Dict[str, Any]
#     datatype_config: Dict[str, str]
#     parameter_config: Dict[str, Any]


# # =========================
# # HELPERS
# # =========================
# def detect_column_type(series):
#     if pd.api.types.is_integer_dtype(series):
#         return "integer"
#     elif pd.api.types.is_float_dtype(series):
#         return "float"
#     elif pd.api.types.is_bool_dtype(series):
#         return "boolean"
#     elif pd.api.types.is_datetime64_any_dtype(series):
#         return "datetime"
#     return "string"


# def validate_and_convert_dataframe(df, datatype_config):
#     errors = []

#     for column, dtype in datatype_config.items():
#         if column not in df.columns:
#             continue

#         try:
#             if dtype == "integer":
#                 df[column] = pd.to_numeric(df[column], errors="raise").astype(int)

#             elif dtype == "float":
#                 df[column] = pd.to_numeric(df[column], errors="raise").astype(float)

#             elif dtype == "datetime":
#                 df[column] = pd.to_datetime(df[column], errors="raise")

#             elif dtype == "boolean":
#                 df[column] = df[column].astype(bool)

#             elif dtype == "string":
#                 df[column] = df[column].astype(str)

#         except Exception:
#             errors.append(f"Column '{column}' could not be converted to {dtype}")

#     return df, errors


# # =========================
# # HEALTH CHECK
# # =========================
# @app.get("/")
# def home():
#     return {"message": "AI Agent Running 🚀"}


# # =========================
# # TEXT ONLY
# # =========================
# @app.post("/ask")
# def ask_agent(request: QueryRequest):
#     try:
#         intent = classify_intent(request.query)

#         result = graph.invoke({
#             "user_input": request.query,
#             "intent": intent,
#             "data": None,
#             "image": None,
#             "invoice": None,
#             "result": ""
#         })

#         return {
#             "query": request.query,
#             "intent": intent,
#             "response": result.get("result", "No result generated")
#         }

#     except Exception as e:
#         return {"error": str(e)}


# # =========================
# # MAIN ENDPOINT
# # =========================
# @app.post("/process-v2")
# async def process_agent(
#     query: str = Form(...),
#     files: list[UploadFile] = File(...)
# ):
#     try:
#         intent = classify_intent(query)

#         data = {}
#         image_bytes = None
#         invoice_bytes = None

#         # FILE HANDLING
#         for file in files:
#             filename = file.filename.lower()

#             if "po" in filename and filename.endswith(".csv"):
#                 df = pd.read_csv(file.file)
#                 data["po"] = df.to_dict(orient="records")

#             elif "dispatch" in filename and filename.endswith(".csv"):
#                 df = pd.read_csv(file.file)
#                 data["dispatch"] = df.to_dict(orient="records")

#             elif filename.endswith(".xlsx"):
#                 excel = pd.ExcelFile(file.file)

#                 if "dispatch_plan" in excel.sheet_names:
#                     df_dispatch = pd.read_excel(excel, "dispatch_plan")
#                     data["dispatch"] = df_dispatch.to_dict(orient="records")

#                 if "capacity_utilization" in excel.sheet_names:
#                     df_util = pd.read_excel(excel, "capacity_utilization")
#                     data["utilization"] = df_util.to_dict(orient="records")

#                 if "po" in excel.sheet_names:
#                     df_po = pd.read_excel(excel, "po")
#                     data["po"] = df_po.to_dict(orient="records")

#             elif filename.endswith((".png", ".jpg", ".jpeg")):
#                 image_bytes = await file.read()

#             elif filename.endswith(".pdf"):
#                 invoice_bytes = await file.read()

#         data["query"] = query

#         # 🔥 SESSION ID (for now static, later from frontend)
#         session_id = "user_1"

#         # 🔥 DYNAMIC + MEMORY
#         if intent == "unknown" and "dispatch" in data:
#             dynamic_result = run_dynamic_query(data, query, session_id)

#             return {
#                 "query": query,
#                 "intent": "dynamic_query",
#                 "response": dynamic_result
#             }

#         # NORMAL FLOW
#         result = graph.invoke({
#             "user_input": query,
#             "intent": intent,
#             "data": data,
#             "image": image_bytes,
#             "invoice": invoice_bytes,
#             "result": ""
#         })

#         return {
#             "query": query,
#             "intent": intent,
#             "response": result.get("result", "No output generated")
#         }

#     except Exception as e:
#         return {"error": str(e)}


# # =========================
# # DOWNLOAD TEMPLATE
# # =========================
# from fastapi.responses import StreamingResponse
# from io import BytesIO


# @app.get("/download-template/truck-utilization")
# def download_truck_utilization_template():
#     template_df = pd.DataFrame([{
#         "plant": "Bangalore Plant",
#         "city": "Hyderabad",
#         "truck": "16MT",
#         "trips": 2,
#         "capacity": 1600,
#         "utilization": 75,
#         "cases": 1200
#     }])

#     output = BytesIO()

#     with pd.ExcelWriter(output, engine="openpyxl") as writer:
#         template_df.to_excel(writer, sheet_name="Template", index=False)

#     output.seek(0)

#     return StreamingResponse(
#         output,
#         media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         headers={"Content-Disposition": "attachment; filename=truck_utilization_template.xlsx"}
#     )


# # =========================
# # RUN AGENT
# # =========================
# @app.post("/run-agent/truck-utilization")
# def run_truck_utilization_agent(request: RunAgentRequest):
#     try:
#         dispatch_data = request.data.get("dispatch", [])

#         if not dispatch_data:
#             return {"status": "failed", "message": "No dispatch data provided"}

#         df = pd.DataFrame(dispatch_data)
#         df.columns = df.columns.str.strip().str.lower()

#         df, errors = validate_and_convert_dataframe(df, request.datatype_config)

#         if errors:
#             return {"status": "failed", "errors": errors}

#         cleaned_data = {"dispatch": df.to_dict(orient="records")}

#         result = check_truck_utilization.invoke({
#             "data": cleaned_data,
#             "config": request.parameter_config
#         })

#         return {
#             "status": "success",
#             "result": result
#         }

#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import pandas as pd

# =========================
# TOOLS
# =========================
from src.tools.planning.truck_scheduling_tool import create_truck_schedule
from src.tools.dispatch.truck_utilization_tool import check_truck_utilization
from src.tools.utilization.adherence_tool import check_dispatch_adherence

# =========================
# UTILS
# =========================
from src.utils.modifier import modify_output
from src.chat.chat_agent import generate_chat_response

# =========================
# SESSION STORE
# =========================
from src.sessions.store import (
    get_session,
    append_history,
    reset_session
)

app = FastAPI()

print("🔥 SKILL CHAT API LOADED 🔥")


# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    query: str


# =========================
# HEALTH
# =========================
@app.get("/")
def home():
    return {"message": "Skill Chat API Running 🚀"}


# =========================
# HELPERS
# =========================
def load_excel_data(files):

    data = {}

    for file in files:

        filename = file.filename.lower()

        if filename.endswith(".xlsx"):

            excel = pd.ExcelFile(file.file)

            # 🚛 DISPATCH
            if "dispatch_plan" in excel.sheet_names:
                df_dispatch = pd.read_excel(excel, "dispatch_plan")
                data["dispatch"] = df_dispatch.to_dict(orient="records")

            # 📊 UTILIZATION
            if "capacity_utilization" in excel.sheet_names:
                df_util = pd.read_excel(excel, "capacity_utilization")
                data["utilization"] = df_util.to_dict(orient="records")

            # 📦 PO
            if "po" in excel.sheet_names:
                df_po = pd.read_excel(excel, "po")
                data["po"] = df_po.to_dict(orient="records")

    return data


# =========================
# 🚛 TRUCK CHAT
# =========================
@app.post("/truck-chat")
async def truck_chat(
    query: str = Form(...),
    files: list[UploadFile] = File(None)
):

    session = get_session("truck_chat")

    # =========================
    # LOAD FILE
    # =========================
    if files:
        session["data"] = load_excel_data(files)

    data = session["data"]

    # =========================
    # MODIFY OUTPUT
    # =========================
    if "modify" in query.lower():

        updated = modify_output(
            session["last_output"],
            query
        )

        session["last_output"] = updated
        append_history("truck_chat", updated)

        chat_response = generate_chat_response(
            user_query=query,
            tool_output=updated,
            history=session["history"],
            skill="truck scheduling"
        )

        return {
            "response": chat_response,
            "data": updated
        }

    # =========================
    # GENERATE SCHEDULE
    # =========================
    result = create_truck_schedule.invoke({
        "data": {
            "dispatch": data.get("dispatch", [])
        }
    })

    output = result.get("schedule", [])

    session["last_output"] = output
    append_history("truck_chat", output)

    # 🔥 HUMAN RESPONSE
    chat_response = generate_chat_response(
        user_query=query,
        tool_output=output,
        history=session["history"],
        skill="truck scheduling"
    )

    return {
        "response": chat_response,
        "data": output
    }


# =========================
# 📊 UTILIZATION CHAT
# =========================
@app.post("/utilization-chat")
async def utilization_chat(
    query: str = Form(...),
    files: list[UploadFile] = File(None)
):

    session = get_session("utilization_chat")

    # =========================
    # LOAD FILE
    # =========================
    if files:
        session["data"] = load_excel_data(files)

    data = session["data"]

    # =========================
    # GENERATE UTILIZATION
    # =========================
    result = check_truck_utilization.invoke({
        "data": {
            "dispatch": data.get("dispatch", [])
        }
    })

    output = result.get("truck_utilization", [])

    session["last_output"] = output
    append_history("utilization_chat", output)

    # 🔥 HUMAN RESPONSE
    chat_response = generate_chat_response(
        user_query=query,
        tool_output=output,
        history=session["history"],
        skill="truck utilization"
    )

    return {
        "response": chat_response,
        "data": output
    }


# =========================
# 📦 ADHERENCE CHAT
# =========================
@app.post("/adherence-chat")
async def adherence_chat(
    query: str = Form(...),
    files: list[UploadFile] = File(None)
):

    session = get_session("adherence_chat")

    # =========================
    # LOAD FILE
    # =========================
    if files:
        session["data"] = load_excel_data(files)

    data = session["data"]

    # =========================
    # GENERATE ADHERENCE
    # =========================
    result = check_dispatch_adherence.invoke({
        "data": {
            "dispatch": data.get("dispatch", [])
        }
    })

    output = result.get("adherence", [])

    session["last_output"] = output
    append_history("adherence_chat", output)

    # 🔥 HUMAN RESPONSE
    chat_response = generate_chat_response(
        user_query=query,
        tool_output=output,
        history=session["history"],
        skill="dispatch adherence"
    )

    return {
        "response": chat_response,
        "data": output
    }