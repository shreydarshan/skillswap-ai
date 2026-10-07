import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserRead], summary="List all users")
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all registered user records.
    Returns an empty array if no users exist.
    """
    users = db.scalars(select(User)).all()
    return users


@router.get("/{user_id}", response_model=UserRead, summary="Get user by ID")
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single user record by user_id UUID.
    Returns HTTP 404 if the user is not found.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )
    return user
