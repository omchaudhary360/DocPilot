from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document, DocumentStatus
from app.services.pdf_extraction_service import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.chunk_service import create_chunks, save_chunks
from app.services.embedding_service import generate_embeddings
from app.services.faiss_service import add_embeddings_to_index


def delete_document_chunks_and_index(db: Session, document_id: int) -> bool:
    """
    Delete all chunks for a document from database and FAISS index.
    """
    
    # Remove chunks from database
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()
    db.commit()
    
    # Remove from FAISS index
    from app.services.faiss_service import remove_document_from_index
    remove_document_from_index(document_id)
    
    return True


def process_document(
    db: Session,
    document_id: int,
    file_path: str
) -> int:
    """
    Complete document processing pipeline:
    
    1. Validate document
    2. Extract text from PDF (with OCR fallback)
    3. Clean text
    4. Create semantic chunks
    5. Save to PostgreSQL
    6. Generate embeddings
    7. Index in FAISS
    8. Mark as processed
    
    Returns: Number of chunks created
    """
    
    # Get document
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if document is None:
        raise ValueError(f"Document {document_id} not found")
    
    try:
        # Mark as processing
        document.status = DocumentStatus.PROCESSING
        db.commit()
        
        # 1. Extract text
        pages = extract_text_from_pdf(file_path)
        
        if not pages or all(not p.get("text") for p in pages):
            raise ValueError("No text could be extracted from PDF")
        
        # 2. Clean text
        cleaned_pages = [
            {
                "page_number": page["page_number"],
                "text": clean_text(page["text"]),
            }
            for page in pages
        ]
        
        # 3. Create chunks
        chunks = create_chunks(cleaned_pages, chunk_size=1000)
        
        if not chunks:
            raise ValueError("No text chunks were created from document")
        
        # 4. Remove any previous chunks for this document
        # (in case of reprocessing)
        delete_document_chunks_and_index(db, document_id)
        
        # 5. Save chunks to database
        saved_count = save_chunks(
            db=db,
            document_id=document_id,
            chunks=chunks
        )
        
        if saved_count == 0:
            raise ValueError("Failed to save chunks to database")
        
        # 6. Get saved chunks
        saved_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_index).all()
        
        # 7. Generate embeddings
        texts = [chunk.text_content for chunk in saved_chunks]
        embeddings = generate_embeddings(texts)
        
        if len(embeddings) != len(saved_chunks):
            raise ValueError("Embedding count mismatch")
        
        # 8. Prepare metadata
        metadata = [
            {
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in saved_chunks
        ]
        
        # 9. Add to FAISS index
        add_embeddings_to_index(
            embeddings=embeddings,
            chunk_ids=[chunk.id for chunk in saved_chunks],
            document_id=document_id,
            document_metadata=metadata
        )
        
        # 10. Mark chunks as indexed
        for chunk in saved_chunks:
            chunk.is_indexed = True
            chunk.embedding_model = "all-MiniLM-L6-v2"
        
        # 11. Mark document as processed
        document.status = DocumentStatus.PROCESSED
        document.indexed_at = datetime.utcnow()
        document.faiss_index_version = 1
        db.commit()
        
        return saved_count
        
    except Exception as error:
        # Mark as failed
        document.status = DocumentStatus.FAILED
        db.commit()
        
        # Cleanup
        delete_document_chunks_and_index(db, document_id)
        
        raise RuntimeError(f"Document processing failed: {str(error)}")