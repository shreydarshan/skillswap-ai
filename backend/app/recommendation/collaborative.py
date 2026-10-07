import uuid
import math
import logging
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill
from app.models.user_skill import UserSkill, SkillType
from app.models.interaction import Interaction, InteractionType
from app.recommendation.schemas import CollaborativeCandidateRecommendation

logger = logging.getLogger("skillswap.recommendation.collaborative")

# Documented Interaction Signal Weights (Stage 5D)
# Explicit strength mapping reflecting engagement depth:
# VIEW     (0.1) -> Low positive exploratory signal
# LIKE     (0.3) -> Explicit positive endorsement/bookmark
# REQUEST  (0.6) -> Strong direct proposal to swap skills
# ACCEPT   (0.8) -> Mutual agreement to exchange knowledge
# COMPLETE (1.0) -> Highest confidence verified swap session
INTERACTION_WEIGHTS: Dict[InteractionType, float] = {
    InteractionType.VIEW: 0.1,
    InteractionType.LIKE: 0.3,
    InteractionType.REQUEST: 0.6,
    InteractionType.ACCEPT: 0.8,
    InteractionType.COMPLETE: 1.0,
}


def compute_interaction_weight(interaction_type: InteractionType) -> float:
    """
    Returns the documented numerical weight for a given interaction type.
    """
    return INTERACTION_WEIGHTS.get(interaction_type, 0.1)


def calculate_user_user_cosine_similarity(
    vector_a: Dict[uuid.UUID, float],
    vector_b: Dict[uuid.UUID, float]
) -> float:
    """
    Computes cosine similarity between two sparse user interaction profiles:
    
    sim(A, B) = dot(r_A, r_B) / (norm(r_A) * norm(r_B))
    
    Properties:
    - Bounded in [0.0, 1.0] since all interaction weights are non-negative.
    - If either vector has norm 0 (no interactions), returns 0.0 safely without ZeroDivisionError.
    - If vectors share no overlapping target students, dot product is 0 and returns 0.0.
    """
    if not vector_a or not vector_b:
        return 0.0

    # Common targets
    common_targets = set(vector_a.keys()) & set(vector_b.keys())
    if not common_targets:
        return 0.0

    dot_product = sum(vector_a[t] * vector_b[t] for t in common_targets)

    norm_a = math.sqrt(sum(v * v for v in vector_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vector_b.values()))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    raw_sim = dot_product / (norm_a * norm_b)
    # Clamp to [0.0, 1.0] to guard against floating-point imprecision
    return float(np.clip(raw_sim, 0.0, 1.0))


def load_user_interaction_profiles(
    db: Session,
    exclude_test_accounts: bool = True
) -> Dict[uuid.UUID, Dict[uuid.UUID, float]]:
    """
    Loads genuine interaction vectors from PostgreSQL.
    Maps: user_id -> { target_user_id: max_interaction_weight }
    
    Excludes:
    - Self-interactions (user_id == target_user_id)
    - Test accounts (is_test == True)
    - Inactive / deleted users
    """
    # 1. Gather all active non-test user IDs
    users_query = (
        select(User.id)
        .join(Profile, Profile.user_id == User.id)
        .where(User.is_active == True)
    )
    if exclude_test_accounts:
        users_query = users_query.where(Profile.is_test == False)

    eligible_user_ids = set(db.scalars(users_query).all())

    # 2. Query genuine interactions between eligible users
    interactions = db.scalars(
        select(Interaction)
        .where(Interaction.user_id.in_(eligible_user_ids))
        .where(Interaction.target_user_id.in_(eligible_user_ids))
        .where(Interaction.user_id != Interaction.target_user_id)
    ).all()

    # 3. Aggregate sparse vectors by user using max weight per target student
    user_profiles: Dict[uuid.UUID, Dict[uuid.UUID, float]] = defaultdict(dict)
    for inter in interactions:
        weight = compute_interaction_weight(inter.interaction_type)
        prev = user_profiles[inter.user_id].get(inter.target_user_id, 0.0)
        if weight > prev:
            user_profiles[inter.user_id][inter.target_user_id] = weight

    return dict(user_profiles)


def get_collaborative_recommendations(
    user_id: uuid.UUID,
    db: Session,
    limit: Optional[int] = 50,
    min_similarity: float = 0.05
) -> List[CollaborativeCandidateRecommendation]:
    """
    Generates user-user collaborative filtering recommendations based on genuine PostgreSQL interactions.
    
    Algorithm:
    1. Retrieve authenticated user A's historical interaction profile.
    2. Check Cold-Start: If A has 0 interactions, return empty list (no fake scores).
    3. Calculate user-user cosine similarity with all other active non-test users.
    4. Identify candidate students interacted with by similar users (sim > min_similarity).
    5. Exclude:
       - User A themselves
       - Candidates User A has already interacted with (recommending novel peer partners)
       - Inactive / test accounts
    6. Aggregate similarity-weighted collaborative evidence:
       score(A, C) = sum(sim(A, U) * r_{U, C}) / sum(sim(A, U))
    7. Normalize score within [0.0, 1.0].
    8. Return ranked candidates with transparent collaborative explanation.
    """
    # 1. Load interaction profiles for all eligible students
    all_profiles = load_user_interaction_profiles(db, exclude_test_accounts=True)

    user_vector = all_profiles.get(user_id, {})

    # Cold-start handling: return empty list immediately if user has no interaction history
    if not user_vector:
        logger.debug("Cold-start: user %s has no interaction history. Returning empty collaborative list.", user_id)
        return []

    # 2. Calculate similarities with other users
    similarities: Dict[uuid.UUID, float] = {}
    for other_id, other_vector in all_profiles.items():
        if other_id == user_id:
            continue
        sim = calculate_user_user_cosine_similarity(user_vector, other_vector)
        if sim >= min_similarity:
            similarities[other_id] = sim

    if not similarities:
        logger.debug("No similar users found above threshold for user %s.", user_id)
        return []

    # 3. Find candidate students interacted with by similar users
    # Candidates already interacted with by User A are excluded from novel partner discovery
    already_interacted = set(user_vector.keys())

    candidate_evidence: Dict[uuid.UUID, List[Tuple[float, float]]] = defaultdict(list)
    candidate_interaction_counts: Dict[uuid.UUID, int] = defaultdict(int)

    for other_id, sim in similarities.items():
        other_vector = all_profiles[other_id]
        for candidate_id, weight in other_vector.items():
            if candidate_id == user_id:
                continue
            if candidate_id in already_interacted:
                continue
            candidate_evidence[candidate_id].append((sim, weight))
            candidate_interaction_counts[candidate_id] += 1

    if not candidate_evidence:
        return []

    # 4. Score candidates via similarity-weighted aggregation
    recommendations: List[CollaborativeCandidateRecommendation] = []

    for candidate_id, evidence in candidate_evidence.items():
        # Validate candidate exists, is active, and is not a test account
        candidate_user = db.get(User, candidate_id)
        if not candidate_user or not candidate_user.is_active:
            continue

        candidate_profile = db.get(Profile, candidate_id)
        if candidate_profile and candidate_profile.is_test:
            continue

        sum_sim_weight = sum(sim * weight for sim, weight in evidence)
        sum_sim = sum(sim for sim, _ in evidence)

        if sum_sim == 0.0:
            continue

        # Weighted average rating: bounded strictly in [0.0, 1.0]
        raw_score = sum_sim_weight / sum_sim
        collab_score = float(np.clip(raw_score, 0.0, 1.0))

        # Retrieve skills for candidate details
        cand_user_skills = db.scalars(
            select(UserSkill).where(UserSkill.user_id == candidate_id)
        ).all()
        skills_offered: List[str] = []
        skills_wanted: List[str] = []
        for us in cand_user_skills:
            sk = db.get(Skill, us.skill_id)
            if sk and sk.name:
                if us.skill_type == SkillType.OFFER:
                    skills_offered.append(sk.name)
                else:
                    skills_wanted.append(sk.name)

        cand_name = (candidate_profile.full_name if candidate_profile else None) or "Student"
        num_similar = len(evidence)
        num_interactions = candidate_interaction_counts[candidate_id]

        explanation = (
            f"Recommended because {num_similar} student{'s' if num_similar > 1 else ''} "
            f"with similar interaction patterns engaged positively with this student."
        )

        recommendations.append(
            CollaborativeCandidateRecommendation(
                candidate_id=candidate_id,
                candidate_name=cand_name,
                collaborative_score=collab_score,
                similar_user_count=num_similar,
                interaction_evidence_count=num_interactions,
                explanation=explanation,
                email=candidate_user.email,
                avatar_url=candidate_profile.avatar_url if candidate_profile else None,
                college=candidate_profile.college if candidate_profile else None,
                branch=candidate_profile.branch if candidate_profile else None,
                year=candidate_profile.year if candidate_profile else None,
                bio=candidate_profile.bio if candidate_profile else None,
                skills_offered=skills_offered,
                skills_wanted=skills_wanted,
                is_demo=candidate_profile.is_demo if candidate_profile else False
            )
        )

    # 5. Rank by collaborative_score descending, then similar_user_count descending
    recommendations.sort(
        key=lambda r: (r.collaborative_score, r.similar_user_count),
        reverse=True
    )

    if limit is not None and limit > 0:
        recommendations = recommendations[:limit]

    return recommendations
