import uuid
import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill
from app.models.user_skill import UserSkill, SkillType
from app.models.interaction import Interaction, InteractionType
from app.evaluation.relevance import RelevanceCriterion, get_user_relevance_map

logger = logging.getLogger("skillswap.evaluation.dataset")


@dataclass
class UserEvaluationProfile:
    """
    In-memory representation of a student user for evaluation purposes.
    """
    user_id: uuid.UUID
    name: str
    email: str
    skills_offered: Set[str] = field(default_factory=set)
    skills_wanted: Set[str] = field(default_factory=set)
    interaction_count: int = 0
    relevant_candidate_ids: Set[uuid.UUID] = field(default_factory=set)
    relevance_grades: Dict[uuid.UUID, float] = field(default_factory=dict)
    is_cold_start: bool = True
    has_sufficient_history: bool = False


@dataclass
class EvaluationDataset:
    """
    Complete evaluation dataset snapshot extracted safely from PostgreSQL.
    """
    users: Dict[uuid.UUID, UserEvaluationProfile] = field(default_factory=dict)
    total_users_count: int = 0
    total_interactions_count: int = 0
    interaction_distribution: Dict[str, int] = field(default_factory=dict)
    cold_start_user_ids: List[uuid.UUID] = field(default_factory=list)
    insufficient_history_user_ids: List[uuid.UUID] = field(default_factory=list)
    evaluable_user_ids: List[uuid.UUID] = field(default_factory=list)
    criterion: RelevanceCriterion = field(default_factory=RelevanceCriterion)


def build_evaluation_dataset(
    db: Session,
    criterion: Optional[RelevanceCriterion] = None,
    min_interactions_for_eval: int = 1,
) -> EvaluationDataset:
    """
    Builds an isolated evaluation dataset snapshot from PostgreSQL without modifying
    any records or schema tables.
    
    Data Integrity Guarantee:
    - Performs strictly read-only SELECT queries.
    - Excludes is_test=True profiles and inactive user accounts.
    - Zero synthetic rows inserted or mutated.
    """
    if criterion is None:
        criterion = RelevanceCriterion()

    # 1. Load active, non-test profiles & users
    profiles = db.scalars(
        select(Profile).where(Profile.is_test == False)
    ).all()

    users_map: Dict[uuid.UUID, UserEvaluationProfile] = {}

    for prof in profiles:
        user = db.get(User, prof.user_id)
        if not user or not user.is_active:
            continue

        users_map[prof.user_id] = UserEvaluationProfile(
            user_id=prof.user_id,
            name=prof.full_name or "Student",
            email=user.email,
        )

    # 2. Load skills for all cohort users
    user_skills = db.scalars(select(UserSkill)).all()
    skills_by_id = {s.id: s.name for s in db.scalars(select(Skill)).all()}

    for us in user_skills:
        if us.user_id in users_map and us.skill_id in skills_by_id:
            skill_name = skills_by_id[us.skill_id]
            if us.skill_type == SkillType.OFFER:
                users_map[us.user_id].skills_offered.add(skill_name)
            else:
                users_map[us.user_id].skills_wanted.add(skill_name)

    # 3. Load genuine interactions
    interactions = db.scalars(select(Interaction)).all()

    interaction_dist: Dict[str, int] = {
        itype.value: 0 for itype in InteractionType
    }

    user_interactions_count: Dict[uuid.UUID, int] = {}

    for inter in interactions:
        interaction_dist[inter.interaction_type.value] = (
            interaction_dist.get(inter.interaction_type.value, 0) + 1
        )
        if inter.user_id in users_map:
            user_interactions_count[inter.user_id] = (
                user_interactions_count.get(inter.user_id, 0) + 1
            )

    # 4. Compute ground truth relevance per user
    user_relevance_map = get_user_relevance_map(interactions, criterion=criterion)

    cold_start_ids: List[uuid.UUID] = []
    insufficient_ids: List[uuid.UUID] = []
    evaluable_ids: List[uuid.UUID] = []

    for uid, profile in users_map.items():
        count = user_interactions_count.get(uid, 0)
        profile.interaction_count = count
        profile.relevance_grades = user_relevance_map.get(uid, {})
        profile.relevant_candidate_ids = {
            target for target, grade in profile.relevance_grades.items()
            if grade >= criterion.min_graded_weight
        }

        if count == 0:
            profile.is_cold_start = True
            profile.has_sufficient_history = False
            cold_start_ids.append(uid)
        elif count < min_interactions_for_eval:
            profile.is_cold_start = False
            profile.has_sufficient_history = False
            insufficient_ids.append(uid)
        else:
            profile.is_cold_start = False
            profile.has_sufficient_history = True
            # User is evaluable if they have at least 1 ground truth interaction to test against
            if profile.relevant_candidate_ids or profile.relevance_grades:
                evaluable_ids.append(uid)
            else:
                insufficient_ids.append(uid)

    return EvaluationDataset(
        users=users_map,
        total_users_count=len(users_map),
        total_interactions_count=len(interactions),
        interaction_distribution=interaction_dist,
        cold_start_user_ids=cold_start_ids,
        insufficient_history_user_ids=insufficient_ids,
        evaluable_user_ids=evaluable_ids,
        criterion=criterion,
    )
