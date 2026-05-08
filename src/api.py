# from fastapi import FastAPI, UploadFile, File, Form
# from pydantic import BaseModel
# import pandas as pd

# # =========================
# # TOOLS
# # =========================
# from src.tools.planning.truck_scheduling_tool import create_truck_schedule
# from src.tools.dispatch.truck_utilization_tool import check_truck_utilization
# from src.tools.utilization.adherence_tool import check_dispatch_adherence

# # =========================
# # UTILS
# # =========================
# from src.utils.modifier import modify_output
# from src.chat.chat_agent import generate_chat_response

# # =========================
# # SESSION STORE
# # =========================
# from src.sessions.store import (
#     get_session,
#     append_history,
#     reset_session
# )

# app = FastAPI()

# print("🔥 SKILL CHAT API LOADED 🔥")


# # =========================
# # REQUEST MODEL
# # =========================
# class ChatRequest(BaseModel):
#     query: str


# # =========================
# # HEALTH
# # =========================
# @app.get("/")
# def home():
#     return {"message": "Skill Chat API Running 🚀"}


# # =========================
# # HELPERS
# # =========================
# def load_excel_data(files):

#     data = {}

#     for file in files:

#         filename = file.filename.lower()

#         if filename.endswith(".xlsx"):

#             excel = pd.ExcelFile(file.file)

#             # 🚛 DISPATCH
#             if "dispatch_plan" in excel.sheet_names:
#                 df_dispatch = pd.read_excel(excel, "dispatch_plan")
#                 data["dispatch"] = df_dispatch.to_dict(orient="records")

#             # 📊 UTILIZATION
#             if "capacity_utilization" in excel.sheet_names:
#                 df_util = pd.read_excel(excel, "capacity_utilization")
#                 data["utilization"] = df_util.to_dict(orient="records")

#             # 📦 PO
#             if "po" in excel.sheet_names:
#                 df_po = pd.read_excel(excel, "po")
#                 data["po"] = df_po.to_dict(orient="records")

#     return data


# # =========================
# # 🚛 TRUCK CHAT
# # =========================
# @app.post("/truck-chat")
# async def truck_chat(
#     query: str = Form(...),
#     files: list[UploadFile] = File(None)
# ):

#     session = get_session("truck_chat")

#     # =========================
#     # LOAD FILE
#     # =========================
#     if files:
#         session["data"] = load_excel_data(files)

#     data = session["data"]

#     # =========================
#     # MODIFY OUTPUT
#     # =========================
#     if "modify" in query.lower():

#         updated = modify_output(
#             session["last_output"],
#             query
#         )

#         session["last_output"] = updated
#         append_history("truck_chat", updated)

#         chat_response = generate_chat_response(
#             user_query=query,
#             tool_output=updated,
#             history=session["history"],
#             skill="truck scheduling"
#         )

#         return {
#             "response": chat_response,
#             "data": updated
#         }

#     # =========================
#     # GENERATE SCHEDULE
#     # =========================
#     result = create_truck_schedule.invoke({
#         "data": {
#             "dispatch": data.get("dispatch", [])
#         }
#     })

#     output = result.get("schedule", [])

#     session["last_output"] = output
#     append_history("truck_chat", output)

#     # 🔥 HUMAN RESPONSE
#     chat_response = generate_chat_response(
#         user_query=query,
#         tool_output=output,
#         history=session["history"],
#         skill="truck scheduling"
#     )

#     return {
#         "response": chat_response,
#         "data": output
#     }


# # =========================
# # 📊 UTILIZATION CHAT
# # =========================
# # =========================
# # 📊 UTILIZATION CHAT
# # =========================
# @app.post("/utilization-chat")
# async def utilization_chat(
#     query: str = Form(...),
#     files: list[UploadFile] = File(None)
# ):

#     session = get_session("utilization_chat")

#     # =========================
#     # LOAD FILE
#     # =========================
#     if files:
#         session["data"] = load_excel_data(files)

#     data = session["data"]

#     # =========================
#     # MODIFY OUTPUT
#     # =========================
#     if "modify" in query.lower():

#         updated = modify_output(
#             session["last_output"],
#             query
#         )

#         session["last_output"] = updated
#         append_history("utilization_chat", updated)

#         chat_response = generate_chat_response(
#             user_query=query,
#             tool_output=updated,
#             history=session["history"],
#             skill="truck utilization"
#         )

#         return {
#             "response": chat_response,
#             "data": updated
#         }

#     # =========================
#     # GENERATE UTILIZATION
#     # =========================
#     result = check_truck_utilization.invoke({
#         "data": {
#             "dispatch": data.get("dispatch", [])
#         }
#     })

#     output = result.get("truck_utilization", [])

#     session["last_output"] = output
#     append_history("utilization_chat", output)

#     # =========================
#     # AI RESPONSE
#     # =========================
#     chat_response = generate_chat_response(
#         user_query=query,
#         tool_output=output,
#         history=session["history"],
#         skill="truck utilization"
#     )

#     return {
#         "response": chat_response,
#         "data": output
#     }
# # =========================
# # 📦 ADHERENCE CHAT
# # =========================
# @app.post("/adherence-chat")
# async def adherence_chat(
#     query: str = Form(...),
#     files: list[UploadFile] = File(None)
# ):

#     session = get_session("adherence_chat")

#     # =========================
#     # LOAD FILE
#     # =========================
#     if files:
#         session["data"] = load_excel_data(files)

#     data = session["data"]

#     # =========================
#     # GENERATE ADHERENCE
#     # =========================
#     result = check_dispatch_adherence.invoke({
#         "data": {
#             "dispatch": data.get("dispatch", [])
#         }
#     })

#     output = result.get("adherence", [])

#     session["last_output"] = output
#     append_history("adherence_chat", output)

#     # 🔥 HUMAN RESPONSE
#     chat_response = generate_chat_response(
#         user_query=query,
#         tool_output=output,
#         history=session["history"],
#         skill="dispatch adherence"
#     )

#     return {
#         "response": chat_response,
#         "data": output
#     }


from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
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
from src.utils.file_handler import upload_report, extract_text   # ✅ NEW
from src.chat.chat_agent import generate_chat_response

# =========================
# SESSION STORE
# =========================
from src.sessions.store import (
    get_session,
    append_history,
    reset_session,
    save_session,           # ✅ NEW
    update_session_data     # ✅ NEW
)

app = FastAPI()

# ✅ NEW — CORS so UI can talk to Cloud Run
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🔥 SKILL CHAT API LOADED 🔥")


# =========================
# REQUEST MODEL
# =========================
class ChatRequest(BaseModel):
    query: str


# =========================
# ✅ NEW — HEALTH CHECK
# Cloud Run needs this to confirm container started
# =========================
@app.get("/health")
def health():
    return {"status": "healthy"}


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"message": "Skill Chat API Running 🚀"}


# =========================
# ✅ NEW — FILE UPLOAD
# UI calls this first before sending chat messages
# =========================
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    chat_name: str = Form(...)   # e.g. "truck_chat"
):
    file_bytes = await file.read()
    filename = file.filename

    # Upload to GCS and extract text for LLM context
    gcs_uri = upload_report(file_bytes, filename, chat_name)
    file_context = extract_text(file_bytes, filename)

    # Save GCS URI + extracted text into the session
    update_session_data(chat_name, {
        "file_uri": gcs_uri,
        "file_name": filename,
        "file_context": file_context,
    })

    return {
        "status": "ok",
        "file_uri": gcs_uri,
        "filename": filename,
        "preview": file_context[:200]
    }


# =========================
# ✅ NEW — RESET SESSION
# UI calls this when user clicks "New Chat"
# =========================
@app.post("/reset")
async def reset_chat(chat_name: str = Form(...)):
    reset_session(chat_name)
    return {"status": "ok", "message": f"{chat_name} session cleared"}


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
        save_session("truck_chat", session)   # ✅ NEW — persist to Firestore

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
        save_session("truck_chat", session)   # ✅ NEW
        append_history("truck_chat", {"role": "user", "content": query})        # ✅ NEW — proper format
        append_history("truck_chat", {"role": "assistant", "content": str(updated)})  # ✅ NEW

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
    save_session("truck_chat", session)       # ✅ NEW — persist to Firestore
    append_history("truck_chat", {"role": "user", "content": query})           # ✅ NEW
    append_history("truck_chat", {"role": "assistant", "content": str(output)}) # ✅ NEW

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
        save_session("utilization_chat", session)   # ✅ NEW

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
        save_session("utilization_chat", session)   # ✅ NEW
        append_history("utilization_chat", {"role": "user", "content": query})
        append_history("utilization_chat", {"role": "assistant", "content": str(updated)})

        chat_response = generate_chat_response(
            user_query=query,
            tool_output=updated,
            history=session["history"],
            skill="truck utilization"
        )

        return {
            "response": chat_response,
            "data": updated
        }

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
    save_session("utilization_chat", session)       # ✅ NEW
    append_history("utilization_chat", {"role": "user", "content": query})
    append_history("utilization_chat", {"role": "assistant", "content": str(output)})

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
        save_session("adherence_chat", session)     # ✅ NEW

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
    save_session("adherence_chat", session)         # ✅ NEW
    append_history("adherence_chat", {"role": "user", "content": query})
    append_history("adherence_chat", {"role": "assistant", "content": str(output)})

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