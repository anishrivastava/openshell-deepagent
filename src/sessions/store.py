# # =========================
# # 🔥 GLOBAL SESSION STORE
# # =========================
# SESSIONS = {
#     "truck_chat": {
#         "data": {},
#         "last_output": [],
#         "history": []
#     },

#     "utilization_chat": {
#         "data": {},
#         "last_output": [],
#         "history": []
#     },

#     "adherence_chat": {
#         "data": {},
#         "last_output": [],
#         "history": []
#     },

#     "reconciliation_chat": {
#         "data": {},
#         "last_output": [],
#         "history": []
#     },

#     "governance_chat": {
#         "data": {},
#         "last_output": [],
#         "history": []
#     }
# }


# # =========================
# # 🔥 GET SESSION
# # =========================
# def get_session(chat_name):

#     if chat_name not in SESSIONS:

#         SESSIONS[chat_name] = {
#             "data": {},
#             "last_output": [],
#             "history": []
#         }

#     return SESSIONS[chat_name]


# # =========================
# # 🔥 RESET SESSION
# # =========================
# def reset_session(chat_name):

#     SESSIONS[chat_name] = {
#         "data": {},
#         "last_output": [],
#         "history": []
#     }


# # =========================
# # 🔥 APPEND HISTORY
# # =========================
# def append_history(chat_name, output):

#     session = get_session(chat_name)

#     session["history"].append(output)
"""
sessions/store.py  —  Firestore-backed session store
Replaces the in-memory SESSIONS dict.
Drop-in replacement: same function signatures, same return shapes.
"""

from __future__ import annotations
import os
import logging
from google.cloud import firestore

logger = logging.getLogger(__name__)

# Firestore client (initialised once at import time)
# _db = firestore.Client(project=os.environ.get("GCP_PROJECT_ID"))
_db = None
_COLLECTION = "chat_sessions"

# ─── shape every session document follows ──────────────────────────────────────
_DEFAULT_SESSION = {
    "data": {},
    "last_output": [],
    "history": []
}

# ─── valid session names (same as before) ──────────────────────────────────────
KNOWN_SESSIONS = [
    "truck_chat",
    "utilization_chat",
    "adherence_chat",
    "reconciliation_chat",
    "governance_chat",
]


# ==============================================================================
# GET SESSION
# ==============================================================================
def get_session(chat_name: str) -> dict:
    global _db
    if _db is None:
        _db = firestore.Client(project=os.environ.get("GCP_PROJECT_ID"))

    try:
        doc_ref = _db.collection(_COLLECTION).document(chat_name)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()

        _db.collection(_COLLECTION).document(chat_name).set(_DEFAULT_SESSION)
        return dict(_DEFAULT_SESSION)

    except Exception as e:
        logger.error(f"[store] get_session failed for '{chat_name}': {e}")
        return dict(_DEFAULT_SESSION)


# ==============================================================================
# SAVE SESSION  (call this after you mutate the session dict)
# ==============================================================================
def save_session(chat_name: str, session: dict) -> None:
    """
    Write the full session dict back to Firestore.
    Call this any time you change session["data"], session["last_output"],
    or session["history"].
    """
    try:
        _db.collection(_COLLECTION).document(chat_name).set(session)
    except Exception as e:
        logger.error(f"[store] save_session failed for '{chat_name}': {e}")


# ==============================================================================
# RESET SESSION
# ==============================================================================
def reset_session(chat_name: str) -> None:
    """
    Wipe a session back to its default empty state in Firestore.
    """
    try:
        _db.collection(_COLLECTION).document(chat_name).set(_DEFAULT_SESSION)
    except Exception as e:
        logger.error(f"[store] reset_session failed for '{chat_name}': {e}")


# ==============================================================================
# APPEND HISTORY
# ==============================================================================
def append_history(chat_name: str, output: dict | str) -> None:
    """
    Append one message to history and persist immediately.
    'output' should be a dict like:
        { "role": "user" | "assistant", "content": "..." }
    Keeps the last 50 messages to avoid Firestore document size limits.
    """
    try:
        session = get_session(chat_name)
        session["history"].append(output)

        # Cap history to last 50 messages (Firestore doc limit is 1 MB)
        if len(session["history"]) > 50:
            session["history"] = session["history"][-50:]

        save_session(chat_name, session)
    except Exception as e:
        logger.error(f"[store] append_history failed for '{chat_name}': {e}")


# ==============================================================================
# UPDATE SESSION DATA  (helper — updates session["data"] and persists)
# ==============================================================================
def update_session_data(chat_name: str, data: dict) -> None:
    """
    Merge new keys into session["data"] and save.
    Useful for storing uploaded file URIs, plan state, etc.
    """
    try:
        session = get_session(chat_name)
        session["data"].update(data)
        save_session(chat_name, session)
    except Exception as e:
        logger.error(f"[store] update_session_data failed for '{chat_name}': {e}")