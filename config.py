import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-this-secret")
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "instance" / "flowpilot.db"))
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
