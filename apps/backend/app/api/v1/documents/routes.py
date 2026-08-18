import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import SessionLocal
from app.db.models.document import Document
from app.services.document_processing_service import process_document


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


UPLOAD_DIR = Path("../../data/uploads")


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
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

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

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