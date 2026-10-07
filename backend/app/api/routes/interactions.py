import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.interaction import Interaction
from app.schemas.interaction import InteractionRead, InteractionCreate, InteractionResponse
from app.api.deps import get_current_user
from app.services.interaction_service import record_interaction, get_user_interactions_history

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post("", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED, summary="Record a user interaction")
def log_interaction(
    interaction_in: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Records a genuine interaction (VIEW, LIKE, REQUEST, ACCEPT, COMPLETE) between the authenticated
    user and a target student.
    
    Rules:
    - Never records self-interactions (HTTP 400).
    - Requires valid, existing target user (HTTP 404).
    - Rejects unauthenticated callers (HTTP 401).
    - Silently excludes test accounts (is_test=True) from persistent storage without breaking the caller.
    """
    # 1. Reject self-interaction
    if interaction_in.target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot record self-interaction"
        )

    # 2. Validate target user exists and is active
    target_user = db.get(User, interaction_in.target_user_id)
    if not target_user or not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target user '{interaction_in.target_user_id}' not found"
        )

    # 3. Check for test accounts (is_test == True)
    curr_profile = db.get(Profile, current_user.id)
    target_profile = db.get(Profile, interaction_in.target_user_id)
    if (curr_profile and curr_profile.is_test) or (target_profile and target_profile.is_test):
        return InteractionResponse(
            status="success",
            recorded=False,
            message="Interaction skipped for test account"
        )

    # 4. Record interaction safely
    interaction = record_interaction(
        db=db,
        user_id=current_user.id,
        target_user_id=interaction_in.target_user_id,
        interaction_type=interaction_in.interaction_type
    )

    if not interaction:
        return InteractionResponse(
            status="success",
            recorded=False,
            message="Interaction filtered or cooldown active"
        )

    return InteractionResponse(
        status="success",
        recorded=True,
        interaction=interaction,
        message="Interaction recorded successfully"
    )


@router.get("/me", response_model=List[InteractionRead], summary="Get authenticated student's interaction history")
def get_my_interactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the authenticated student's own private interaction history.
    """
    return get_user_interactions_history(db, current_user.id)


@router.get("/users/{user_id}/interactions", response_model=List[InteractionRead], summary="Get interactions for a user (strictly restricted to owner)")
def get_user_interactions(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Protected interaction history retrieval.
    Enforces privacy: students can ONLY view their own interaction history.
    """
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view another user's private interaction history"
        )

    return get_user_interactions_history(db, user_id)
