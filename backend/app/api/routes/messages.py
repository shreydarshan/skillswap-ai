import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_, asc
from app.core.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.message import Message
from app.schemas.message import MessageRead, MessageCreate
from app.api.deps import get_current_user

router = APIRouter(tags=["Messages"])


def _format_message_read(msg: Message, db: Session) -> MessageRead:
    sender_prof = db.get(Profile, msg.sender_id)
    receiver_prof = db.get(Profile, msg.receiver_id)
    sender_name = sender_prof.full_name if (sender_prof and sender_prof.full_name) else "Student"
    receiver_name = receiver_prof.full_name if (receiver_prof and receiver_prof.full_name) else "Student"
    sender_avatar = sender_prof.avatar_url if sender_prof else None
    receiver_avatar = receiver_prof.avatar_url if receiver_prof else None

    return MessageRead(
        id=msg.id,
        sender_id=msg.sender_id,
        receiver_id=msg.receiver_id,
        message=msg.message,
        created_at=msg.created_at,
        sender_name=sender_name,
        receiver_name=receiver_name,
        sender_avatar=sender_avatar,
        receiver_avatar=receiver_avatar
    )


@router.post("/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED, summary="Send a direct message to a student")
def send_message(
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sends a direct message from the authenticated student to a recipient student.
    Derives sender identity strictly from JWT.
    Validates recipient exists, prevents self-messaging, and validates non-empty message content.
    """
    if message_in.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send a message to yourself"
        )

    clean_content = message_in.message.strip()
    if not clean_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty"
        )

    receiver = db.get(User, message_in.receiver_id)
    if not receiver or not receiver.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipient student '{message_in.receiver_id}' not found"
        )

    new_msg = Message(
        sender_id=current_user.id,
        receiver_id=message_in.receiver_id,
        message=clean_content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)

    return _format_message_read(new_msg, db)


@router.get("/messages/me", response_model=List[MessageRead], summary="Get authenticated user's messages")
def get_my_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve direct messages for the authenticated student.
    """
    messages = db.scalars(
        select(Message).where(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id
            )
        ).order_by(asc(Message.created_at))
    ).all()
    return [_format_message_read(m, db) for m in messages]


@router.get("/messages/conversations/{other_user_id}", response_model=List[MessageRead], summary="Get conversation messages with a specific student")
def get_conversation_messages(
    other_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve direct messages exchanged between the authenticated student and a specific peer student.
    """
    messages = db.scalars(
        select(Message).where(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id),
            )
        ).order_by(asc(Message.created_at))
    ).all()
    return [_format_message_read(m, db) for m in messages]


@router.get("/messages/me/unread-count", summary="Get unread message count for authenticated user")
def get_my_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the count of unread messages for the authenticated student.
    """
    messages = db.scalars(
        select(Message).where(Message.receiver_id == current_user.id)
    ).all()
    return {"unread_count": len(messages)}


@router.get("/users/{user_id}/messages", response_model=List[MessageRead], summary="Get messages for a user")
def get_user_messages(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve direct messages for a specific user_id.
    Strictly protected: A user can only inspect their own message history.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view another student's private messages"
        )

    messages = db.scalars(
        select(Message).where(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).order_by(asc(Message.created_at))
    ).all()
    return [_format_message_read(m, db) for m in messages]
