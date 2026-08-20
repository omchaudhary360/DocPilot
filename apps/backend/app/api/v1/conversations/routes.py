from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from app.services.conversation_service import (
    create_conversation,
    get_conversations,
    get_conversation,
    delete_conversation,
)


router = APIRouter(prefix="/conversations", tags=["Conversations"])


class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"
    document_id: int | None = None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def create_new_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db)
):
    """Create a new conversation"""
    conversation = create_conversation(
        db=db,
        title=request.title,
        document_id=request.document_id,
    )
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "document_id": conversation.document_id,
        "document_name": (
            conversation.document.original_name
            if conversation.document
            else None
        ),
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
    }


@router.get("")
def list_conversations(db: Session = Depends(get_db)):
    """List all conversations"""
    conversations = get_conversations(db)
    
    return [
        {
            "id": conversation.id,
            "title": conversation.title,
            "document_id": conversation.document_id,
            "document_name": (
                conversation.document.original_name
                if conversation.document
                else None
            ),
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.get("/{conversation_id}")
def get_single_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a single conversation with all messages"""
    conversation = get_conversation(db, conversation_id)
    
    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "document_id": conversation.document_id,
        "document_name": (
            conversation.document.original_name
            if conversation.document
            else None
        ),
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "sources": message.sources or [],
                "created_at": message.created_at,
            }
            for message in conversation.messages
        ],
    }


@router.delete("/{conversation_id}")
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    deleted = delete_conversation(db, conversation_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )
    
    return {
        "message": "Conversation deleted successfully.",
        "conversation_id": conversation_id
    }