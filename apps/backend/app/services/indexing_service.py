from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.services.embedding_service import generate_embeddings
from app.services.faiss_service import add_embeddings_to_index


def build_document_index(
    db: Session,
    document_id: int
):
    """
    Generate embeddings for all chunks of a document
    and add them to the shared FAISS index.
    """

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    if not chunks:
        raise ValueError(
            f"No chunks found for document {document_id}"
        )

    texts = [
        chunk.text_content
        for chunk in chunks
    ]

    chunk_ids = [
        chunk.id
        for chunk in chunks
    ]

    embeddings = generate_embeddings(texts)

    index = add_embeddings_to_index(
        embeddings=embeddings,
        chunk_ids=chunk_ids
    )

    return {
        "document_id": document_id,
        "chunks_indexed": len(chunks),
        "total_vectors_in_index": index.ntotal,
        "embedding_dimension": index.d,
    }