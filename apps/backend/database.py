import os
from app.db.models.conversation import Conversation
from app.db.models.message import Message
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


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database()")
        )

        return result.scalar()


def create_tables():
    Base.metadata.create_all(bind=engine)