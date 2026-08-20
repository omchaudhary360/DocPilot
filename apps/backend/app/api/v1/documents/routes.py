import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import SessionLocal
from app.db.models.document import Document
from app.services.document_processing_service import process_document


router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a PDF document.
    
    Returns:
    {
        "message": str,
        "document_id": int,
        "file_name": str,
        "status": str,
        "chunks_created": int
    }
    """
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )
    
    # Save file
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    file_path = UPLOAD_DIR / file.filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database record
    document = Document(
        file_name=file.filename,
        original_name=file.filename,
        file_type="pdf",
        storage_path=str(file_path),
        status="uploaded"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document
    try:
        chunks_count = process_document(
            db=db,
            document_id=document.id,
            file_path=str(file_path)
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(error)}"
        )
    
    return {
        "message": "Document uploaded and processed successfully",
        "document_id": document.id,
        "file_name": document.original_name,
        "status": document.status,
        "chunks_created": chunks_count
    }


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).all()
    
    return [
        {
            "id": doc.id,
            "file_name": doc.original_name,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at,
            "indexed_at": doc.indexed_at,
        }
        for doc in documents
    ]


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and its chunks"""
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )
    
    # Remove file
    try:
        Path(document.storage_path).unlink(missing_ok=True)
    except Exception:
        pass
    
    # Remove from FAISS
    from app.services.faiss_service import remove_document_from_index
    remove_document_from_index(document_id)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }