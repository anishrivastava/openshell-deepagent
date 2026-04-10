from fastapi import FastAPI
from pydantic import BaseModel

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
# MAIN ENDPOINT
# =========================
@app.post("/ask")
def ask_agent(request: QueryRequest):

    user_input = request.query

    try:
        # 🔥 classify intent
        intent = classify_intent(user_input)

        # 🔥 run graph
        result = graph.invoke({
            "user_input": user_input,
            "intent": intent,
            "result": "",
            "data": []
        })

        return {
            "query": user_input,
            "intent": intent,
            "response": result.get("result", "No result generated")
        }

    except Exception as e:
        return {"error": str(e)}