from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "plant_data"
    api_key: str = "change-me-to-something-secret"
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()