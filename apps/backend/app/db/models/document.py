from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.chunk import DocumentChunk

from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.db.base import Base


class DocumentStatus(str, enum.Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    DELETED = "deleted"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    file_name: Mapped[str] = mapped_column(String(255))

    original_name: Mapped[str] = mapped_column(String(255))

    file_type: Mapped[str] = mapped_column(String(50))

    storage_path: Mapped[str] = mapped_column(String(500))

    status: Mapped[str] = mapped_column(
        SQLEnum(DocumentStatus),
        default=DocumentStatus.UPLOADED
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    faiss_index_version: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        default=None
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="select"
    )