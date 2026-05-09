"""
utils/file_handler.py  —  Cloud Storage upload + file text extraction
NEW FILE — did not exist before.

Handles:
  - Uploading report files (PDF, Excel, CSV) to GCS
  - Extracting text from uploaded files to pass as context to the LLM
  - Storing the GCS URI in the session so agents can reference it
"""

from __future__ import annotations
import os
import io
import logging
from typing import Optional

from google.cloud import storage

logger = logging.getLogger(__name__)

# ─── GCS config ─────────────────────────────────────────────────────────────────
GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME", "your-bucket-name")
# _storage_client = storage.Client(project=os.environ.get("GCP_PROJECT_ID"))
_storage_client = None


# ==============================================================================
# UPLOAD FILE TO GCS
# ==============================================================================
def upload_report(
    file_bytes: bytes,
    filename: str,
    chat_name: str,
) -> str:
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=os.environ.get("GCP_PROJECT_ID"))

    try:
        bucket = _storage_client.bucket(GCS_BUCKET)
        blob_path = f"reports/{chat_name}/{filename}"
        blob = bucket.blob(blob_path)

        blob.upload_from_string(file_bytes, content_type=_guess_mime(filename))

        gcs_uri = f"gs://{GCS_BUCKET}/{blob_path}"
        logger.info(f"[file_handler] Uploaded {filename} → {gcs_uri}")
        return gcs_uri

    except Exception as e:
        logger.error(f"[file_handler] upload_report failed: {e}")
        raise


# ==============================================================================
# EXTRACT TEXT FROM FILE  (for LLM context)
# ==============================================================================
def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Extract readable text from an uploaded file.
    Supports: .csv, .txt, .pdf, .xlsx

    Returns plain text string (max ~4000 chars) to pass as file_context
    to generate_chat_response().
    """
    ext = filename.lower().rsplit(".", 1)[-1]

    try:
        if ext in ("csv", "txt"):
            return _extract_csv_txt(file_bytes)

        elif ext == "pdf":
            return _extract_pdf(file_bytes)

        elif ext in ("xlsx", "xls"):
            return _extract_excel(file_bytes)

        else:
            return f"[File uploaded: {filename} — text extraction not supported for .{ext}]"

    except Exception as e:
        logger.error(f"[file_handler] extract_text failed for {filename}: {e}")
        return f"[Could not extract text from {filename}: {str(e)}]"


# ==============================================================================
# PRIVATE HELPERS
# ==============================================================================
def _extract_csv_txt(file_bytes: bytes) -> str:
    text = file_bytes.decode("utf-8", errors="replace")
    return text[:4000]


def _extract_pdf(file_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages[:10]]
        return "\n".join(pages)[:4000]
    except ImportError:
        return "[PDF extraction requires pypdf — add it to requirements.txt]"


def _extract_excel(file_bytes: bytes) -> str:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        lines = []
        for sheet in wb.worksheets[:2]:           # first 2 sheets
            lines.append(f"Sheet: {sheet.title}")
            for row in sheet.iter_rows(max_row=50, values_only=True):
                lines.append("\t".join(str(c) if c is not None else "" for c in row))
        return "\n".join(lines)[:4000]
    except ImportError:
        return "[Excel extraction requires openpyxl — add it to requirements.txt]"


def _guess_mime(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    return {
        "pdf":  "application/pdf",
        "csv":  "text/csv",
        "txt":  "text/plain",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xls":  "application/vnd.ms-excel",
    }.get(ext, "application/octet-stream")