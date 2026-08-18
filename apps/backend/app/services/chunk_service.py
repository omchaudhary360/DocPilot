import re

from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split cleaned page text into meaningful paragraphs.
    """
    paragraphs = re.split(r"\n\s*\n", text)

    return [
        paragraph.strip()
        for paragraph in paragraphs
        if paragraph.strip()
    ]


def create_chunks(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 150
) -> list[dict]:
    """
    Create chunks using paragraph boundaries while
    preserving page numbers.
    """

    chunks = []

    for page in pages:
        page_number = page["page_number"]
        text = page["text"]

        if not text:
            continue

        paragraphs = split_into_paragraphs(text)

        current_chunk = ""

        for paragraph in paragraphs:

            # If adding this paragraph keeps us within the target size
            if len(current_chunk) + len(paragraph) + 1 <= chunk_size:
                current_chunk = (
                    f"{current_chunk}\n{paragraph}"
                    if current_chunk
                    else paragraph
                )

            else:
                # Save current chunk
                if current_chunk:
                    chunks.append(
                        {
                            "chunk_index": len(chunks),
                            "page_number": page_number,
                            "text": current_chunk.strip(),
                        }
                    )

                # Start a new chunk
                current_chunk = paragraph

        # Save remaining text from the page
        if current_chunk:
            chunks.append(
                {
                    "chunk_index": len(chunks),
                    "page_number": page_number,
                    "text": current_chunk.strip(),
                }
            )

    return chunks


def save_chunks(
    db: Session,
    document_id: int,
    chunks: list[dict]
) -> int:
    """
    Save chunks for a document in PostgreSQL.
    """

    chunk_objects = []

    for chunk in chunks:
        chunk_object = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk["chunk_index"],
            text_content=chunk["text"],
            page_number=chunk["page_number"],
        )

        chunk_objects.append(chunk_object)

    if not chunk_objects:
        return 0

    db.add_all(chunk_objects)
    db.commit()

    return len(chunk_objects)