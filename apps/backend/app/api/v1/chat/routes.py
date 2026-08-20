from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal

from app.services.rag_service import answer_question

from app.services.conversation_service import (
    get_conversation,
    add_message,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# =========================================
# REQUEST MODEL
# =========================================

class ChatRequest(BaseModel):

    question: str

    document_id: int | None = None

    conversation_id: int | None = None

    top_k: int = 3


# =========================================
# DATABASE
# =========================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================
# CHAT
# =========================================

@router.post("")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):

    # =====================================
    # VALIDATE QUESTION
    # =====================================

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )


    # =====================================
    # VALIDATE CONVERSATION
    # =====================================

    if request.conversation_id is not None:

        conversation = get_conversation(
            db=db,
            conversation_id=request.conversation_id
        )

        if conversation is None:

            raise HTTPException(
                status_code=404,
                detail="Conversation not found."
            )


    # =====================================
    # SAVE USER MESSAGE
    # =====================================

    if request.conversation_id is not None:

        add_message(
            db=db,
            conversation_id=request.conversation_id,
            role="user",
            content=request.question
        )


    # =====================================
    # RAG
    # =====================================

    result = answer_question(
        db=db,
        question=request.question,
        document_id=request.document_id,
        top_k=request.top_k
    )


    # =====================================
    # SAVE ASSISTANT MESSAGE
    # =====================================

    if request.conversation_id is not None:

        add_message(
            db=db,
            conversation_id=request.conversation_id,
            role="assistant",
            content=result["answer"]
        )


    # =====================================
    # RETURN RESPONSE
    # =====================================

    return result