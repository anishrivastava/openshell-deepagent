import pytesseract
import cv2
from pdf2image import convert_from_path
import numpy as np
import json
from langchain_openai import ChatOpenAI

import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

llm = ChatOpenAI(temperature=0)

# =========================
# PDF → IMAGE → OCR
# =========================
def extract_text_from_pdf(pdf_path):

    images = convert_from_path(
        pdf_path,
        poppler_path=r"C:\poppler\poppler-25.12.0\Library\bin"
    )

    full_text = ""

    for img in images:
        img = np.array(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        text = pytesseract.image_to_string(gray)
        full_text += text + "\n"

    return full_text


# =========================
# LLM → STRUCTURED DATA
# =========================
def parse_invoice(text):

    prompt = f"""
Extract invoice data VERY CAREFULLY.

Rules:
- Invoice ID starts with INV (not INVO)
- PO ID starts with PO
- Truck ID should be clean (remove spaces/symbols)
- billed_trips = value under "Billed Trips"
- DO NOT take GST total
- billed_amount = ONLY freight amount (before tax)

Return JSON:
{{
    "invoice_id": "",
    "po_id": "",
    "truck_id": "",
    "distance_km": number,
    "rate_per_km": number,
    "billed_trips": number,
    "billed_amount": number
}}

Invoice Text:
{text}
"""

    response = llm.invoke(prompt)

    content = response.content.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(content)
    except:
        return None
def clean_data(data):

    if not data:
        return data

    # 🔹 Fix invoice_id
    if "invoice_id" in data:
        inv = data["invoice_id"]

        # Ensure format INV001
        inv = inv.replace("O", "0")

        if len(inv) == 5:   # INV01 → INV001
            inv = inv[:3] + "0" + inv[3:]

        data["invoice_id"] = inv

    # 🔹 Fix PO
    if "po_id" in data:
        data["po_id"] = data["po_id"].upper()

    # 🔹 Clean truck id
    if "truck_id" in data:
        truck = data["truck_id"]

        # remove slash part
        if "/" in truck:
            truck = truck.split("/")[-1]

        # clean formatting
        truck = truck.replace(" ", "_").replace("-", "_")

        data["truck_id"] = truck

    return data
# =========================
# MAIN FUNCTION
# =========================
def process_invoice(pdf_path):

    text = extract_text_from_pdf(pdf_path)
    data = parse_invoice(text)

    return data