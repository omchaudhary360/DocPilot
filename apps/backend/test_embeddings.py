from database import SessionLocal
from app.db.models.chunk import DocumentChunk
from app.services.embedding_service import generate_embedding


db = SessionLocal()

try:
    chunk = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == 1)
        .order_by(DocumentChunk.chunk_index)
        .first()
    )

    if chunk is None:
        print("No chunk found.")
    else:
        embedding = generate_embedding(chunk.text_content)

        print(f"Chunk ID: {chunk.id}")
        print(f"Page: {chunk.page_number}")
        print(f"Embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")

finally:
    db.close()