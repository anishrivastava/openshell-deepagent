from pathlib import Path
import pandas as pd
from langchain_core.tools import tool


@tool
def get_top_5_cities_by_dispatch():
    """
    Read the latest planning output Excel file and return top 5 cities by dispatched cases.
    Use this when the user asks for top cities by dispatch.
    """

    outputs_dir = Path(r"C:\Users\shash\OneDrive\Desktop\FSD AI AGENT\outputs")

    files = list(outputs_dir.glob("fsd_planning_output_*.xlsx"))
    if not files:
        return {"status": "failed", "message": "No planning output files found."}

    latest_file = max(files, key=lambda x: x.stat().st_mtime)

    try:
        df = pd.read_excel(latest_file, sheet_name="dispatch_plan")
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Could not read dispatch_plan sheet: {str(e)}"
        }

    expected_city_col = "city"

    # try to detect cases column
    possible_case_cols = ["cases", "total_cases", "supplied_cases", "demand_cases"]
    case_col = None
    for col in possible_case_cols:
        if col in df.columns:
            case_col = col
            break

    if expected_city_col not in df.columns or case_col is None:
        return {
            "status": "failed",
            "message": f"Required columns not found. Available columns: {list(df.columns)}"
        }

    top5 = (
        df.groupby(expected_city_col, as_index=False)[case_col]
        .sum()
        .sort_values(case_col, ascending=False)
        .head(5)
    )

    return {
        "status": "success",
        "file_used": str(latest_file),
        "metric_column": case_col,
        "top_5_cities": top5.to_dict(orient="records")
    }