from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)

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

    name = str(data.get("name", "")).strip()
    event_name = str(data.get("event", "")).strip()

    if not name:
        return jsonify({
            "success": False,
            "message": "Student name/shortcut is required"
        }), 400

    if not event_name:
        return jsonify({
            "success": False,
            "message": "Event is required"
        }), 400

    event_name = event_name.upper()

    new_event = {
        "id": str(uuid.uuid4()),
        "name": name,
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
    new_event = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
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
