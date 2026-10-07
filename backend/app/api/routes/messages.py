import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.core.database import get_db
from app.models.user import User
from app.models.message import Message
from app.schemas.message import MessageRead

router = APIRouter(tags=["Messages"])


from app.api.deps import get_current_user


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
        )
    ).all()
    return messages


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
def get_user_messages(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve direct messages (sent or received) for a specific user_id.
    Returns HTTP 404 if the user does not exist.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    messages = db.scalars(
        select(Message).where(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        )
    ).all()
    return messages
