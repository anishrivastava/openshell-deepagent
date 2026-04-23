# from pathlib import Path
# import pandas as pd
# from langchain_core.tools import tool
# from src.tools.finance.invoice_parser import process_invoice


# @tool
# def run_reconciliation():
#     """
#     Reconcile PO, Dispatch, and Invoice data using:
#     - PO CSV
#     - Dispatch CSV
#     - Invoice PDFs (OCR + 6LLM)
#     """

#     # =========================
#     # PATHS
#     # =========================
#     base_path = Path(r"C:\Users\shash\OneDrive\Desktop\AI_data")

#     po_file = base_path / "PO_FINAL_DATA.csv"
#     dispatch_file = base_path / "DISPATCH_FINAL_DATA.csv"

#     invoice_folder = Path("data/invoices")

#     try:
#         po_df = pd.read_csv(po_file)
#         dispatch_df = pd.read_csv(dispatch_file)
#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     # =========================
#     # LOAD INVOICE FROM PDFs 🔥
#     # =========================
#     invoice_data = []

#     for pdf in invoice_folder.glob("*.pdf"):
#         parsed = process_invoice(str(pdf))
#         if parsed:
#             invoice_data.append(parsed)

#     if not invoice_data:
#         return {"status": "failed", "message": "No invoice data extracted"}

#     invoice_df = pd.DataFrame(invoice_data)

#     # =========================
#     # CLEAN DATA (IMPORTANT)
#     # =========================
#     po_df.columns = po_df.columns.str.lower().str.strip()
#     dispatch_df.columns = dispatch_df.columns.str.lower().str.strip()
#     invoice_df.columns = invoice_df.columns.str.lower().str.strip()

#     results = []

#     # =========================
#     # MAIN LOOP
#     # =========================
#     for _, inv in invoice_df.iterrows():

#         invoice_id = inv.get("invoice_id", "UNKNOWN")
#         truck_id = str(inv.get("truck_id", "")).lower()
#         po_id = str(inv.get("po_id", "")).upper()
#         billed_trips = int(inv.get("billed_trips", 0))
#         billed_amount = float(inv.get("billed_amount", 0))

#         # 🔹 Find PO
#         po_row = po_df[po_df["po_id"].str.upper() == po_id]

#         if po_row.empty:
#             results.append({
#                 "invoice_id": invoice_id,
#                 "status": "INVALID_PO 🚨",
#                 "remark": "PO not found"
#             })
#             continue

#         rate = float(po_row.iloc[0]["rate_per_km"])

#         # 🔹 Find Dispatch (fuzzy match 🔥)
#         dispatch_row = dispatch_df[
#             dispatch_df["truck_id"].str.lower().str.contains(truck_id[:8], na=False)
#         ]

#         if dispatch_row.empty:
#             results.append({
#                 "invoice_id": invoice_id,
#                 "status": "FAKE_TRUCK 🚨",
#                 "remark": "No dispatch record"
#             })
#             continue

#         actual_trips = int(dispatch_row.iloc[0]["trips"])
#         distance = float(dispatch_row.iloc[0]["distance_km"])

#         expected_amount = distance * rate

#         # =========================
#         # CHECKS 🔥
#         # =========================
#         if billed_trips > actual_trips:
#             status = "EXTRA_TRIPS 🚨"
#             remark = "Billed more trips than actual"

#         elif billed_amount > expected_amount:
#             status = "OVERBILLING 🚨"
#             remark = f"Expected {expected_amount}, got {billed_amount}"

#         else:
#             status = "OK ✅"
#             remark = "Invoice correct"

#         results.append({
#             "invoice_id": invoice_id,
#             "status": status,
#             "remark": remark
#         })

#     # =========================
#     # MISSING INVOICE CHECK
#     # =========================
#     dispatch_trucks = set(dispatch_df["truck_id"].str.lower())
#     invoice_trucks = set(invoice_df["truck_id"].str.lower())

#     missing = dispatch_trucks - invoice_trucks

#     for truck in missing:
#         results.append({
#             "invoice_id": f"NA_{truck}",
#             "status": "MISSING_INVOICE 🚨",
#             "remark": "Dispatch done but no invoice"
#         })

#     return {
#         "status": "success",
#         "reconciliation": results
#     }


# import pandas as pd
# from langchain_core.tools import tool
# from src.tools.finance.invoice_parser import process_invoice


# @tool
# def run_reconciliation(data: dict):
#     """
#     Reconcile PO, Dispatch, and Invoice data using:
#     - PO CSV (from API)
#     - Dispatch CSV (from API)
#     - Invoice PDFs (from API)
#     """

#     # =========================
#     # VALIDATION
#     # =========================
#     if not data:
#         return {"status": "failed", "message": "No input data received"}

#     po_data = data.get("po")
#     dispatch_data = data.get("dispatch")
#     invoices = data.get("invoices", [])

#     if not po_data or not dispatch_data:
#         return {"status": "failed", "message": "Missing PO or Dispatch data"}

#     # =========================
#     # LOAD DATAFRAMES
#     # =========================
#     try:
#         po_df = pd.DataFrame(po_data)
#         dispatch_df = pd.DataFrame(dispatch_data)
#     except Exception as e:
#         return {"status": "failed", "message": str(e)}

#     # =========================
#     # PROCESS INVOICE PDFs 🔥
#     # =========================
#     invoice_data = []

#     for pdf in invoices:
#         try:
#             parsed = process_invoice(pdf["content"])   # 🔥 IMPORTANT
#             if parsed:
#                 invoice_data.append(parsed)
#         except Exception as e:
#             print(f"Error processing invoice: {e}")

#     if not invoice_data:
#         return {"status": "failed", "message": "No invoice data extracted"}

#     invoice_df = pd.DataFrame(invoice_data)

#     # =========================
#     # CLEAN DATA
#     # =========================
#     po_df.columns = po_df.columns.str.lower().str.strip()
#     dispatch_df.columns = dispatch_df.columns.str.lower().str.strip()
#     invoice_df.columns = invoice_df.columns.str.lower().str.strip()

#     results = []

#     # =========================
#     # MAIN LOOP
#     # =========================
#     for _, inv in invoice_df.iterrows():

#         invoice_id = inv.get("invoice_id", "UNKNOWN")
#         truck_id = str(inv.get("truck_id", "")).lower()
#         po_id = str(inv.get("po_id", "")).upper()
#         billed_trips = int(inv.get("billed_trips", 0))
#         billed_amount = float(inv.get("billed_amount", 0))

#         # 🔹 Find PO
#         po_row = po_df[po_df["po_id"].str.upper() == po_id]

#         if po_row.empty:
#             results.append({
#                 "invoice_id": invoice_id,
#                 "status": "INVALID_PO 🚨",
#                 "remark": "PO not found"
#             })
#             continue

#         rate = float(po_row.iloc[0]["rate_per_km"])

#         # 🔹 Find Dispatch
#         dispatch_row = dispatch_df[
#             dispatch_df["truck_id"].str.lower().str.contains(truck_id[:8], na=False)
#         ]

#         if dispatch_row.empty:
#             results.append({
#                 "invoice_id": invoice_id,
#                 "status": "FAKE_TRUCK 🚨",
#                 "remark": "No dispatch record"
#             })
#             continue

#         actual_trips = int(dispatch_row.iloc[0]["trips"])
#         distance = float(dispatch_row.iloc[0]["distance_km"])

#         expected_amount = distance * rate

#         # =========================
#         # CHECKS 🔥
#         # =========================
#         if billed_trips > actual_trips:
#             status = "EXTRA_TRIPS 🚨"
#             remark = "Billed more trips than actual"

#         elif billed_amount > expected_amount:
#             status = "OVERBILLING 🚨"
#             remark = f"Expected {expected_amount}, got {billed_amount}"

#         else:
#             status = "OK ✅"
#             remark = "Invoice correct"

#         results.append({
#             "invoice_id": invoice_id,
#             "status": status,
#             "remark": remark
#         })

#     # =========================
#     # MISSING INVOICE CHECK
#     # =========================
#     dispatch_trucks = set(dispatch_df["truck_id"].str.lower())
#     invoice_trucks = set(invoice_df["truck_id"].str.lower())

#     missing = dispatch_trucks - invoice_trucks

#     for truck in missing:
#         results.append({
#             "invoice_id": f"NA_{truck}",
#             "status": "MISSING_INVOICE 🚨",
#             "remark": "Dispatch done but no invoice"
#         })

#     return {
#         "status": "success",
#         "reconciliation": results
#     }

import pandas as pd
from langchain_core.tools import tool
from tools.finance.invoice_parser import process_invoice


@tool
def run_reconciliation(data: dict, invoice: bytes):
    """
    Reconcile PO, Dispatch, and Invoice data

    Inputs:
    - PO CSV (data["po"])
    - Dispatch CSV (data["dispatch"])
    - Invoice PDF (single file)
    """

    # =========================
    # VALIDATION
    # =========================
    if not data:
        return {"status": "failed", "message": "No input data"}

    po_data = data.get("po")
    dispatch_data = data.get("dispatch")

    if not po_data or not dispatch_data:
        return {"status": "failed", "message": "Missing PO or Dispatch"}

    if not invoice:
        return {"status": "failed", "message": "No invoice PDF provided"}

    # =========================
    # DATAFRAMES
    # =========================
    po_df = pd.DataFrame(po_data)
    dispatch_df = pd.DataFrame(dispatch_data)

    po_df.columns = po_df.columns.str.lower().str.strip()
    dispatch_df.columns = dispatch_df.columns.str.lower().str.strip()

    # =========================
    # PROCESS INVOICE PDF 🔥
    # =========================
    parsed = process_invoice(invoice)

    if not parsed:
        return {"status": "failed", "message": "Invoice parsing failed"}

    invoice_df = pd.DataFrame([parsed])
    invoice_df.columns = invoice_df.columns.str.lower().str.strip()

    results = []

    # =========================
    # MAIN LOGIC
    # =========================
    for _, inv in invoice_df.iterrows():

        invoice_id = inv.get("invoice_id", "UNKNOWN")
        truck_id = str(inv.get("truck_id", "")).lower()
        po_id = str(inv.get("po_id", "")).upper()
        billed_trips = int(inv.get("billed_trips", 0))
        billed_amount = float(inv.get("billed_amount", 0))

        # 🔹 PO CHECK
        po_row = po_df[po_df["po_id"].str.upper() == po_id]

        if po_row.empty:
            results.append({
                "invoice_id": invoice_id,
                "status": "INVALID_PO ",
                "remark": "PO not found"
            })
            continue

        rate = float(po_row.iloc[0]["rate_per_km"])

        # 🔹 DISPATCH CHECK
        dispatch_row = dispatch_df[
            dispatch_df["truck_id"].str.lower().str.contains(truck_id[:6], na=False)
        ]

        if dispatch_row.empty:
            results.append({
                "invoice_id": invoice_id,
                "status": "FAKE_TRUCK ",
                "remark": "No dispatch record"
            })
            continue

        actual_trips = int(dispatch_row.iloc[0]["trips"])
        distance = float(dispatch_row.iloc[0]["distance_km"])

        expected_amount = distance * rate

        # =========================
        # VALIDATION
        # =========================
        if billed_trips > actual_trips:
            status = "EXTRA_TRIPS "
            remark = "More trips billed"

        elif billed_amount > expected_amount:
            status = "OVERBILLING "
            remark = f"Expected {expected_amount}, got {billed_amount}"

        else:
            status = "OK "
            remark = "Invoice correct"

        results.append({
            "invoice_id": invoice_id,
            "status": status,
            "remark": remark
        })

    return {
        "status": "success",
        "reconciliation": results
    }