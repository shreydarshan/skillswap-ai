import uuid
import logging
from typing import Iterable, Sequence, Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill
from app.models.user_skill import UserSkill, SkillType
from app.recommendation.schemas import ReciprocalMatchScores, CandidateRecommendation, SkillDetail
from app.recommendation.similarity import (
    normalize_skill_name,
    calculate_directional_score,
)

logger = logging.getLogger("skillswap.recommendation")


def find_matching_skills(source_skills: Iterable[str], target_skills: Iterable[str]) -> List[str]:
    """
    Finds skills present in both source and target using normalized comparison.
    Returns the target skills (with original casing) that match.
    """
    norm_source = {normalize_skill_name(s) for s in source_skills if normalize_skill_name(s)}
    matching: List[str] = []
    seen = set()
    for t in target_skills:
        norm_t = normalize_skill_name(t)
        if norm_t and norm_t in norm_source and norm_t not in seen:
            seen.add(norm_t)
            matching.append(t)
    return matching


def calculate_reciprocal_match(
    user_a_offers: Iterable[str],
    user_a_wants: Iterable[str],
    user_b_offers: Iterable[str],
    user_b_wants: Iterable[str],
    vocabulary: Optional[Sequence[str]] = None,
    candidate_id: Optional[str] = None,
    candidate_name: Optional[str] = None
) -> ReciprocalMatchScores:
    """
    Computes content-based reciprocal skill matching scores between User A and User B:
    
    1. forward_score = cosine_similarity(A_wants, B_offers)
    2. reverse_score = cosine_similarity(A_offers, B_wants)
    3. reciprocal_score = (forward_score + reverse_score) / 2
    
    All scores are mathematically guaranteed within [0.0, 1.0].
    
    :param user_a_offers: Skills offered by User A
    :param user_a_wants: Skills wanted by User A
    :param user_b_offers: Skills offered by User B
    :param user_b_wants: Skills wanted by User B
    :param vocabulary: Shared skill vocabulary (optional, built dynamically if omitted)
    :param candidate_id: Optional candidate identifier for debug logging
    :param candidate_name: Optional candidate name for debug logging
    :return: ReciprocalMatchScores model with forward_score, reverse_score, reciprocal_score
    """
    forward_score = calculate_directional_score(
        source_skills=user_a_wants,
        target_skills=user_b_offers,
        vocabulary=vocabulary
    )

    reverse_score = calculate_directional_score(
        source_skills=user_a_offers,
        target_skills=user_b_wants,
        vocabulary=vocabulary
    )

    reciprocal_score = (forward_score + reverse_score) / 2.0

    # Ensure bounds strictly within [0.0, 1.0]
    reciprocal_score = max(0.0, min(1.0, reciprocal_score))

    # Debug logging for inspection without exposing any sensitive credentials
    logger.debug(
        "Reciprocal match calculated | candidate_id=%s candidate_name='%s' | forward=%.4f reverse=%.4f reciprocal=%.4f",
        candidate_id or "unknown",
        candidate_name or "anonymous",
        forward_score,
        reverse_score,
        reciprocal_score
    )

    return ReciprocalMatchScores(
        forward_score=forward_score,
        reverse_score=reverse_score,
        reciprocal_score=reciprocal_score
    )


def get_database_vocabulary(db: Session, additional_skills: Optional[Iterable[str]] = None) -> List[str]:
    """
    Builds the shared normalized skill vocabulary from the PostgreSQL `skills` table.
    
    :param db: SQLAlchemy Session
    :param additional_skills: Any optional additional skills to include in the vocabulary
    :return: Sorted list of unique normalized skill names
    """
    catalog_skills = db.scalars(select(Skill.name)).all()
    vocab_set = {normalize_skill_name(name) for name in catalog_skills if normalize_skill_name(name)}

    if additional_skills:
        for skill in additional_skills:
            normalized = normalize_skill_name(skill)
            if normalized:
                vocab_set.add(normalized)

    return sorted(list(vocab_set))


def get_user_skill_names(user_id: uuid.UUID, db: Session) -> Tuple[List[str], List[str]]:
    """
    Retrieves the offered and wanted skill names for a given user from PostgreSQL.
    
    :param user_id: User UUID
    :param db: SQLAlchemy Session
    :return: Tuple of (skills_offered, skills_wanted)
    """
    user_skills = db.scalars(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    offers: List[str] = []
    wants: List[str] = []

    for us in user_skills:
        skill = db.get(Skill, us.skill_id)
        if skill and skill.name:
            if us.skill_type == SkillType.OFFER:
                offers.append(skill.name)
            else:
                wants.append(skill.name)

    return offers, wants


def calculate_reciprocal_match_for_users(
    user_a_id: uuid.UUID,
    user_b_id: uuid.UUID,
    db: Session
) -> ReciprocalMatchScores:
    """
    Calculates the reciprocal match between two specific registered users in PostgreSQL.
    
    :param user_a_id: Authenticated user UUID
    :param user_b_id: Candidate user UUID
    :param db: SQLAlchemy Session
    :return: ReciprocalMatchScores
    """
    a_offers, a_wants = get_user_skill_names(user_a_id, db)
    b_offers, b_wants = get_user_skill_names(user_b_id, db)

    cand_profile = db.get(Profile, user_b_id)
    cand_name = cand_profile.full_name if cand_profile else str(user_b_id)

    vocabulary = get_database_vocabulary(db)

    return calculate_reciprocal_match(
        user_a_offers=a_offers,
        user_a_wants=a_wants,
        user_b_offers=b_offers,
        user_b_wants=b_wants,
        vocabulary=vocabulary,
        candidate_id=str(user_b_id),
        candidate_name=cand_name
    )


def get_candidate_recommendations(
    user_id: uuid.UUID,
    db: Session,
    limit: Optional[int] = None
) -> List[CandidateRecommendation]:
    """
    Retrieves and ranks candidate student recommendations from PostgreSQL:
    
    Excludes:
    - Current authenticated user (user_id == current_user_id)
    - Test accounts (is_test == True)
    - Inactive / deleted users
    
    Includes:
    - Real users
    - Demo users (is_demo == True)
    
    Ranks by reciprocal_score descending, with forward_score as tiebreaker.
    
    :param user_id: Authenticated user UUID
    :param db: SQLAlchemy Session
    :param limit: Optional max number of candidates to return
    :return: List of CandidateRecommendation
    """
    # 1. Fetch current user skills
    user_offers, user_wants = get_user_skill_names(user_id, db)

    # 2. Build shared database vocabulary
    vocabulary = get_database_vocabulary(db)

    # 3. Retrieve all candidate profiles excluding current user & test accounts
    candidate_profiles = db.scalars(
        select(Profile)
        .where(Profile.user_id != user_id)
        .where(Profile.is_test == False)
    ).all()

    recommendations: List[CandidateRecommendation] = []
    seen_candidate_ids = set()

    for prof in candidate_profiles:
        if prof.user_id in seen_candidate_ids:
            continue
        seen_candidate_ids.add(prof.user_id)

        # Check active status of candidate user account
        candidate_user = db.get(User, prof.user_id)
        if not candidate_user or not candidate_user.is_active:
            continue

        cand_offers, cand_wants = get_user_skill_names(prof.user_id, db)

        scores = calculate_reciprocal_match(
            user_a_offers=user_offers,
            user_a_wants=user_wants,
            user_b_offers=cand_offers,
            user_b_wants=cand_wants,
            vocabulary=vocabulary,
            candidate_id=str(prof.user_id),
            candidate_name=prof.full_name
        )

        matching_wanted = find_matching_skills(user_wants, cand_offers)
        matching_offered = find_matching_skills(cand_wants, user_offers)

        reasons: List[str] = []
        if matching_wanted:
            reasons.append(f"They offer {', '.join(matching_wanted)}, which you want to learn.")
        if matching_offered:
            reasons.append(f"You offer {', '.join(matching_offered)}, which they want to learn.")

        if not reasons:
            if scores.forward_score > 0:
                reasons.append("There is partial alignment with skills you want to learn.")
            elif scores.reverse_score > 0:
                reasons.append("They may be interested in skills you can offer.")
            else:
                reasons.append("Explore their profile to discover complementary learning opportunities.")

        cand_name = prof.full_name or "Student"
        role_str = f"{prof.branch or 'Student'} ({prof.college or 'Campus'})"
        pct = int(round(scores.reciprocal_score * 100))

        recommendations.append(
            CandidateRecommendation(
                user_id=prof.user_id,
                candidate_id=str(prof.user_id),
                full_name=cand_name,
                candidate_name=cand_name,
                email=candidate_user.email,
                avatar_url=prof.avatar_url,
                avatar=prof.avatar_url,
                college=prof.college,
                university=prof.college,
                branch=prof.branch,
                major=prof.branch,
                role=role_str,
                year=prof.year,
                bio=prof.bio,
                location=prof.location,
                availability=prof.availability,
                gender_preference=prof.gender_preference,
                is_demo=prof.is_demo,
                is_test=prof.is_test,
                skills_offered=cand_offers,
                skills_wanted=cand_wants,
                skillsOffered=[SkillDetail(id=f"off-{i}", name=s, category="General") for i, s in enumerate(cand_offers)],
                skillsWanted=[SkillDetail(id=f"wnt-{i}", name=s, category="General") for i, s in enumerate(cand_wants)],
                match_scores=scores,
                reciprocal_score=scores.reciprocal_score,
                forward_score=scores.forward_score,
                reverse_score=scores.reverse_score,
                match_percentage=pct,
                matching_wanted_skills=matching_wanted,
                matching_offered_skills=matching_offered,
                match_reasons=reasons
            )
        )

    # 4. Rank candidates by reciprocal_score desc, then forward_score desc
    recommendations.sort(
        key=lambda r: (r.match_scores.reciprocal_score, r.match_scores.forward_score),
        reverse=True
    )

    if limit is not None and limit > 0:
        recommendations = recommendations[:limit]

    return recommendations
