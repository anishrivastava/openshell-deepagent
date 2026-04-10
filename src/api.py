# from fastapi import FastAPI
# from pydantic import BaseModel

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
# # MAIN ENDPOINT
# # =========================
# @app.post("/ask")
# def ask_agent(request: QueryRequest):

#     user_input = request.query

#     try:
#         # 🔥 classify intent
#         intent = classify_intent(user_input)

#         # 🔥 run graph
#         result = graph.invoke({
#             "user_input": user_input,
#             "intent": intent,
#             "result": "",
#             "data": []
#         })

#         return {
#             "query": user_input,
#             "tent": intent,
#             "response": result.get("result", "No result generated")
#         }

#     except Exception as e:
#         return {"error": str(e)}

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import pandas as pd
from typing import Optional

from src.graph.graph import graph
from src.intent_classifier import classify_intent

app = FastAPI()

# =========================
# REQUEST SCHEMA (TEXT ONLY)
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

    user_input = request.query

    try:
        intent = classify_intent(user_input)

        result = graph.invoke({
            "user_input": user_input,
            "intent": intent,
            "data": []
        })

        return {
            "query": user_input,
            "intent": intent,
            "response": result.get("result", "No result generated")
        }

    except Exception as e:
        return {"error": str(e)}


# =========================
# MULTI INPUT ENDPOINT (🔥 MAIN)
# =========================
@app.post("/process")
async def process_agent(
    query: str = Form(...),
    file: Optional[UploadFile] = File(None)
):

    try:
        intent = classify_intent(query)

        data = None
        image_bytes = None

        # =========================
        # FILE HANDLING
        # =========================
        if file:

            # CSV CASE
            if file.filename.endswith(".csv"):
                df = pd.read_csv(file.file)
                data = df.to_dict(orient="records")

            # IMAGE CASE
            elif file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                image_bytes = await file.read()

        # =========================
        # GRAPH CALL
        # =========================
        result = graph.invoke({
            "user_input": query,
            "intent": intent,
            "data": data,
            "image": image_bytes,
            "result": ""
        })

        return {
            "query": query,
            "intent": intent,
            "response": result.get("result", "No output generated")
        }

    except Exception as e:
        return {"error": str(e)}