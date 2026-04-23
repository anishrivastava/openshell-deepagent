

# import pytesseract
# import cv2
# import numpy as np
# import base64
# import json
# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI

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
# # BASE64
# # =========================
# def encode_bytes(image_bytes):
#     return base64.b64encode(image_bytes).decode("utf-8")


# # =========================
# # VISION
# # =========================
# def analyze_image_bytes(image_bytes, stage):

#     base64_image = encode_bytes(image_bytes)

#     prompt = f"""
# You are a STRICT audit AI.

# Check image for stage: {stage}

# IMPORTANT RULES:
# - If truck is NOT clearly visible → return ISSUE
# - If unsure → return ISSUE
# - Do NOT guess
# - Do NOT assume

# Return ONLY JSON:
# {{
#   "status": "OK or ISSUE",
#   "reason": "what exactly you saw"
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
# # GOVERNANCE TOOL (FINAL)
# # =========================
# @tool
# def check_governance(image: bytes, stage: str = "loading"):
#     """
#     Governance check using uploaded image
#     """

#     if not image:
#         return {"status": "failed", "message": "No image provided"}

#     # OCR
#     text = extract_text_from_bytes(image)

#     # Vision
#     vision = analyze_image_bytes(image, stage)

#     vision_status = vision.get("status", "ERROR")
#     vision_reason = vision.get("reason", "")

#     # =========================
#     # SIMPLE VALIDATION
#     # =========================
#     if stage == "loading":
#         if vision_status == "ISSUE":
#             status = "NO_TRUCK 🚨"
#             remark = vision_reason
#         elif "truck" not in vision_reason.lower():
#             status = "SUSPECT ⚠️"
#             remark = "Model unsure about truck presence"
#         else:
#             status = "OK ✅"
#             remark = "Truck clearly detected"

#     elif stage == "seal_close":
#         if vision_status == "ISSUE" and "SEAL" not in text:
#             status = "SEAL_MISSING 🚨"
#             remark = "Seal not detected"
#         else:
#             status = "OK ✅"
#             remark = "Seal verified"

#     else:
#         status = vision_status
#         remark = vision_reason

#     return {
#         "status": "success",
#         "governance": [
#             {
#                 "stage": stage,
#                 "status": status,
#                 "remark": remark
#             }
#         ]
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

        if img is None:
            return ""

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
# VISION (STRICT)
# =========================
def analyze_image_bytes(image_bytes, stage):

    base64_image = encode_bytes(image_bytes)

    # 🔥 STAGE SPECIFIC PROMPT
    if stage == "loading":
        prompt = """
You are a STRICT compliance AI.

Check:
1. Is a truck clearly visible?
2. Is a truck number visible?

If unsure → ISSUE

Return JSON:
{
 "status": "OK or ISSUE",
 "truck_present": "YES or NO",
 "truck_number_visible": "YES or NO",
 "reason": "what exactly you see"
}
"""

    elif stage == "box_scan":
        prompt = """
You are a STRICT compliance AI.

Check:
1. Is a BOX/CARTON visible?
2. Is a LABEL or BARCODE visible?

If missing → ISSUE

Return JSON:
{
 "status": "OK or ISSUE",
 "box_present": "YES or NO",
 "label_visible": "YES or NO",
 "reason": "what exactly you see"
}
"""

    else:
        prompt = f"""
Check image for stage: {stage}

Return JSON:
{{
 "status": "OK or ISSUE",
 "reason": "what you see"
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
    Compliance governance tool:
    - Detect truck presence
    - Detect truck number using OCR
    - Validate box and label
    - Return compliance status
    """

    if not image:
        return {"status": "failed", "message": "No image provided"}

    # 🔥 OCR
    text = extract_text_from_bytes(image)

    # 🔥 Vision
    vision = analyze_image_bytes(image, stage)

    vision_status = vision.get("status", "ERROR")
    reason = vision.get("reason", "")

    # =========================
    # OCR CHECK (NUMBER / LABEL)
    # =========================
    has_numbers = any(char.isdigit() for char in text)

    # =========================
    # FINAL COMPLIANCE LOGIC
    # =========================

    # 🚚 LOADING
    if stage == "loading":

        if vision_status == "ISSUE":
            status = "NO_TRUCK 🚨"
            remark = reason

        elif not has_numbers:
            status = "NO_TRUCK_NUMBER ⚠️"
            remark = "Truck present but number missing"

        else:
            status = "COMPLIANT ✅"
            remark = "Truck + number verified"

    # 📦 BOX SCAN
    elif stage == "box_scan":

        if vision_status == "ISSUE":
            status = "NO_BOX 🚨"
            remark = reason

        elif len(text.strip()) < 5:
            status = "NO_LABEL 🚨"
            remark = "Label / barcode not readable"

        else:
            status = "COMPLIANT ✅"
            remark = "Box + label verified"

    # 🔐 SEAL
    elif stage == "seal_close":

        if vision_status == "ISSUE" and "SEAL" not in text:
            status = "SEAL_MISSING 🚨"
            remark = "Seal not detected"

        else:
            status = "COMPLIANT ✅"
            remark = "Seal verified"

    else:
        status = vision_status
        remark = reason

    return {
        "status": "success",
        "governance": [
            {
                "stage": stage,
                "status": status,
                "remark": remark,
                "ocr_sample": text[:50]
            }
        ]
    }