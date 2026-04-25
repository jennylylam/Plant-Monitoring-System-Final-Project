from fastapi import FastAPI, HTTPException, Depends, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from contextlib import asynccontextmanager
from typing import Annotated

from app.models import (
    PlantReadingCreate, PlantReadingResponse,
    SensorResponse, StatsResponse, ErrorResponse
)
from app.database import connect_db, disconnect_db, get_database, check_db_health
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()
    yield
    disconnect_db()


app = FastAPI(title="Plant Monitoring API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth ---

def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# --- Helpers ---

def reading_from_doc(doc: dict) -> PlantReadingResponse:
    return PlantReadingResponse(
        id=str(doc["_id"]),
        sensor_id=doc["sensor_id"],
        moisture=doc["moisture"],
        status=doc["status"],
        timestamp=doc["timestamp"],
        location=doc.get("location"),
    )


def upsert_sensor(db, sensor_id: str, location: str | None):
    now = datetime.now(timezone.utc)
    db.sensors.update_one(
        {"_id": sensor_id},
        {
            "$setOnInsert": {"registered_at": now},
            "$set": {"last_seen": now, "location": location},
        },
        upsert=True,
    )


# --- Endpoints ---

@app.post("/api/v1/readings", response_model=PlantReadingResponse, status_code=201)
def create_reading(reading: PlantReadingCreate, _=Depends(verify_api_key)):
    db = get_database()
    doc = reading.model_dump()
    if doc["timestamp"] is None:
        doc["timestamp"] = datetime.now(timezone.utc)

    result = db.readings.insert_one(doc)
    upsert_sensor(db, reading.sensor_id, reading.location)

    doc["_id"] = result.inserted_id
    return reading_from_doc(doc)


@app.get("/api/v1/readings", response_model=dict)
def get_readings(
    sensor_id: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _=Depends(verify_api_key),
):
    db = get_database()
    query = {}
    if sensor_id:
        query["sensor_id"] = sensor_id
    if start or end:
        query["timestamp"] = {}
        if start:
            query["timestamp"]["$gte"] = start
        if end:
            query["timestamp"]["$lte"] = end

    total = db.readings.count_documents(query)
    cursor = db.readings.find(query).sort("timestamp", -1).skip(offset).limit(limit)
    readings = [reading_from_doc(doc) for doc in cursor]

    return {"count": len(readings), "total": total, "readings": readings}


@app.get("/api/v1/readings/{sensor_id}/latest", response_model=PlantReadingResponse)
def get_latest(sensor_id: str, _=Depends(verify_api_key)):
    db = get_database()
    doc = db.readings.find_one({"sensor_id": sensor_id}, sort=[("timestamp", -1)])
    if not doc:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"No readings found for sensor '{sensor_id}'"}
        )
    return reading_from_doc(doc)


@app.get("/api/v1/sensors", response_model=dict)
def get_sensors(_=Depends(verify_api_key)):
    db = get_database()
    sensors = []
    for doc in db.sensors.find().sort("last_seen", -1):
        sensors.append(SensorResponse(
            sensor_id=doc["_id"],
            name=doc.get("name"),
            location=doc.get("location"),
            registered_at=doc["registered_at"],
            last_seen=doc["last_seen"],
        ))
    return {"count": len(sensors), "sensors": sensors}


@app.get("/api/v1/sensors/{sensor_id}/stats", response_model=StatsResponse)
def get_stats(
    sensor_id: str,
    hours: int = Query(default=24, ge=1, le=720),
    _=Depends(verify_api_key),
):
    db = get_database()
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    readings = list(db.readings.find({"sensor_id": sensor_id, "timestamp": {"$gte": since}}))

    if not readings:
        raise HTTPException(
            status_code=404,
            detail={"error": "NOT_FOUND", "message": f"No readings for '{sensor_id}' in last {hours}h"}
        )

    total = len(readings)
    dry_count = sum(1 for r in readings if r["moisture"] == 1)
    wet_count = total - dry_count

    return StatsResponse(
        sensor_id=sensor_id,
        period_hours=hours,
        total_readings=total,
        wet_count=wet_count,
        dry_count=dry_count,
        dry_percentage=round(dry_count / total * 100, 1),
    )


@app.get("/health")
def health():
    db_ok = check_db_health()
    if not db_ok:
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "database": "disconnected"})