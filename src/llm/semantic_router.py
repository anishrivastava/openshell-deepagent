import numpy as np
from langchain_openai import OpenAIEmbeddings

# Initialize embedding model
embeddings = OpenAIEmbeddings()


# 🔹 Define intents with examples
INTENTS = {
    "run_planning": [
        "run planning",
        "execute planning",
        "start supply plan",
        "run next month planning",
    ],
    "top_dispatch": [
        "top cities by dispatch",
        "highest shipment cities",
        "which cities have max dispatch",
        "where is delivery highest",
        "top delivery locations",
    ],
    "underutilized_plants": [
        "underutilized plants",
        "low utilization plants",
        "plants not used much",
        "which plants are idle",
        "plants with low capacity usage",
    
    ],
    "truck_schedule": [
    "create truck schedule",
    "how many trucks needed",
    "schedule trucks",
    "truck planning",
    ],
    "adherence": [
    "check adherence",
    "dispatch delay",
    "which trucks are delayed",
    "delivery status",
    ],
    "truck_utilization": [
    "truck utilization",
    "truck efficiency",
    "low truck load",
    "which trucks are underutilized"
    ],
    "reconciliation": [
    "check reconciliation",
    "invoice mismatch",
    "billing errors",
    "finance check"
    ],
    "governance": [
    "check governance",
    "validate process",
    "check compliance",
    "verify images",
    "truck validation",
    "is process followed correctly",
    "check proof of delivery",
    "validate truck loading",
    "check seal and lock",
    "image verification",
    "logistics compliance check",
    "was seal opened correctly",
    "check unloading proof"
],
}


# 🔹 Cosine similarity function
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# 🔹 Precompute intent vectors
intent_vectors = {}

for intent, examples in INTENTS.items():
    vectors = [embeddings.embed_query(text) for text in examples]
    intent_vectors[intent] = np.mean(vectors, axis=0)


# 🔹 Main function
def semantic_classify_intent(user_input: str) -> str:
    query_vec = embeddings.embed_query(user_input)

    best_intent = "unknown"
    best_score = -1

    for intent, vec in intent_vectors.items():
        score = cosine_similarity(query_vec, vec)

        if score > best_score:
            best_score = score
            best_intent = intent

    # 🔥 threshold (important)
    if best_score < 0.70:
        return "unknown"

    return best_intent