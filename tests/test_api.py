from unittest.mock import MagicMock
from bson import ObjectId
from datetime import datetime, timezone


HEADERS = {"X-API-Key": "change-me-to-something-secret"}

def make_doc(sensor_id="plant-001", moisture=1, status="dry"):
    return {
        "_id": ObjectId(),
        "sensor_id": sensor_id,
        "moisture": moisture,
        "status": status,
        "timestamp": datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc),
        "location": "kitchen",
    }


# --- POST /readings ---

def test_create_reading_success(client, mock_db):
    mock_db.readings.insert_one.return_value = MagicMock(inserted_id=ObjectId())
    mock_db.sensors.update_one.return_value = None

    r = client.post("/api/v1/readings", json={
        "sensor_id": "plant-001", "moisture": 1, "status": "dry", "location": "kitchen"
    }, headers=HEADERS)

    assert r.status_code == 201
    assert r.json()["sensor_id"] == "plant-001"


def test_create_reading_no_token(client):
    r = client.post("/api/v1/readings", json={
        "sensor_id": "plant-001", "moisture": 1, "status": "dry"
    })
    assert r.status_code == 401


def test_create_reading_bad_token(client):
    r = client.post("/api/v1/readings", json={
        "sensor_id": "plant-001", "moisture": 1, "status": "dry"
    }, headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 401


def test_create_reading_validation_error(client):
    r = client.post("/api/v1/readings", json={
        "sensor_id": "plant-001", "moisture": 5, "status": "dry"
    }, headers=HEADERS)
    assert r.status_code == 422


def test_create_reading_missing_field(client):
    r = client.post("/api/v1/readings", json={
        "moisture": 1, "status": "dry"
    }, headers=HEADERS)
    assert r.status_code == 422


# --- GET /readings ---

def test_get_readings_empty(client, mock_db):
    mock_db.readings.count_documents.return_value = 0
    mock_db.readings.find.return_value.sort.return_value.skip.return_value.limit.return_value = []

    r = client.get("/api/v1/readings", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["readings"] == []


def test_get_readings_by_sensor(client, mock_db):
    docs = [make_doc("plant-001"), make_doc("plant-001")]
    mock_db.readings.count_documents.return_value = 2
    mock_db.readings.find.return_value.sort.return_value.skip.return_value.limit.return_value = docs

    r = client.get("/api/v1/readings?sensor_id=plant-001", headers=HEADERS)