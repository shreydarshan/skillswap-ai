import uuid
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field
from app.models.interaction import Interaction, InteractionType
from app.recommendation.collaborative import INTERACTION_WEIGHTS

# Default positive engagement signals:
# REQUEST (0.6), ACCEPT (0.8), COMPLETE (1.0) indicate active swap intention or completed exchange.
# VIEW (0.1) is purely exploratory, and LIKE (0.3) is passive bookmarking.
DEFAULT_POSITIVE_TYPES: Set[InteractionType] = {
    InteractionType.REQUEST,
    InteractionType.ACCEPT,
    InteractionType.COMPLETE,
}

# Graded relevance weights reflecting interaction depth for DCG/NDCG:
GRADED_RELEVANCE_WEIGHTS: Dict[InteractionType, float] = dict(INTERACTION_WEIGHTS)


@dataclass
class RelevanceCriterion:
    """
    Configurable relevance criteria for recommendation evaluation.
    
    Attributes:
        positive_interaction_types: Set of interaction types considered binary positive relevance.
        min_graded_weight: Minimum weight threshold for binary relevance.
        graded_weights: Map of InteractionType to numerical relevance grade [0.0, 1.0].
        include_likes_as_positive: If True, extends positive types to include LIKE (0.3).
    """
    positive_interaction_types: Set[InteractionType] = field(
        default_factory=lambda: set(DEFAULT_POSITIVE_TYPES)
    )
    min_graded_weight: float = 0.6
    graded_weights: Dict[InteractionType, float] = field(
        default_factory=lambda: dict(GRADED_RELEVANCE_WEIGHTS)
    )
    include_likes_as_positive: bool = False

    def __post_init__(self):
        if self.include_likes_as_positive:
            self.positive_interaction_types.add(InteractionType.LIKE)
            self.min_graded_weight = min(self.min_graded_weight, 0.3)

    def is_relevant(self, interaction_type: InteractionType) -> bool:
        """Determines if a given interaction indicates positive relevance."""
        return interaction_type in self.positive_interaction_types

    def get_grade(self, interaction_type: InteractionType) -> float:
        """Returns graded relevance value in [0.0, 1.0]."""
        return self.graded_weights.get(interaction_type, 0.1)


def get_user_relevance_map(
    interactions: List[Interaction],
    criterion: Optional[RelevanceCriterion] = None,
) -> Dict[uuid.UUID, Dict[uuid.UUID, float]]:
    """
    Builds a mapping of user_id -> {candidate_id: graded_relevance_score}
    and filters to highest observed engagement per candidate.
    
    Returns:
        Dict[user_id, Dict[candidate_id, max_graded_score]]
    """
    if criterion is None:
        criterion = RelevanceCriterion()

    user_candidate_grades: Dict[uuid.UUID, Dict[uuid.UUID, float]] = {}

    for inter in interactions:
        uid = inter.user_id
        target = inter.target_user_id
        grade = criterion.get_grade(inter.interaction_type)

        if uid not in user_candidate_grades:
            user_candidate_grades[uid] = {}

        # Retain maximum observed engagement grade for this candidate
        current = user_candidate_grades[uid].get(target, 0.0)
        if grade > current:
            user_candidate_grades[uid][target] = grade

    return user_candidate_grades
