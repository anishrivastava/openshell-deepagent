# =========================
# 🔥 MODIFY OUTPUT
# =========================
def modify_output(data, query):

    if not isinstance(data, list):
        return data

    query = query.lower()

    filtered = data

    # =========================
    # 🚛 TRUCK TYPE FILTER
    # =========================

    # 🔥 ONLY 16MT
    if "16mt" in query:

        filtered = [
            row for row in filtered
            if str(row.get("truck_type", "")).upper() == "16MT"
        ]

    # 🔥 ONLY 9MT
    elif "9mt" in query:

        filtered = [
            row for row in filtered
            if str(row.get("truck_type", "")).upper() == "9MT"
        ]

    # =========================
    # 🏭 PLANT FILTER
    # =========================
    if "bangalore" in query:

        filtered = [
            row for row in filtered
            if "bangalore" in str(row.get("plant", "")).lower()
        ]

    # =========================
    # 📍 DESTINATION FILTER
    # =========================
    if "destination" in query:

        words = query.split()

        for word in words:

            if word.isdigit():

                filtered = [
                    row for row in filtered
                    if str(row.get("destination", "")) == word
                ]

    return filtered