

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

from graph.graph import graph
from intent_classifier import classify_intent

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

# Truck Utilization Template Download Logic

from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd


@app.get("/download-template/truck-utilization")
def download_truck_utilization_template():

    # =========================
    # TEMPLATE DATA
    # =========================
    template_df = pd.DataFrame([
        {
            "plant": "Bangalore Plant",
            "city": "Hyderabad",
            "truck": "16MT",
            "trips": 2,
            "capacity": 1600,
            "utilization": 75,
            "cases": 1200
        }
    ])

    # =========================
    # DATA DICTIONARY
    # =========================
    dictionary_df = pd.DataFrame([
        {
            "column_name": "plant",
            "description": "Manufacturing plant or warehouse from where the shipment is dispatched",
            "example": "Bangalore Plant",
            "mandatory": "Yes",
            "business_meaning": "Used to identify the shipment origin and analyze dispatch performance by plant"
        },
        {
            "column_name": "city",
            "description": "Destination city where the shipment is being delivered",
            "example": "Hyderabad",
            "mandatory": "Yes",
            "business_meaning": "Used to identify route destination and compare truck utilization across cities"
        },
        {
            "column_name": "truck",
            "description": "Truck type or vehicle category used for the shipment",
            "example": "16MT",
            "mandatory": "Yes",
            "business_meaning": "Used to estimate truck carrying capacity and identify whether the correct truck size is being used"
        },
        {
            "column_name": "trips",
            "description": "Number of trips made for the same route and shipment",
            "example": "2",
            "mandatory": "Yes",
            "business_meaning": "Used to calculate average load per trip and identify over-splitting of shipments"
            
        },
        {
            "column_name": "cases",
            "description": "Total number of product cases shipped across all trips",
            "example": "1200",
            "mandatory": "Yes",
            "business_meaning": "Used to calculate average load carried by the truck and overall utilization percentage"
        },
        {
            "column_name": "capacity",
            "description": "Maximum truck carrying capacity in number of cases",
            "example": "1600",
            "mandatory": "No",
            "business_meaning": "If not provided, the system automatically derives capacity from truck type"
        },
        {
            "column_name": "utilization",
            "description": "Percentage of truck capacity actually used",
            "example": "75",
            "mandatory": "No",
            "business_meaning": "Automatically calculated by the system to identify underutilized or overloaded trucks"
        }
    ])

    # =========================
    # BUSINESS CONTEXT
    # =========================
    context_df = pd.DataFrame([
        {
            "section": "Agent Name",
            "details": "Truck Utilization Agent"
        },
        {
            "section": "Objective",
            "details": "Analyze truck-level loading efficiency and identify routes where trucks are being underutilized"
        },
        {
            "section": "Business Problem",
            "details": "Many logistics operations use larger trucks than required, resulting in unused capacity, higher transportation cost, and inefficient route planning"
        },
        {
            "section": "How It Works",
            "details": "The agent compares total shipped cases against truck carrying capacity to calculate utilization percentage for every route"
        },
        {
            "section": "Required Inputs",
            "details": "plant, city, truck, trips, cases"
        },
        {
            "section": "System Generated Outputs",
            "details": "capacity (if not provided), utilization percentage, utilization status, route summary, and optimization alert"
        },
        {
            "section": "Business Value",
            "details": "Helps reduce freight cost, optimize truck selection, minimize empty space, and improve dispatch planning efficiency"
        },
        {
            "section": "Typical Recommendation",
            "details": "If a 16MT truck is carrying only 40 percent of its capacity, the system may recommend switching to a smaller truck such as 9MT"
        }
    ])

    # =========================
    # CREATE EXCEL FILE
    # =========================
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        template_df.to_excel(writer, sheet_name="Template", index=False)
        dictionary_df.to_excel(writer, sheet_name="Description", index=False)
        context_df.to_excel(writer, sheet_name="Business Context", index=False)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=truck_utilization_template.xlsx"
        }
    )

