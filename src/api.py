from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import pandas as pd
from typing import List
from fastapi import HTTPException
from typing import Dict, Any
import json
from langchain_openai import ChatOpenAI

from tools.dispatch.truck_utilization_tool import check_truck_utilization

from graph.graph import graph
from intent_classifier import classify_intent

app = FastAPI()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

print("🔥 NEW API VERSION LOADED 🔥")


# =========================
# REQUEST SCHEMA
# =========================
class QueryRequest(BaseModel):
    query: str

class SaveConfigRequest(BaseModel):
    data: Dict[str, Any]
    datatype_config: Dict[str, str]
    parameter_config: Dict[str, Any]


class RunAgentRequest(BaseModel):
    data: Dict[str, Any]
    datatype_config: Dict[str, str]
    parameter_config: Dict[str, Any]




def detect_column_type(series):
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    elif pd.api.types.is_float_dtype(series):
        return "float"
    elif pd.api.types.is_bool_dtype(series):
        return "boolean"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    return "string"


def validate_and_convert_dataframe(df, datatype_config):
    errors = []

    for column, dtype in datatype_config.items():

        if column not in df.columns:
            continue

        try:
            if dtype == "integer":
                df[column] = pd.to_numeric(df[column], errors="raise").astype(int)

            elif dtype == "float":
                df[column] = pd.to_numeric(df[column], errors="raise").astype(float)

            elif dtype == "datetime":
                df[column] = pd.to_datetime(df[column], errors="raise")

            elif dtype == "boolean":
                df[column] = df[column].astype(bool)

            elif dtype == "string":
                df[column] = df[column].astype(str)

        except Exception:
            errors.append(f"Column '{column}' could not be converted to {dtype}")

    return df, errors




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
    # CREATE EXCEL FILE
    # =========================
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        template_df.to_excel(writer, sheet_name="Template", index=False)


    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=truck_utilization_template.xlsx"
        }
    )

#----------------------------------
#GENERATE CONETEXT ENDPOINT 
#-----------------------------

@app.post("/generate-context/truck-utilization")
async def generate_truck_utilization_context(file: UploadFile = File(...)):

    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        elif file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported")

        df.columns = df.columns.str.strip().str.lower()

        detected_columns = []

        for column in df.columns:
            detected_columns.append({
                "column_name": column,
                "detected_type": detect_column_type(df[column]),
                "editable_type": detect_column_type(df[column])
            })

        parameter_config = {
            "low_utilization_threshold": {
                "label": "Low Utilization Threshold",
                "value": 50,
                "type": "number",
                "min": 0,
                "max": 100,
                "description": "Trucks below this utilization percentage are considered underutilized"
            },
            "medium_utilization_threshold": {
                "label": "Medium Utilization Threshold",
                "value": 80,
                "type": "number",
                "min": 0,
                "max": 100,
                "description": "Trucks below this utilization percentage are considered moderately utilized"
            },
            "max_results": {
                "label": "Maximum Results",
                "value": 25,
                "type": "number",
                "min": 1,
                "max": 100,
                "description": "Maximum number of truck records returned in the final output"
            }
        }

        data_dictionary = []

        for column in df.columns:
            data_dictionary.append({
                "column_name": column,
                "datatype": detect_column_type(df[column]),
                "description": f"Business column for {column.replace('_', ' ')}"
            })

        business_context = (
            "This agent analyzes truck-level loading efficiency by comparing shipped cases "
            "against truck carrying capacity. It identifies underutilized trucks, route inefficiencies, "
            "and opportunities to optimize freight cost."
        )

        return {
            "status": "success",
            "file_name": file.filename,
            "preview_data": df.head(10).fillna("").to_dict(orient="records"),
            "columns": detected_columns,
            "parameters": parameter_config,
            "data_dictionary": data_dictionary,
            "business_context": business_context
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#---------------------------------
#RUN AGENT ENDPOINT
#----------------------------------

@app.post("/run-agent/truck-utilization")
def run_truck_utilization_agent(request: RunAgentRequest):

    try:
        dispatch_data = request.data.get("dispatch", [])

        if not dispatch_data:
            return {
                "status": "failed",
                "message": "No dispatch data provided"
            }

        df = pd.DataFrame(dispatch_data)
        df.columns = df.columns.str.strip().str.lower()

        df, errors = validate_and_convert_dataframe(df, request.datatype_config)

        if errors:
            return {
                "status": "failed",
                "errors": errors
            }

        cleaned_data = {
            "dispatch": df.to_dict(orient="records")
        }

        result = check_truck_utilization.invoke({
            "data": cleaned_data,
            "config": request.parameter_config
        })

        truck_results = result.get("truck_utilization", [])

        summary_prompt = f"""
        You are a logistics analyst.

        Analyze the following truck utilization output and generate:
        1. Overall summary
        2. Major risks
        3. Best performing routes
        4. Underutilized truck count
        5. Recommendations

        Keep the word limit to 150 words and use bullet points for clarity.

        Truck Utilization Data:
        {truck_results}
        """

        summary_response = llm.invoke(summary_prompt)
        summary_text = summary_response.content

        return {
            "status": "success",
            "result": result,
            "summary": summary_text
        }

    except Exception as e:
        return {
            "status": "failed",
            "message": str(e)
        }