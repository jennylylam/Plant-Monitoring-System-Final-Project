from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from app.config import settings

client: MongoClient | None = None


def get_database():
    return client[settings.database_name]


def connect_db():
    global client
    client = MongoClient(settings.mongodb_url)
    db = get_database()
    # Create indexes
    db.readings.create_index([("sensor_id", 1), ("timestamp", DESCENDING)])
    db.sensors.create_index([("last_seen", DESCENDING)])
    print("Connected to MongoDB")


def disconnect_db():
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")


def check_db_health() -> bool:
    try:
        client.admin.command("ping")
        return True
    except (ConnectionFailure, Exception):
        return False