import uuid
import math
import logging
from typing import List, Optional
import numpy as np
from sqlalchemy.orm import Session

from app.models.user import User
from app.recommendation.schemas import HybridCandidateRecommendation
from app.recommendation.engine import get_candidate_recommendations
from app.recommendation.collaborative import get_collaborative_recommendations

logger = logging.getLogger("skillswap.recommendation.hybrid")

# ==============================================================================
# CONFIGURABLE WEIGHT CONSTANTS (Stage 5E)
# ==============================================================================
# IMPORTANT ARCHITECTURAL NOTE:
# 70/30 is an initial baseline weighting and must be evaluated experimentally.
# The later evaluation stage will compare different weight configurations
# using recommendation metrics (e.g. Precision@K, Recall@K, NDCG, Reciprocity).
DEFAULT_CONTENT_WEIGHT: float = 0.70
DEFAULT_COLLABORATIVE_WEIGHT: float = 0.30


def validate_hybrid_weights(content_weight: float, collaborative_weight: float) -> None:
    """
    Validates hybrid weighting constraints:
    1. content_weight >= 0
    2. collaborative_weight >= 0
    3. content_weight + collaborative_weight == 1.0 (within float tolerance)
    
    Raises:
        ValueError: If any constraint is violated.
    """
    if content_weight < 0.0:
        raise ValueError(f"Content weight cannot be negative: {content_weight}")
    if collaborative_weight < 0.0:
        raise ValueError(f"Collaborative weight cannot be negative: {collaborative_weight}")
    
    total_weight = content_weight + collaborative_weight
    if not math.isclose(total_weight, 1.0, rel_tol=1e-5, abs_tol=1e-5):
        raise ValueError(
            f"Hybrid weights must sum to 1.0. Received content_weight={content_weight}, "
            f"collaborative_weight={collaborative_weight} (sum={total_weight:.4f})"
        )


def calculate_hybrid_score(
    content_score: float,
    collaborative_score: Optional[float] = None,
    content_weight: float = DEFAULT_CONTENT_WEIGHT,
    collaborative_weight: float = DEFAULT_COLLABORATIVE_WEIGHT,
) -> float:
    """
    Pure evaluation/scoring utility to combine content-based and collaborative signals.
    
    Baseline formula:
        If collaborative_score is unavailable (cold-start / insufficient history):
            hybrid_score = content_score
        If collaborative_score is available:
            hybrid_score = content_weight * content_score + collaborative_weight * collaborative_score
            
    Guarantees:
    - Rejects invalid weights with ValueError
    - Handles missing collaborative signal via documented cold-start fallback
    - Clamps all inputs to [0.0, 1.0] safely
    - Never produces NaN or ZeroDivisionError
    - Always returns a score bounded strictly in [0.0, 1.0]
    """
    validate_hybrid_weights(content_weight, collaborative_weight)

    # Check and clamp content score
    if math.isnan(content_score):
        c_score = 0.0
    else:
        c_score = float(np.clip(content_score, 0.0, 1.0))

    # Cold-start fallback: When collaborative score is unavailable,
    # do NOT penalize candidate with zero. Fallback to reciprocal content score.
    if collaborative_score is None:
        return c_score

    if math.isnan(collaborative_score):
        collab_score = 0.0
    else:
        collab_score = float(np.clip(collaborative_score, 0.0, 1.0))

    raw_hybrid = (content_weight * c_score) + (collaborative_weight * collab_score)
    return float(np.clip(raw_hybrid, 0.0, 1.0))


def get_hybrid_recommendations(
    user_id: uuid.UUID,
    db: Session,
    limit: Optional[int] = None,
    content_weight: float = DEFAULT_CONTENT_WEIGHT,
    collaborative_weight: float = DEFAULT_COLLABORATIVE_WEIGHT,
) -> List[HybridCandidateRecommendation]:
    """
    Computes hybrid recommendations for an authenticated student.
    
    Combines:
    1. Content-based reciprocal skill compatibility (Stage 5A/5B)
    2. User-user collaborative filtering engagement score (Stage 5D)
    
    Candidate Pool Population Rules:
    - Excludes authenticated student
    - Excludes is_test=True students
    - Excludes inactive accounts
    - Preserves real registered students
    - Preserves controlled demo students
    - Does NOT manufacture synthetic interactions or fake candidates
    
    Cold-Start Fallback:
    - If collaborative signal is unavailable for the user or candidate,
      falls back gracefully to reciprocal content score without penalty.
    """
    validate_hybrid_weights(content_weight, collaborative_weight)

    user = db.get(User, user_id)
    if not user or not user.is_active:
        return []

    # 1. Fetch reciprocal content recommendations (full eligible candidate pool)
    content_candidates = get_candidate_recommendations(user_id=user_id, db=db, limit=None)

    # 2. Fetch collaborative recommendations (from genuine PostgreSQL interaction history)
    collab_candidates = get_collaborative_recommendations(user_id=user_id, db=db, limit=None)

    # Map collaborative results by candidate UUID string
    collab_map = {str(c.candidate_id): c for c in collab_candidates}

    hybrid_results: List[HybridCandidateRecommendation] = []
    seen_hybrid_ids = set()

    for cand in content_candidates:
        cand_id_str = str(cand.user_id)
        if cand_id_str in seen_hybrid_ids:
            continue
        seen_hybrid_ids.add(cand_id_str)
        collab_entry = collab_map.get(cand_id_str)

        if collab_entry is not None:
            collab_score: Optional[float] = collab_entry.collaborative_score
            similar_user_count: int = collab_entry.similar_user_count
            interaction_evidence_count: int = collab_entry.interaction_evidence_count
            collab_explanation: Optional[str] = collab_entry.explanation
            is_collab_available: bool = True
            collab_match_pct: Optional[int] = int(round(collab_score * 100))
            rec_explanation = (
                "Strong reciprocal skill compatibility and positive engagement from students "
                "with similar interaction patterns."
            )
        else:
            collab_score = None
            similar_user_count = 0
            interaction_evidence_count = 0
            collab_explanation = None
            is_collab_available = False
            collab_match_pct = None
            rec_explanation = (
                "Recommended based on reciprocal skill compatibility. More personalized "
                "recommendations will improve as interaction history grows."
            )

        # Compute hybrid score
        h_score = calculate_hybrid_score(
            content_score=cand.reciprocal_score,
            collaborative_score=collab_score,
            content_weight=content_weight,
            collaborative_weight=collaborative_weight,
        )

        content_match_pct = int(round(cand.reciprocal_score * 100))
        hybrid_match_pct = int(round(h_score * 100))

        hybrid_rec = HybridCandidateRecommendation(
            candidate_id=cand.user_id,
            user_id=cand.user_id,
            candidate_name=cand.full_name or "Student",
            full_name=cand.full_name or "Student",
            email=cand.email,
            avatar_url=cand.avatar_url,
            avatar=cand.avatar_url,
            college=cand.college,
            university=cand.college,
            branch=cand.branch,
            major=cand.branch,
            role=cand.role,
            year=cand.year,
            bio=cand.bio,
            location=cand.location,
            availability=cand.availability,
            gender_preference=getattr(cand, 'gender_preference', None),
            skills_offered=cand.skills_offered,
            skills_wanted=cand.skills_wanted,
            skillsOffered=cand.skillsOffered,
            skillsWanted=cand.skillsWanted,
            content_score=cand.reciprocal_score,
            collaborative_score=collab_score,
            hybrid_score=h_score,
            content_match_percentage=content_match_pct,
            collaborative_match_percentage=collab_match_pct,
            hybrid_match_percentage=hybrid_match_pct,
            match_percentage=hybrid_match_pct,
            content_match_reasons=cand.match_reasons,
            match_reasons=cand.match_reasons,
            collaborative_explanation=collab_explanation,
            recommendation_explanation=rec_explanation,
            is_collaborative_available=is_collab_available,
            similar_user_count=similar_user_count,
            interaction_evidence_count=interaction_evidence_count,
            matching_wanted_skills=cand.matching_wanted_skills,
            matching_offered_skills=cand.matching_offered_skills,
            forward_score=cand.forward_score,
            reverse_score=cand.reverse_score,
            reciprocal_score=cand.reciprocal_score,
            is_demo=cand.is_demo,
            is_test=cand.is_test,
        )
        hybrid_results.append(hybrid_rec)

    # 3. Rank by hybrid_score descending, then content_score descending, then similar_user_count descending
    hybrid_results.sort(
        key=lambda r: (r.hybrid_score, r.content_score, r.similar_user_count),
        reverse=True,
    )

    if limit is not None and limit > 0:
        hybrid_results = hybrid_results[:limit]

    return hybrid_results
