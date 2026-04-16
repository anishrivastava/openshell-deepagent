


# from pathlib import Path
# import pandas as pd
# import pytesseract
# import cv2
# import base64
# import json
# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI

# # 🔥 Vision model (LangChain)
# vision_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# # 🔥 Set tesseract path (Windows)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# # =========================
# # OCR FUNCTION
# # =========================
# def extract_text(image_path: str):
#     try:
#         img = cv2.imread(image_path)

#         if img is None:
#             return ""

#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

#         text = pytesseract.image_to_string(gray)

#         return text.upper()

#     except Exception:
#         return ""


# # =========================
# # IMAGE → BASE64
# # =========================
# def encode_image(image_path):
#     try:
#         with open(image_path, "rb") as f:
#             return base64.b64encode(f.read()).decode("utf-8")
#     except Exception:
#         return None


# # =========================
# # VISION FUNCTION
# # =========================
# def analyze_image(image_path, stage):
#     base64_image = encode_image(image_path)

#     if base64_image is None:
#         return {"status": "ERROR", "reason": "Image not found"}

#     prompt = f"""
#     You are a supply chain audit AI.

#     Analyze the image for stage: {stage}

#     Rules:
#     - loading → check if truck is present
#     - seal_close → check if seal is visible
#     - seal_open → check if seal is opened
#     - box_scan → check if box and label visible
#     - warehouse_open → check if warehouse is open

#     Return STRICT JSON:
#     {{
#         "status": "OK or ISSUE",
#         "reason": "short explanation"
#     }}
#     """

#     try:
#         response = vision_llm.invoke([
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ])

#         content = response.content

#         # 🔥 FIX JSON formatting issue
#         content = content.replace("```json", "").replace("```", "").strip()

#         return json.loads(content)

#     except Exception as e:
#         return {"status": "ERROR", "reason": str(e)}


# # =========================
# # GOVERNANCE TOOL
# # =========================
# @tool
# def check_governance():
#     """
#     Governance validation using OCR + Vision AI
#     """

#     base_path = Path(r"C:\Users\shash\OneDrive\Desktop\AI_data")
#     file_path = base_path / "image_data.csv"

#     try:
#         df = pd.read_csv(file_path)
#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     df.columns = df.columns.str.strip().str.lower()

#     results = []

#     for _, row in df.iterrows():

#         truck_id = row.get("truck_id", "UNKNOWN")
#         stage = str(row.get("stage", "")).lower()
#         image_path = row.get("image_path", "")

#         # 🔥 OCR
#         text = extract_text(image_path)

#         # 🔥 Vision
#         vision_result = analyze_image(image_path, stage)

#         vision_status = vision_result.get("status", "ERROR")
#         vision_reason = vision_result.get("reason", "")

#         # =========================
#         # HYBRID VALIDATION LOGIC
#         # =========================

#         if stage == "box_scan":

#             expected_sn = str(row.get("expected_serial", "")).upper()

#             if not expected_sn:
#                 status = "NO_EXPECTED_SN ⚠️"
#                 remark = "Expected serial missing"

#             elif expected_sn not in text:
#                 status = "SERIAL_MISMATCH 🚨"
#                 remark = f"OCR failed: {expected_sn} not found"

#             elif vision_status == "ISSUE":
#                 status = "VISUAL_ISSUE 🚨"
#                 remark = vision_reason

#             else:
#                 status = "OK ✅"
#                 remark = "Serial + box verified"

#         elif stage == "loading":

#             if vision_status == "ISSUE":
#                 status = "NO_TRUCK 🚨"
#                 remark = vision_reason
#             else:
#                 status = "OK ✅"
#                 remark = "Truck detected"

#         elif stage == "seal_close":

#             if vision_status == "ISSUE" and "SEAL" not in text:
#                 status = "SEAL_MISSING 🚨"
#                 remark = "Seal not detected (OCR + Vision)"
#             else:
#                 status = "OK ✅"
#                 remark = "Seal verified"

#         elif stage == "seal_open":

#             if vision_status == "ISSUE":
#                 status = "NOT_OPENED 🚨"
#                 remark = vision_reason
#             else:
#                 status = "OK ✅"
#                 remark = "Seal opened"

#         elif stage == "warehouse_open":

#             if vision_status == "ISSUE":
#                 status = "NOT_OPENED 🚨"
#                 remark = vision_reason
#             else:
#                 status = "OK ✅"
#                 remark = "Warehouse opened"

#         else:
#             status = "UNKNOWN ⚠️"
#             remark = f"Stage '{stage}' not configured"

#         results.append({
#             "truck_id": truck_id,
#             "stage": stage,
#             "status": status,
#             "remark": remark
#         })

#     return {
#         "status": "success",
#         "governance": results[:25]
#     }

# import pytesseract
# import cv2
# import numpy as np
# import base64
# import json
# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI

# # 🔥 Vision model
# vision_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# # =========================
# # OCR FROM BYTES
# # =========================
# def extract_text_from_bytes(image_bytes):
#     try:
#         nparr = np.frombuffer(image_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

#         gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#         gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

#         text = pytesseract.image_to_string(gray)

#         return text.upper()

#     except Exception:
#         return ""


# # =========================
# # BASE64 ENCODE
# # =========================
# def encode_bytes(image_bytes):
#     return base64.b64encode(image_bytes).decode("utf-8")


# # =========================
# # VISION (IMAGE ANALYSIS)
# # =========================
# def analyze_image_bytes(image_bytes, stage):

#     base64_image = encode_bytes(image_bytes)

#     prompt = f"""
# You are a supply chain audit AI.

# Analyze the image for stage: {stage}

# Rules:
# - loading → check if truck is present
# - seal_close → check if seal is visible
# - seal_open → check if seal is opened
# - box_scan → check if box and label visible
# - warehouse_open → check if warehouse is open

# Return STRICT JSON:
# {{
#     "status": "OK or ISSUE",
#     "reason": "short explanation"
# }}
# """

#     try:
#         response = vision_llm.invoke([
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": prompt},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ])

#         content = response.content.replace("```json", "").replace("```", "").strip()
#         return json.loads(content)

#     except Exception as e:
#         return {"status": "ERROR", "reason": str(e)}


# # =========================
# # GOVERNANCE TOOL
# # =========================
# @tool
# def check_governance(data: dict):

#     input_data = data.get("images", [])

#     if not input_data:
#         return {"status": "failed", "message": "No image data provided"}

#     results = []

#     for row in input_data:

#         truck_id = row.get("truck_id", "UNKNOWN")
#         stage = str(row.get("stage", "")).lower()
#         image_bytes = row.get("image_bytes")

#         if not image_bytes:
#             continue

#         # 🔥 OCR (DIRECT FROM BYTES)
#         text = extract_text_from_bytes(image_bytes)

#         # 🔥 VISION (DIRECT FROM BYTES)
#         vision_result = analyze_image_bytes(image_bytes, stage)

#         vision_status = vision_result.get("status", "ERROR")
#         vision_reason = vision_result.get("reason", "")

#         # =========================
#         # VALIDATION LOGIC
#         # =========================

#         if stage == "box_scan":

#             expected_sn = str(row.get("expected_serial", "")).upper()

#             if not expected_sn:
#                 status = "NO_EXPECTED_SN ⚠️"
#                 remark = "Expected serial missing"

#             elif expected_sn not in text:
#                 status = "SERIAL_MISMATCH 🚨"
#                 remark = f"OCR failed: {expected_sn} not found"

#             elif vision_status == "ISSUE":
#                 status = "VISUAL_ISSUE 🚨"
#                 remark = vision_reason

#             else:
#                 status = "OK ✅"
#                 remark = "Serial + box verified"

#         elif stage == "loading":

#             if vision_status == "ISSUE":
#                 status = "NO_TRUCK 🚨"
#                 remark = vision_reason
#             else:
#                 status = "OK ✅"
#                 remark = "Truck detected"

#         elif stage == "seal_close":

#             if vision_status == "ISSUE" and "SEAL" not in text:
#                 status = "SEAL_MISSING 🚨"
#                 remark = "Seal not detected"
#             else:
#                 status = "OK ✅"
#                 remark = "Seal verified"

#         elif stage == "seal_open":

#             if vision_status == "ISSUE":
#                 status = "NOT_OPENED 🚨"
#                 remark = vision_reason
#             else:
#                 status = "OK ✅"
#                 remark = "Seal opened"

#         elif stage == "warehouse_open":

#             if vision_status == "ISSUE":
#                 status = "NOT_OPENED 🚨"
#                 remark = vision_reason
#             else:
#                 status = "OK ✅"
#                 remark = "Warehouse opened"

#         else:
#             status = "UNKNOWN ⚠️"
#             remark = f"Stage '{stage}' not configured"

#         results.append({
#             "truck_id": truck_id,
#             "stage": stage,
#             "status": status,
#             "remark": remark
#         })

#     return {
#         "status": "success",
#         "governance": results[:25]
#     }

import pytesseract
import cv2
import numpy as np
import base64
import json
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

vision_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# =========================
# OCR FROM BYTES
# =========================
def extract_text_from_bytes(image_bytes):
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(gray)
        return text.upper()

    except Exception:
        return ""


# =========================
# BASE64
# =========================
def encode_bytes(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


# =========================
# VISION
# =========================
def analyze_image_bytes(image_bytes, stage):

    base64_image = encode_bytes(image_bytes)

    prompt = f"""
Analyze image for stage: {stage}

Return STRICT JSON:
{{
  "status": "OK or ISSUE",
  "reason": "short explanation"
}}
"""

    try:
        response = vision_llm.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ])

        content = response.content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)

    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}


# =========================
# GOVERNANCE TOOL (FINAL)
# =========================
@tool
def check_governance(image: bytes, stage: str = "loading"):
    """
    Governance check using uploaded image
    """

    if not image:
        return {"status": "failed", "message": "No image provided"}

    # OCR
    text = extract_text_from_bytes(image)

    # Vision
    vision = analyze_image_bytes(image, stage)

    vision_status = vision.get("status", "ERROR")
    vision_reason = vision.get("reason", "")

    # =========================
    # SIMPLE VALIDATION
    # =========================
    if stage == "loading":
        if vision_status == "ISSUE":
            status = "NO_TRUCK 🚨"
            remark = vision_reason
        else:
            status = "OK ✅"
            remark = "Truck detected"

    elif stage == "seal_close":
        if vision_status == "ISSUE" and "SEAL" not in text:
            status = "SEAL_MISSING 🚨"
            remark = "Seal not detected"
        else:
            status = "OK ✅"
            remark = "Seal verified"

    else:
        status = vision_status
        remark = vision_reason

    return {
        "status": "success",
        "governance": [
            {
                "stage": stage,
                "status": status,
                "remark": remark
            }
        ]
    }