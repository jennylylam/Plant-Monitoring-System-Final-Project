import pytest
from pydantic import ValidationError
from app.models import PlantReadingCreate


def valid_base():
    return {"sensor_id": "plant-001", "moisture": 0, "status": "wet"}


# --- Valid inputs ---

def test_valid_reading_minimal():
    r = PlantReadingCreate(**valid_base())
    assert r.sensor_id == "plant-001"


def test_valid_reading_full():
    r = PlantReadingCreate(**valid_base(), timestamp="2024-03-15T10:00:00Z", location="kitchen")
    assert r.location == "kitchen"


def test_valid_moisture_wet():
    r = PlantReadingCreate(**{**valid_base(), "moisture": 0, "status": "wet"})
    assert r.moisture == 0


def test_valid_moisture_dry():
    r = PlantReadingCreate(**{**valid_base(), "moisture": 1, "status": "dry"})
    assert r.moisture == 1


def test_valid_sensor_id_with_hyphens():
    r = PlantReadingCreate(**{**valid_base(), "sensor_id": "my-plant-01"})
    assert r.sensor_id == "my-plant-01"


def test_auto_timestamp():
    r = PlantReadingCreate(**valid_base())
    assert r.timestamp is not None


# --- Invalid inputs ---

def test_missing_sensor_id():
    with pytest.raises(ValidationError):
        PlantReadingCreate(moisture=0, status="wet")


def test_missing_moisture():
    with pytest.raises(ValidationError):
        PlantReadingCreate(sensor_id="plant-001", status="wet")


def test_missing_status():
    with pytest.raises(ValidationError):
        PlantReadingCreate(sensor_id="plant-001", moisture=0)


def test_empty_sensor_id():
    with pytest.raises(ValidationError):
        PlantReadingCreate(**{**valid_base(), "sensor_id": ""})


def test_sensor_id_too_long():
    with pytest.raises(ValidationError):
        PlantReadingCreate(**{**valid_base(), "sensor_id": "x" * 51})


def test_sensor_id_invalid_chars():
    with pytest.raises(ValidationError):
        PlantReadingCreate(**{**valid_base(), "sensor_id": "plant@001!"})


def test_moisture_invalid():
    with pytest.raises(ValidationError):
        PlantReadingCreate(**{**valid_base(), "moisture": 5})


def test_status_invalid():
    with pytest.raises(ValidationError):
        PlantReadingCreate(**{**valid_base(), "status": "moist"})