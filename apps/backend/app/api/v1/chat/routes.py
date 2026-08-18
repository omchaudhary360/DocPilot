from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from app.services.rag_service import answer_question


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    question: str
    document_id: int | None = None
    top_k: int = 3


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    result = answer_question(
        db=db,
        question=request.question,
        document_id=request.document_id,
        top_k=request.top_k
    )

    return result