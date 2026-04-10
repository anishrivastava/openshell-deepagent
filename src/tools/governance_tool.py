# from pathlib import Path
# import pandas as pd
# from langchain_core.tools import tool


# @tool
# def run_governance_check():
#     """
#     Validate logistics process using image metadata.
#     """

#     base_path = Path(r"C:\Users\shash\OneDrive\Desktop\AI_data")

#     image_file = base_path / "image_data.csv"

#     try:
#         # ✅ FIX: use read_csv
#         df = pd.read_csv(image_file)

#         # ✅ Clean column names
#         df.columns = df.columns.str.strip().str.lower()

#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     results = []

#     trucks = df["truck_id"].unique()

#     for truck in trucks:
#         truck_data = df[df["truck_id"] == truck]

#         stages = truck_data["stage"].tolist()

#         truck_issues = []   # 🔥 track issues per truck

#         # 🔥 1. Loading check
#         if "loading" not in stages:
#             truck_issues.append({
#                 "truck_id": truck,
#                 "status": "MISSING_LOADING",
#                 "remark": "No loading proof"
#             })

#         # 🔥 2. Seal close check
#         if "seal_close" not in stages:
#             truck_issues.append({
#                 "truck_id": truck,
#                 "status": "MISSING_SEAL",
#                 "remark": "Seal not applied"
#             })

#         # 🔥 3. Seal open check
#         if "seal_open" not in stages:
#             truck_issues.append({
#                 "truck_id": truck,
#                 "status": "MISSING_UNSEAL",
#                 "remark": "No unloading proof"
#             })

#         # 🔥 4. Sequence check
#         try:
#             seal_close_times = truck_data[truck_data["stage"] == "seal_close"]["timestamp"]
#             seal_open_times = truck_data[truck_data["stage"] == "seal_open"]["timestamp"]

#             if not seal_close_times.empty and not seal_open_times.empty:
#                 seal_close_time = pd.to_datetime(seal_close_times.min())
#                 seal_open_time = pd.to_datetime(seal_open_times.min())

#                 if seal_open_time < seal_close_time:
#                     truck_issues.append({
#                         "truck_id": truck,
#                         "status": "INVALID_SEQUENCE",
#                         "remark": "Seal opened before sealing"
#                     })

#         except Exception:
#             pass

#         # ✅ Final decision per truck
#         if truck_issues:
#             results.extend(truck_issues)
#         else:
#             results.append({
#                 "truck_id": truck,
#                 "status": "OK",
#                 "remark": "Process followed correctly"
#             })

#     return {
#         "status": "success",
#         "governance": results
#     }

# from pathlib import Path
# import pandas as pd
# import pytesseract
# import cv2
# from langchain_core.tools import tool


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

#         # Improve OCR accuracy
#         gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

#         text = pytesseract.image_to_string(gray)

#         return text.upper()

#     except Exception:
#         return ""


# # =========================
# # GOVERNANCE TOOL
# # =========================
# @tool
# def check_governance():
#     """
#     Governance validation using OCR + metadata
#     """

#     base_path = Path(r"C:\Users\shash\OneDrive\Desktop\AI_data")
#     file_path = base_path / "image_data.csv"

#     try:
#         df = pd.read_csv(file_path)
#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     # 🔥 CLEAN COLUMN NAMES
#     df.columns = df.columns.str.strip().str.lower()

#     results = []

#     for _, row in df.iterrows():

#         truck_id = row.get("truck_id", "UNKNOWN")
#         stage = str(row.get("stage", "")).lower()
#         image_path = row.get("image_path", "")

#         # 🔥 OCR
#         text = extract_text(image_path)

#         # =========================
#         # VALIDATION LOGIC
#         # =========================

#         if stage == "box_scan":

#             expected_sn = str(row.get("expected_serial", "")).upper()

#             if not expected_sn:
#                 status = "NO_EXPECTED_SN ⚠️"
#                 remark = "Expected serial missing in data"

#             elif expected_sn not in text:
#                 status = "SERIAL_MISMATCH 🚨"
#                 remark = f"Expected {expected_sn} not found"

#             else:
#                 status = "OK ✅"
#                 remark = "Correct serial"

#         elif stage == "seal_close":

#             if "SEAL" not in text:
#                 status = "SEAL_MISSING 🚨"
#                 remark = "Seal not detected"
#             else:
#                 status = "OK ✅"
#                 remark = "Seal present"

#         elif stage == "seal_open":

#             if "OPEN" not in text:
#                 status = "NOT_OPENED 🚨"
#                 remark = "Seal not opened"
#             else:
#                 status = "OK ✅"
#                 remark = "Seal opened"

#         elif stage == "loading":

#             if "TRUCK" not in text:
#                 status = "NO_TRUCK 🚨"
#                 remark = "Truck not detected in loading"
#             else:
#                 status = "OK ✅"
#                 remark = "Truck loading verified"

#         elif stage == "warehouse_open":

#             if "OPEN" not in text:
#                 status = "NOT_OPENED 🚨"
#                 remark = "Warehouse not opened"
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


from pathlib import Path
import pandas as pd
import pytesseract
import cv2
import base64
import json
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# 🔥 Vision model (LangChain)
vision_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 🔥 Set tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# =========================
# OCR FUNCTION
# =========================
def extract_text(image_path: str):
    try:
        img = cv2.imread(image_path)

        if img is None:
            return ""

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]

        text = pytesseract.image_to_string(gray)

        return text.upper()

    except Exception:
        return ""


# =========================
# IMAGE → BASE64
# =========================
def encode_image(image_path):
    try:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


# =========================
# VISION FUNCTION
# =========================
def analyze_image(image_path, stage):
    base64_image = encode_image(image_path)

    if base64_image is None:
        return {"status": "ERROR", "reason": "Image not found"}

    prompt = f"""
    You are a supply chain audit AI.

    Analyze the image for stage: {stage}

    Rules:
    - loading → check if truck is present
    - seal_close → check if seal is visible
    - seal_open → check if seal is opened
    - box_scan → check if box and label visible
    - warehouse_open → check if warehouse is open

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

        content = response.content

        # 🔥 FIX JSON formatting issue
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}


# =========================
# GOVERNANCE TOOL
# =========================
@tool
def check_governance():
    """
    Governance validation using OCR + Vision AI
    """

    base_path = Path(r"C:\Users\shash\OneDrive\Desktop\AI_data")
    file_path = base_path / "image_data.csv"

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {"status": "failed", "message": str(e)}

    df.columns = df.columns.str.strip().str.lower()

    results = []

    for _, row in df.iterrows():

        truck_id = row.get("truck_id", "UNKNOWN")
        stage = str(row.get("stage", "")).lower()
        image_path = row.get("image_path", "")

        # 🔥 OCR
        text = extract_text(image_path)

        # 🔥 Vision
        vision_result = analyze_image(image_path, stage)

        vision_status = vision_result.get("status", "ERROR")
        vision_reason = vision_result.get("reason", "")

        # =========================
        # HYBRID VALIDATION LOGIC
        # =========================

        if stage == "box_scan":

            expected_sn = str(row.get("expected_serial", "")).upper()

            if not expected_sn:
                status = "NO_EXPECTED_SN ⚠️"
                remark = "Expected serial missing"

            elif expected_sn not in text:
                status = "SERIAL_MISMATCH 🚨"
                remark = f"OCR failed: {expected_sn} not found"

            elif vision_status == "ISSUE":
                status = "VISUAL_ISSUE 🚨"
                remark = vision_reason

            else:
                status = "OK ✅"
                remark = "Serial + box verified"

        elif stage == "loading":

            if vision_status == "ISSUE":
                status = "NO_TRUCK 🚨"
                remark = vision_reason
            else:
                status = "OK ✅"
                remark = "Truck detected"

        elif stage == "seal_close":

            if vision_status == "ISSUE" and "SEAL" not in text:
                status = "SEAL_MISSING 🚨"
                remark = "Seal not detected (OCR + Vision)"
            else:
                status = "OK ✅"
                remark = "Seal verified"

        elif stage == "seal_open":

            if vision_status == "ISSUE":
                status = "NOT_OPENED 🚨"
                remark = vision_reason
            else:
                status = "OK ✅"
                remark = "Seal opened"

        elif stage == "warehouse_open":

            if vision_status == "ISSUE":
                status = "NOT_OPENED 🚨"
                remark = vision_reason
            else:
                status = "OK ✅"
                remark = "Warehouse opened"

        else:
            status = "UNKNOWN ⚠️"
            remark = f"Stage '{stage}' not configured"

        results.append({
            "truck_id": truck_id,
            "stage": stage,
            "status": status,
            "remark": remark
        })

    return {
        "status": "success",
        "governance": results[:25]
    }