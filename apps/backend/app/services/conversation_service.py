from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.conversation import Conversation
from app.db.models.message import Message


def create_conversation(
    db: Session,
    title: str = "New Conversation",
    document_id: int | None = None
) -> Conversation:
    """Create a new conversation"""
    conversation = Conversation(
        title=title,
        document_id=document_id
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


def get_conversations(db: Session) -> list[Conversation]:
    """Get all conversations ordered by most recent"""
    return db.query(Conversation).order_by(
        Conversation.updated_at.desc()
    ).all()


def get_conversation(
    db: Session,
    conversation_id: int
) -> Conversation | None:
    """Get a single conversation"""
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    sources: list | None = None
) -> Message:
    """Add a message to a conversation"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources
    )
    
    db.add(message)
    
    # Update conversation
    conversation = get_conversation(db, conversation_id)
    
    if conversation:
        # Auto-generate title from first user message
        if (role == "user" and 
            conversation.title == "New Conversation"):
            
            title = content.strip()
            if len(title) > 60:
                title = title[:60].rstrip() + "..."
            
            conversation.title = title
        
        # Update timestamp
        conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    return message


def delete_conversation(
    db: Session,
    conversation_id: int
) -> bool:
    """Delete a conversation"""
    conversation = get_conversation(db, conversation_id)
    
    if conversation is None:
        return False
    
    db.delete(conversation)
    db.commit()
    
    return True