import os
import requests

# =========================================================
# SETTINGS
# Replace 'your-app-name.onrender.com' with your actual Render URL!
# =========================================================

RENDER_URL = os.environ.get("RENDER_URL", "https://your-app-name.onrender.com")
SERVER_URL = f"{RENDER_URL.rstrip('/')}/event"


# =========================================================
# EVENT SHORTCUTS
# =========================================================

EVENTS = {
    "JOINED": "JOINED",
    "JOIN": "JOINED",
    "LEFT": "LEFT",
    "CAM ON": "CAMERA ON",
    "CAMERA ON": "CAMERA ON",
    "CAM OFF": "CAMERA OFF",
    "CAMERA OFF": "CAMERA OFF",
    "MIC ON": "MIC ON",
    "MIC OFF": "MIC OFF",
    "WAITING": "WAITING"
}


# =========================================================
# SEND EVENT
# =========================================================

def send_event(name, event):
    try:
        response = requests.post(
            SERVER_URL,
            json={
                "name": name,
                "event": event
            },
            timeout=5
        )

        if response.ok:
            print(f"✓ {name} → {event}")
        else:
            print(f"✗ Server error: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("⏳ Waiting for server connection...")
    except requests.exceptions.Timeout:
        print("⏳ Request timed out (Server might be waking up)...")
    except Exception as error:
        print(f"✗ Error: {error}")


# =========================================================
# INPUT
# =========================================================

print()
print("==============================================")
print("          P6D CLASS MONITOR CLI")
print("==============================================")
print(f" Target Server: {SERVER_URL}")
print("==============================================")
print()
print("Type example:")
print("  SHP,JOIN")
print("  SHP,CAM ON")
print("  SHP,CAM OFF")
print("  SHP,MIC ON")
print("  SHP,MIC OFF")
print("  SHP,LEFT")
print()
print("Shortcuts are NOT case-sensitive.")
print("Type EXIT to stop.")
print()
print("==============================================")
print()


while True:
    user_input = input("> ").strip()

    # EXIT
    if user_input.upper() == "EXIT":
        print("Monitor stopped.")
        break

    # CHECK FORMAT
    if "," not in user_input:
        print("✗ Use format: SHORTCUT,EVENT")
        continue

    # SPLIT
    name, event = user_input.split(",", 1)
    name = name.strip().upper()
    event = event.strip().upper()

    # CHECK EMPTY
    if not name or not event:
        print("✗ Use format: SHORTCUT,EVENT")
        continue

    # CONVERT EVENT SHORTCUT
    if event in EVENTS:
        event = EVENTS[event]
    else:
        print(f"✗ Unknown event: {event}")
        print("Available: JOIN, CAM ON, CAM OFF, MIC ON, MIC OFF, LEFT, WAITING")
        continue

    # SEND
    send_event(name, event)
