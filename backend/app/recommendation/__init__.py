"""
SkillSwap AI Recommendation Module
Stage 5A: Content-Based Reciprocal Skill Matching Engine
"""

from app.recommendation.schemas import (
    ReciprocalMatchScores,
    CandidateRecommendation,
    ReciprocalMatchSimulationRequest,
    CollaborativeCandidateRecommendation,
    HybridCandidateRecommendation,
)
from app.recommendation.similarity import (
    normalize_skill_name,
    build_skill_vector,
    compute_cosine_similarity,
    calculate_directional_score,
)
from app.recommendation.engine import (
    calculate_reciprocal_match,
    calculate_reciprocal_match_for_users,
    get_candidate_recommendations,
    get_database_vocabulary,
    get_user_skill_names,
)
from app.recommendation.collaborative import (
    INTERACTION_WEIGHTS,
    compute_interaction_weight,
    calculate_user_user_cosine_similarity,
    load_user_interaction_profiles,
    get_collaborative_recommendations,
)
from app.recommendation.hybrid import (
    DEFAULT_CONTENT_WEIGHT,
    DEFAULT_COLLABORATIVE_WEIGHT,
    validate_hybrid_weights,
    calculate_hybrid_score,
    get_hybrid_recommendations,
)

__all__ = [
    "ReciprocalMatchScores",
    "CandidateRecommendation",
    "ReciprocalMatchSimulationRequest",
    "CollaborativeCandidateRecommendation",
    "HybridCandidateRecommendation",
    "normalize_skill_name",
    "build_skill_vector",
    "compute_cosine_similarity",
    "calculate_directional_score",
    "calculate_reciprocal_match",
    "calculate_reciprocal_match_for_users",
    "get_candidate_recommendations",
    "get_database_vocabulary",
    "get_user_skill_names",
    "INTERACTION_WEIGHTS",
    "compute_interaction_weight",
    "calculate_user_user_cosine_similarity",
    "load_user_interaction_profiles",
    "get_collaborative_recommendations",
    "DEFAULT_CONTENT_WEIGHT",
    "DEFAULT_COLLABORATIVE_WEIGHT",
    "validate_hybrid_weights",
    "calculate_hybrid_score",
    "get_hybrid_recommendations",
]
