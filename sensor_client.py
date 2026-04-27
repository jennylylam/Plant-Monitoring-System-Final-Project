"""
sensor_client.py — runs on the Raspberry Pi
Reads LM393 soil moisture sensor every 30 seconds and POSTs to the API.
"""

import time
import requests
from datetime import datetime, timezone

# --- Config ---
SENSOR_PIN = 21
SENSOR_ID = "plant-001"
LOCATION = "kitchen"
API_URL = "http://172.20.10.10:8000/api/v1/readings"
API_KEY = "change-me-to-something-secret"
INTERVAL = 30

print(f"Plant monitor started. Posting every {INTERVAL}s")

# --- GPIO setup ---
try:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)
    USE_GPIO = True

except ImportError:
    print("ERROR: RPi.GPIO not found. Run this on the Raspberry Pi.")
    USE_GPIO = False
    exit()

# --- Main loop ---
try:
    while True:

        # Read sensor
        raw = GPIO.input(SENSOR_PIN)

        # DEBUG: show raw sensor value
        print("RAW:", raw)

        # Convert to status (may flip depending on calibration)
        status = "dry" if raw == 1 else "wet"

        # Build payload
        payload = {
            "sensor_id": SENSOR_ID,
            "moisture": raw,
            "status": status,
            "location": LOCATION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Send to server
        try:
            resp = requests.post(
                API_URL,
                json=payload,
                headers={"X-API-Key": API_KEY},
                timeout=10,
            )

            print(
                f"{payload['timestamp']}  "
                f"moisture={raw}  status={status}  HTTP {resp.status_code}"
            )

        except requests.exceptions.RequestException as e:
            print("Failed to send:", e)

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nStopped.")
    GPIO.cleanup()
