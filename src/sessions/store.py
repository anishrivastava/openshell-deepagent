# =========================
# 🔥 GLOBAL SESSION STORE
# =========================
SESSIONS = {
    "truck_chat": {
        "data": {},
        "last_output": [],
        "history": []
    },

    "utilization_chat": {
        "data": {},
        "last_output": [],
        "history": []
    },

    "adherence_chat": {
        "data": {},
        "last_output": [],
        "history": []
    },

    "reconciliation_chat": {
        "data": {},
        "last_output": [],
        "history": []
    },

    "governance_chat": {
        "data": {},
        "last_output": [],
        "history": []
    }
}


# =========================
# 🔥 GET SESSION
# =========================
def get_session(chat_name):

    if chat_name not in SESSIONS:

        SESSIONS[chat_name] = {
            "data": {},
            "last_output": [],
            "history": []
        }

    return SESSIONS[chat_name]


# =========================
# 🔥 RESET SESSION
# =========================
def reset_session(chat_name):

    SESSIONS[chat_name] = {
        "data": {},
        "last_output": [],
        "history": []
    }


# =========================
# 🔥 APPEND HISTORY
# =========================
def append_history(chat_name, output):

    session = get_session(chat_name)

    session["history"].append(output)