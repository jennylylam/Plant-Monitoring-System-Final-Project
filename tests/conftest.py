import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime, timezone


@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("app.database.client", MagicMock())
    monkeypatch.setattr("app.database.get_database", lambda: mock)
    monkeypatch.setattr("app.database.check_db_health", lambda: True)
    return mock


@pytest.fixture
def client(mock_db):
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "change-me-to-something-secret"}


@pytest.fixture
def sample_readings():
    return [
        {"sensor_id": "plant-001", "moisture": 0, "status": "wet",
         "timestamp": datetime(2024, 3, 15, 10, 0, tzinfo=timezone.utc), "location": "kitchen"},
        {"sensor_id": "plant-001", "moisture": 1, "status": "dry",
         "timestamp": datetime(2024, 3, 15, 11, 0, tzinfo=timezone.utc), "location": "kitchen"},
        {"sensor_id": "plant-001", "moisture": 1, "status": "dry",
         "timestamp": datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc), "location": "kitchen"},
    ]