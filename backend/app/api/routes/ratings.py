import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from app.core.database import get_db
from app.models.user import User
from app.models.rating import Rating
from app.schemas.rating import RatingRead

router = APIRouter(tags=["Ratings"])


@router.get("/users/{user_id}/ratings", response_model=List[RatingRead], summary="Get ratings for a user")
def get_user_ratings(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve peer ratings (given or received) for a specific user_id.
    Returns HTTP 404 if the user does not exist.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    ratings = db.scalars(
        select(Rating).where(
            or_(
                Rating.reviewer_id == user_id,
                Rating.reviewed_id == user_id
            )
        )
    ).all()
    return ratings
