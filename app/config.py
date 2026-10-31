import os
from pydantic import BaseModel

class Settings(BaseModel):
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    enable_gemini: bool = os.getenv("ENABLE_GEMINI", "true").lower() in ("true", "1")
    gemini_timeout_seconds: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))
    gemini_max_retries: int = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./netcoop.db")
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    protocol_version: str = "1.0"
    schema_version: str = "1.0"

settings = Settings()