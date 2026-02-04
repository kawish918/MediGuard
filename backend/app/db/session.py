# backend/app/db/session.py

from sqlmodel import create_engine, SQLModel, Session
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent / "medguard.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
