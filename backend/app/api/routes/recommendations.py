import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.recommendation.schemas import (
    CandidateRecommendation,
    ReciprocalMatchScores,
    ReciprocalMatchSimulationRequest,
    CollaborativeCandidateRecommendation,
    HybridCandidateRecommendation,
)
from app.recommendation.engine import (
    calculate_reciprocal_match,
    calculate_reciprocal_match_for_users,
    get_candidate_recommendations,
)
from app.recommendation.collaborative import get_collaborative_recommendations
from app.recommendation.hybrid import (
    DEFAULT_CONTENT_WEIGHT,
    DEFAULT_COLLABORATIVE_WEIGHT,
    validate_hybrid_weights,
    get_hybrid_recommendations,
)

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/hybrid", response_model=List[HybridCandidateRecommendation], summary="Get final hybrid recommendation candidates")
def get_hybrid_recommendations_for_user(
    limit: Optional[int] = 50,
    content_weight: float = DEFAULT_CONTENT_WEIGHT,
    collaborative_weight: float = DEFAULT_COLLABORATIVE_WEIGHT,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns candidate students ranked by final hybrid recommendation score combining:
    1. Content-based reciprocal skill compatibility (Stage 5A/5B)
    2. User-user collaborative filtering engagement score (Stage 5D)
    
    If collaborative signals are unavailable for a candidate or student (cold start),
    gracefully falls back to pure content-based reciprocal score without penalty.
    """
    try:
        validate_hybrid_weights(content_weight, collaborative_weight)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    candidates = get_hybrid_recommendations(
        user_id=current_user.id,
        db=db,
        limit=limit,
        content_weight=content_weight,
        collaborative_weight=collaborative_weight
    )
    return candidates


@router.get("/collaborative", response_model=List[CollaborativeCandidateRecommendation], summary="Get collaborative filtering recommendation candidates")
def get_collaborative_recommendations_for_user(
    limit: Optional[int] = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns candidate students ranked by user-user collaborative filtering
    based on genuine interaction history in PostgreSQL.
    Excludes the authenticated student, already interacted students, and test accounts.
    Returns an empty list on cold-start (zero interaction history) without fabricating scores.
    """
    candidates = get_collaborative_recommendations(
        user_id=current_user.id,
        db=db,
        limit=limit
    )
    return candidates


@router.get("", response_model=List[CandidateRecommendation], summary="Get ranked reciprocal skill match candidates")
def get_recommendations_for_current_user(
    limit: Optional[int] = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns database-driven candidate skill partners ranked by reciprocal match score.
    Excludes the authenticated student, inactive users, and test users (is_test=True).
    Includes demo profiles and real student users.
    """
    candidates = get_candidate_recommendations(
        user_id=current_user.id,
        db=db,
        limit=limit
    )
    return candidates


@router.get("/match/{candidate_user_id}", response_model=ReciprocalMatchScores, summary="Calculate reciprocal match with a specific candidate")
def calculate_match_with_user(
    candidate_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes directional and reciprocal scores between authenticated user and specified candidate.
    """
    if candidate_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot calculate reciprocal match with oneself"
        )

    candidate = db.get(User, candidate_user_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate user '{candidate_user_id}' not found"
        )

    scores = calculate_reciprocal_match_for_users(
        user_a_id=current_user.id,
        user_b_id=candidate_user_id,
        db=db
    )
    return scores


@router.post("/simulate", response_model=ReciprocalMatchScores, summary="Simulate reciprocal match between arbitrary skill sets")
def simulate_reciprocal_match(
    request: ReciprocalMatchSimulationRequest
):
    """
    Stateless endpoint for development and testing to inspect:
    - forward_score (A_wants vs B_offers)
    - reverse_score (A_offers vs B_wants)
    - reciprocal_score ((forward + reverse) / 2)
    """
    scores = calculate_reciprocal_match(
        user_a_offers=request.user_a_offers,
        user_a_wants=request.user_a_wants,
        user_b_offers=request.user_b_offers,
        user_b_wants=request.user_b_wants
    )
    return scores
