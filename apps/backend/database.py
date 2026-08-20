import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document
from app.db.models.conversation import Conversation
from app.db.models.message import Message


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def test_database_connection():
    """Test database connectivity"""
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database()")
            )
            return result.scalar()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)