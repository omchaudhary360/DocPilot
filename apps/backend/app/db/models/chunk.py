from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.document import Document

from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Text, Float, String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    __table_args__ = (
        Index('idx_document_id', 'document_id'),
        Index('idx_chunk_index', 'chunk_index'),
        Index('idx_document_status', 'document_id', 'is_indexed'),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    text_content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    is_indexed: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )

    faiss_position: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    char_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    document: Mapped["Document"] = relationship(
        back_populates="chunks",
        lazy="select"
    )