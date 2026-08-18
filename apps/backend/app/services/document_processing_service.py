from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document
from app.services.pdf_extraction_service import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.chunk_service import create_chunks, save_chunks
from app.services.embedding_service import generate_embeddings
from app.services.faiss_service import add_embeddings_to_index


def process_document(
    db: Session,
    document_id: int,
    file_path: str
) -> int:
    """
    Complete document processing pipeline:

    PDF
    → text extraction
    → cleaning
    → chunking
    → PostgreSQL
    → embeddings
    → FAISS
    """

    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise ValueError(
            f"Document {document_id} not found."
        )

    try:
        # 1. Mark as processing
        document.status = "processing"
        db.commit()

        # 2. Extract text
        pages = extract_text_from_pdf(file_path)

        # 3. Clean text
        cleaned_pages = [
            {
                "page_number": page["page_number"],
                "text": clean_text(page["text"]),
            }
            for page in pages
        ]

        # 4. Create chunks
        chunks = create_chunks(cleaned_pages)

        if not chunks:
            raise ValueError(
                "No text chunks were created."
            )

        # 5. Save chunks to PostgreSQL
        saved_count = save_chunks(
            db=db,
            document_id=document_id,
            chunks=chunks
        )

        # 6. Get saved chunks
        saved_chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
            .all()
        )

        texts = [
            chunk.text_content
            for chunk in saved_chunks
        ]

        chunk_ids = [
            chunk.id
            for chunk in saved_chunks
        ]

        # 7. Generate embeddings
        embeddings = generate_embeddings(texts)

        # 8. Add embeddings to FAISS
        add_embeddings_to_index(
            embeddings=embeddings,
            chunk_ids=chunk_ids
        )

        # 9. Mark as processed
        document.status = "processed"
        db.commit()

        return saved_count

    except Exception:
        document.status = "failed"
        db.commit()
        raise