from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")
    SQLITE_URL = "sqlite+aiosqlite:///notes.db"
    CLOUD_DB_URL = os.getenv("CLOUD_DB_URL", "")
    CLOUD_DB_API_KEY = os.getenv("CLOUD_DB_API_KEY", "")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
    TEST_USER = os.getenv("TEST_USER", "testuser")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "testpassword")

config = Config()
