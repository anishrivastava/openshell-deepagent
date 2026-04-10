from pathlib import Path
import pandas as pd
from langchain_core.tools import tool


@tool
def get_underutilized_plants():
    """
    Read the latest planning output Excel file and return the most underutilized plants.
    """

    outputs_dir = Path(r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT\outputs")

    files = list(outputs_dir.glob("fsd_planning_output_*.xlsx"))
    if not files:
        return {"status": "failed", "message": "No planning output files found."}

    latest_file = max(files, key=lambda x: x.stat().st_mtime)

    possible_sheets = ["capacity_utilization", "capacity utilisation", "utilization", "capacity"]
    df = None
    sheet_used = None

    for sheet in possible_sheets:
        try:
            df = pd.read_excel(latest_file, sheet_name=sheet)
            sheet_used = sheet
            break
        except Exception:
            continue

    if df is None:
        return {
            "status": "failed",
            "message": "Could not find capacity utilization sheet in latest output file."
        }

    plant_col = None
    for col in ["plant", "plant_code", "source"]:
        if col in df.columns:
            plant_col = col
            break

    util_col = None
    for col in ["utilization_%", "utilization", "utilisation_%", "utilisation"]:
        if col in df.columns:
            util_col = col
            break

    if plant_col is None or util_col is None:
        return {
            "status": "failed",
            "message": f"Required columns not found. Available columns: {list(df.columns)}"
        }

    cleaned = df[[plant_col, util_col]].copy()
    cleaned = cleaned.dropna()
    cleaned[util_col] = pd.to_numeric(cleaned[util_col], errors="coerce")
    cleaned = cleaned.dropna(subset=[util_col])

    underutilized = (
        cleaned.sort_values(util_col, ascending=True)
        .head(5)
        .reset_index(drop=True)
    )

    return {
        "status": "success",
        "file_used": str(latest_file),
        "sheet_used": sheet_used,
        "plant_column": plant_col,
        "utilization_column": util_col,
        "underutilized_plants": underutilized.to_dict(orient="records")
    }