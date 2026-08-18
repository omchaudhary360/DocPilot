from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.models.chunk import DocumentChunk
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
        String(50),
        default="uploaded"
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan"
    )