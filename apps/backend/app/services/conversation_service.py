from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.conversation import Conversation
from app.db.models.message import Message


# =========================================
# CREATE CONVERSATION
# =========================================

def create_conversation(
    db: Session,
    title: str = "New Conversation",
    document_id: int | None = None
) -> Conversation:

    conversation = Conversation(
        title=title,
        document_id=document_id
    )

    db.add(conversation)

    db.commit()

    db.refresh(conversation)

    return conversation


# =========================================
# GET ALL CONVERSATIONS
# =========================================

def get_conversations(
    db: Session
) -> list[Conversation]:

    return (
        db.query(Conversation)
        .order_by(
            Conversation.updated_at.desc()
        )
        .all()
    )


# =========================================
# GET SINGLE CONVERSATION
# =========================================

def get_conversation(
    db: Session,
    conversation_id: int
) -> Conversation | None:

    return (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id
        )
        .first()
    )


# =========================================
# ADD MESSAGE
# =========================================

def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
    sources: list | None = None
) -> Message:

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources
    )

    db.add(message)


    conversation = get_conversation(
        db,
        conversation_id
    )


    if conversation:

        # -----------------------------------------
        # Generate title from first user question
        # -----------------------------------------

        if (
            role == "user"
            and conversation.title == "New Conversation"
        ):

            title = content.strip()

            if len(title) > 60:

                title = (
                    title[:60].rstrip()
                    + "..."
                )

            conversation.title = title


        # -----------------------------------------
        # Update timestamp
        # -----------------------------------------

        conversation.updated_at = (
            datetime.utcnow()
        )


    db.commit()

    db.refresh(message)

    return message


# =========================================
# DELETE CONVERSATION
# =========================================

def delete_conversation(
    db: Session,
    conversation_id: int
) -> bool:

    conversation = get_conversation(
        db,
        conversation_id
    )


    if conversation is None:
        return False


    db.delete(conversation)

    db.commit()

    return True