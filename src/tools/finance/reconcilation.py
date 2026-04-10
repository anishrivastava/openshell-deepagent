from pathlib import Path
import pandas as pd
from langchain_core.tools import tool
from src.tools.finance.invoice_parser import process_invoice


@tool
def run_reconciliation():
    """
    Reconcile PO, Dispatch, and Invoice data using:
    - PO CSV
    - Dispatch CSV
    - Invoice PDFs (OCR + 6LLM)
    """

    # =========================
    # PATHS
    # =========================
    base_path = Path(r"C:\Users\shash\OneDrive\Desktop\AI_data")

    po_file = base_path / "PO_FINAL_DATA.csv"
    dispatch_file = base_path / "DISPATCH_FINAL_DATA.csv"

    invoice_folder = Path("data/invoices")

    try:
        po_df = pd.read_csv(po_file)
        dispatch_df = pd.read_csv(dispatch_file)
    except Exception as e:
        return {"status": "failed", "message": str(e)}

    # =========================
    # LOAD INVOICE FROM PDFs 🔥
    # =========================
    invoice_data = []

    for pdf in invoice_folder.glob("*.pdf"):
        parsed = process_invoice(str(pdf))
        if parsed:
            invoice_data.append(parsed)

    if not invoice_data:
        return {"status": "failed", "message": "No invoice data extracted"}

    invoice_df = pd.DataFrame(invoice_data)

    # =========================
    # CLEAN DATA (IMPORTANT)
    # =========================
    po_df.columns = po_df.columns.str.lower().str.strip()
    dispatch_df.columns = dispatch_df.columns.str.lower().str.strip()
    invoice_df.columns = invoice_df.columns.str.lower().str.strip()

    results = []

    # =========================
    # MAIN LOOP
    # =========================
    for _, inv in invoice_df.iterrows():

        invoice_id = inv.get("invoice_id", "UNKNOWN")
        truck_id = str(inv.get("truck_id", "")).lower()
        po_id = str(inv.get("po_id", "")).upper()
        billed_trips = int(inv.get("billed_trips", 0))
        billed_amount = float(inv.get("billed_amount", 0))

        # 🔹 Find PO
        po_row = po_df[po_df["po_id"].str.upper() == po_id]

        if po_row.empty:
            results.append({
                "invoice_id": invoice_id,
                "status": "INVALID_PO 🚨",
                "remark": "PO not found"
            })
            continue

        rate = float(po_row.iloc[0]["rate_per_km"])

        # 🔹 Find Dispatch (fuzzy match 🔥)
        dispatch_row = dispatch_df[
            dispatch_df["truck_id"].str.lower().str.contains(truck_id[:8], na=False)
        ]

        if dispatch_row.empty:
            results.append({
                "invoice_id": invoice_id,
                "status": "FAKE_TRUCK 🚨",
                "remark": "No dispatch record"
            })
            continue

        actual_trips = int(dispatch_row.iloc[0]["trips"])
        distance = float(dispatch_row.iloc[0]["distance_km"])

        expected_amount = distance * rate

        # =========================
        # CHECKS 🔥
        # =========================
        if billed_trips > actual_trips:
            status = "EXTRA_TRIPS 🚨"
            remark = "Billed more trips than actual"

        elif billed_amount > expected_amount:
            status = "OVERBILLING 🚨"
            remark = f"Expected {expected_amount}, got {billed_amount}"

        else:
            status = "OK ✅"
            remark = "Invoice correct"

        results.append({
            "invoice_id": invoice_id,
            "status": status,
            "remark": remark
        })

    # =========================
    # MISSING INVOICE CHECK
    # =========================
    dispatch_trucks = set(dispatch_df["truck_id"].str.lower())
    invoice_trucks = set(invoice_df["truck_id"].str.lower())

    missing = dispatch_trucks - invoice_trucks

    for truck in missing:
        results.append({
            "invoice_id": f"NA_{truck}",
            "status": "MISSING_INVOICE 🚨",
            "remark": "Dispatch done but no invoice"
        })

    return {
        "status": "success",
        "reconciliation": results
    }