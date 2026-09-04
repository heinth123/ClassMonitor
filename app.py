from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)

# =========================================================
# CLASS ROSTER & MAPPINGS (25 STUDENTS)
# =========================================================

STUDENT_MAP = {
    # Short Initials
    "AHO": "Aung Htet Oo",
    "AMM": "Aung Myint Myat",
    "APK": "Aung Phyo Khant",
    "BMK": "Bhone Myat Kaung",
    "ECK": "Eaint Chue Khaing",
    "HHM": "Hein Htet Myint",
    "HTAZ": "Hein Thant Aye Zaw",
    "HMT": "Hmue Myat Thakhin",
    "HHN": "Htet Htet Naing",
    "KHK": "Kaung Htet Kyaw",
    "KKMN": "Kaung Khant Myo Nyunt",
    "KSO": "Kaung Satt Oo",
    "KTZ": "Kaung Thiha Zaw",
    "MTCM": "May Thu Chan Myae",
    "MMK": "Myat Min Khant",
    "PMK": "Phone Myat Kyaw",
    "PHK": "Pyae Hmue Khin",
    "PTK": "Pyae Thadar Khin",
    "SNL": "Saw Noel Linn",
    "SHP": "Shine Htet Paing",
    "TBT": "Thant Bhone Tayza",
    "TS": "Thant Sin",
    "TYT": "Thoon Yati Thant",
    "WMH": "Wint Maw Htun",
    "ZMH": "Zwe Myat Htut",

    # ID Numbers (01 - 25)
    "01": "Aung Htet Oo",
    "02": "Aung Myint Myat",
    "03": "Aung Phyo Khant",
    "04": "Bhone Myat Kaung",
    "05": "Eaint Chue Khaing",
    "06": "Hein Htet Myint",
    "07": "Hein Thant Aye Zaw",
    "08": "Hmue Myat Thakhin",
    "09": "Htet Htet Naing",
    "10": "Kaung Htet Kyaw",
    "11": "Kaung Khant Myo Nyunt",
    "12": "Kaung Satt Oo",
    "13": "Kaung Thiha Zaw",
    "14": "May Thu Chan Myae",
    "15": "Myat Min Khant",
    "16": "Phone Myat Kyaw",
    "17": "Pyae Hmue Khin",
    "18": "Pyae Thadar Khin",
    "19": "Saw Noel Linn",
    "20": "Shine Htet Paing",
    "21": "Thant Bhone Tayza",
    "22": "Thant Sin",
    "23": "Thoon Yati Thant",
    "24": "Wint Maw Htun",
    "25": "Zwe Myat Htut",

    # Full ID Codes
    "P6 DO 0626-01": "Aung Htet Oo",
    "P6 DO 0626-02": "Aung Myint Myat",
    "P6 DO 0626-03": "Aung Phyo Khant",
    "P6 DO 0626-04": "Bhone Myat Kaung",
    "P6 DO 0626-05": "Eaint Chue Khaing",
    "P6 DO 0626-06": "Hein Htet Myint",
    "P6 DO 0626-07": "Hein Thant Aye Zaw",
    "P6 DO 0626-08": "Hmue Myat Thakhin",
    "P6 DO 0626-09": "Htet Htet Naing",
    "P6 DO 0626-10": "Kaung Htet Kyaw",
    "P6 DO 0626-11": "Kaung Khant Myo Nyunt",
    "P6 DO 0626-12": "Kaung Satt Oo",
    "P6 DO 0626-13": "Kaung Thiha Zaw",
    "P6 DO 0626-14": "May Thu Chan Myae",
    "P6 DO 0626-15": "Myat Min Khant",
    "P6 DO 0626-16": "Phone Myat Kyaw",
    "P6 DO 0626-17": "Pyae Hmue Khin",
    "P6 DO 0626-18": "Pyae Thadar Khin",
    "P6 DO 0626-19": "Saw Noel Linn",
    "P6 DO 0626-20": "Shine Htet Paing",
    "P6 DO 0626-21": "Thant Bhone Tayza",
    "P6 DO 0626-22": "Thant Sin",
    "P6 DO 0626-23": "Thoon Yati Thant",
    "P6 DO 0626-24": "Wint Maw Htun",
    "P6 DO 0626-25": "Zwe Myat Htut"
}


# Helper function to convert input (like AHO or 01) to full name
def resolve_student_name(input_str):
    clean_input = input_str.strip().upper()
    # Check if input is in our map, otherwise use what was typed
    return STUDENT_MAP.get(clean_input, input_str.strip())


# =========================================================
# EVENT STORAGE
# =========================================================

DATA_FILE = "events.json"


# =========================================================
# LOAD EVENTS FROM FILE
# =========================================================

def load_events():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


# =========================================================
# SAVE EVENTS TO FILE
# =========================================================

def save_events():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(
                events,
                file,
                indent=4,
                ensure_ascii=False
            )
    except OSError as error:
        print(f"Could not save events: {error}")


# =========================================================
# EVENTS
# =========================================================

events = load_events()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# =========================================================
# GET ALL EVENTS
# =========================================================

@app.route("/events", methods=["GET"])
def get_events():
    return jsonify(events)


# =========================================================
# ADD EVENT
# =========================================================

@app.route("/event", methods=["POST"])
def add_event():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No JSON data received"
        }), 400

    raw_name = str(data.get("name", "")).strip()
    event_name = str(data.get("event", "")).strip()

    if not raw_name:
        return jsonify({
            "success": False,
            "message": "Student name/shortcut is required"
        }), 400

    if not event_name:
        return jsonify({
            "success": False,
            "message": "Event is required"
        }), 400

    # Translate AHO -> Aung Htet Oo
    resolved_name = resolve_student_name(raw_name)
    event_name = event_name.upper()

    new_event = {
        "id": str(uuid.uuid4()),
        "name": resolved_name,
        "event": event_name,
        "time": datetime.now().isoformat()
    }

    events.append(new_event)
    save_events()

    return jsonify({
        "success": True,
        "message": "Event added",
        "event": new_event
    }), 201


# =========================================================
# TEST EVENT
# =========================================================

@app.route("/add/<name>/<event_name>", methods=["GET"])
def add_test_event(name, event_name):
    resolved_name = resolve_student_name(name)
    
    new_event = {
        "id": str(uuid.uuid4()),
        "name": resolved_name,
        "event": event_name.strip().upper(),
        "time": datetime.now().isoformat()
    }

    events.append(new_event)
    save_events()

    return jsonify({
        "success": True,
        "message": "Test event added",
        "event": new_event
    })


# =========================================================
# DELETE ONE EVENT
# =========================================================

@app.route("/delete-event", methods=["POST"])
def delete_event():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No JSON data received"
        }), 400

    event_id = str(data.get("id", "")).strip()

    if not event_id:
        return jsonify({
            "success": False,
            "message": "Event ID is required"
        }), 400

    global events
    old_count = len(events)
    events = [event for event in events if str(event.get("id")) != event_id]
    deleted = len(events) < old_count

    if deleted:
        save_events()

    return jsonify({
        "success": deleted,
        "deleted": deleted
    })


# =========================================================
# CLEAR ALL EVENTS
# =========================================================

@app.route("/clear-events", methods=["POST"])
def clear_events():
    global events
    events = []
    save_events()

    return jsonify({
        "success": True,
        "message": "All events cleared"
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "online": True,
        "events": len(events),
        "time": datetime.now().isoformat()
    })


# =========================================================
# ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({
        "success": False,
        "message": "Page not found"
    }), 404


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
