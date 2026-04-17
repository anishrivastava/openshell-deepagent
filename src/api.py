

# from fastapi import FastAPI, UploadFile, File, Form
# from pydantic import BaseModel
# import pandas as pd
# from typing import Optional

# from src.graph.graph import graph
# from src.intent_classifier import classify_intent

# app = FastAPI()


# # =========================
# # REQUEST SCHEMA
# # =========================
# class QueryRequest(BaseModel):
#     query: str


# # =========================
# # HEALTH CHECK
# # =========================
# @app.get("/")
# def home():
#     return {"message": "AI Agent Running 🚀"}


# # =========================
# # TEXT ONLY ENDPOINT
# # =========================
# @app.post("/ask")
# def ask_agent(request: QueryRequest):

#     user_input = request.query

#     try:
#         intent = classify_intent(user_input)

#         result = graph.invoke({
#             "user_input": user_input,
#             "intent": intent,
#             "data": None,
#             "image": None,
#             "result": ""
#         })

#         return {
#             "query": user_input,
#             "intent": intent,
#             "response": result.get("result", "No result generated")
#         }

#     except Exception as e:
#         return {"error": str(e)}


# # =========================
# # MULTI INPUT ENDPOINT
# # =========================
# @app.post("/process")
# async def process_agent(
#     query: str = Form(...),
#     file: Optional[UploadFile] = File(None)
# ):

#     try:
#         intent = classify_intent(query)

#         data = None
#         image_bytes = None

#         # =========================
#         # FILE HANDLING
#         # =========================
#         if file:

#             filename = file.filename.lower()

#             # CSV
#             if filename.endswith(".csv"):
#                 df = pd.read_csv(file.file)
#                 data = df.to_dict(orient="records")

#             # EXCEL (🔥 IMPORTANT FOR YOU)
#             elif filename.endswith(".xlsx"):
#                 excel = pd.ExcelFile(file.file)
#                 data = {}
#                 if "dispatch_plan" in excel.sheet_names:
#                     df_dispatch = pd.read_excel(excel, "dispatch_plan")
#                     data["dispatch"] = df_dispatch.to_dict(orient="records")
#                     if "capacity_utilization" in excel.sheet_names:
#                         df_util = pd.read_excel(excel, "capacity_utilization")
#                         data["utilization"] = df_util.to_dict(orient="records")

#             # IMAGE
#             elif filename.endswith((".png", ".jpg", ".jpeg")):
#                 image_bytes = await file.read()

#         # =========================
#         # GRAPH CALL
#         # =========================
#         result = graph.invoke({
#             "user_input": query,
#             "intent": intent,
#             "data": data,
#             "image": image_bytes,
#             "result": ""
#         })

#         return {
#             "query": query,
#             "intent": intent,
#             "response": result.get("result", "No output generated")
#         }

#     except Exception as e:
#         return {"error": str(e)}
print("🔥 NEW API VERSION LOADED 🔥")
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import pandas as pd
from typing import List

from src.graph.graph import graph
from src.intent_classifier import classify_intent

app = FastAPI()


# =========================
# REQUEST SCHEMA
# =========================
class QueryRequest(BaseModel):
    query: str


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"message": "AI Agent Running 🚀"}


# =========================
# TEXT ONLY ENDPOINT
# =========================
@app.post("/ask")
def ask_agent(request: QueryRequest):

    try:
        intent = classify_intent(request.query)

        result = graph.invoke({
            "user_input": request.query,
            "intent": intent,
            "data": None,
            "image": None,
            "invoice": None,
            "result": ""
        })

        return {
            "query": request.query,
            "intent": intent,
            "response": result.get("result", "No result generated")
        }

    except Exception as e:
        return {"error": str(e)}


# =========================
# MULTI-FILE ENDPOINT
# =========================
@app.post("/process-v2")   # 👈 CHANGE NAME
async def process_agent(
    query: str = Form(...),
    files: list[UploadFile] = File(...)
):

    try:
        intent = classify_intent(query)

        data = {}
        image_bytes = None
        invoice_bytes = None

        # =========================
        # MULTI FILE HANDLING
        # =========================
        for file in files:

            filename = file.filename.lower()

            # -------------------------
            # PO CSV
            # -------------------------
            if "po" in filename and filename.endswith(".csv"):
                df = pd.read_csv(file.file)
                data["po"] = df.to_dict(orient="records")

            # -------------------------
            # DISPATCH CSV
            # -------------------------
            elif "dispatch" in filename and filename.endswith(".csv"):
                df = pd.read_csv(file.file)
                data["dispatch"] = df.to_dict(orient="records")

            # -------------------------
            # EXCEL (OPTIONAL)
            # -------------------------
            elif filename.endswith(".xlsx"):
                excel = pd.ExcelFile(file.file)

                if "dispatch_plan" in excel.sheet_names:
                    df_dispatch = pd.read_excel(excel, "dispatch_plan")
                    data["dispatch"] = df_dispatch.to_dict(orient="records")

                if "capacity_utilization" in excel.sheet_names:
                    df_util = pd.read_excel(excel, "capacity_utilization")
                    data["utilization"] = df_util.to_dict(orient="records")

                if "po" in excel.sheet_names:
                    df_po = pd.read_excel(excel, "po")
                    data["po"] = df_po.to_dict(orient="records")

            # -------------------------
            # IMAGE (GOVERNANCE)
            # -------------------------
            elif filename.endswith((".png", ".jpg", ".jpeg")):
                image_bytes = await file.read()

            # -------------------------
            # PDF (INVOICE)
            # -------------------------6
            elif filename.endswith(".pdf"):
                invoice_bytes = await file.read()

        # =========================
        # GRAPH CALL
        # =========================
        result = graph.invoke({
            "user_input": query,
            "intent": intent,
            "data": data,
            "image": image_bytes,
            "invoice": invoice_bytes,
            "result": ""
        })

        return {
            "query": query,
            "intent": intent,
            "response": result.get("result", "No output generated")
        }

    except Exception as e:
        return {"error": str(e)}