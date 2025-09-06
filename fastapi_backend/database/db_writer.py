import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, Field
from typing import Optional
from fastapi_backend.database.models import Users,BlueTeams,CheckInstance,IOCCheckResult

DB_PATH = Path(__file__).parent.parent.parent / "db" / "database.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Create ../db/ if it doesn't exist

# Create database engine
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=False to suppress SQL logs

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    print(f"Database created at {DB_PATH}")
