"""
sensor_client.py — runs on the Raspberry Pi
Reads LM393 soil moisture sensor every 60 seconds and POSTs to the API.
"""
import time
import requests
from datetime import datetime, timezone

# --- Config ---
SENSOR_PIN  = 17
SENSOR_ID   = "plant-001"
LOCATION    = "kitchen"
API_URL     = "http://YOUR_SERVER_IP:8000/api/v1/readings"
API_KEY     = "change-me-to-something-secret"
INTERVAL    = 60

print(f"Plant monitor started. Posting every {INTERVAL}s")

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN)
    USE_GPIO = True
except ImportError:
    print("RPi.GPIO not found - running in simulation mode")
    USE_GPIO = False

import random

try:
    while True:
        if USE_GPIO:
            raw = GPIO.input(SENSOR_PIN)
        else:
            raw = random.choice([0, 1])  # simulate on Mac

        status = "dry" if raw == 1 else "wet"
        payload = {
            "sensor_id": SENSOR_ID,
            "moisture":  raw,
            "status":    status,
            "location":  LOCATION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            resp = requests.post(
                API_URL,
                json=payload,
                headers={"X-API-Key": API_KEY},
                timeout=10,
            )
            print(f"{payload['timestamp']}  moisture={raw}  status={status}  HTTP {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send: {e}")

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nStopped.")
    if USE_GPIO:
        GPIO.cleanup()