import uuid
import math
import pytest
from app.models.interaction import InteractionType
from app.recommendation.collaborative import (
    INTERACTION_WEIGHTS,
    compute_interaction_weight,
    calculate_user_user_cosine_similarity,
)


class TestCollaborativeAlgorithmMath:
    """
    Mathematical tests for user-user collaborative filtering similarity & weighting.
    """

    def test_interaction_weights_ranking(self):
        """
        Verify documented interaction weight hierarchy:
        VIEW < LIKE < REQUEST < ACCEPT <= COMPLETE
        """
        assert compute_interaction_weight(InteractionType.VIEW) == 0.1
        assert compute_interaction_weight(InteractionType.LIKE) == 0.3
        assert compute_interaction_weight(InteractionType.REQUEST) == 0.6
        assert compute_interaction_weight(InteractionType.ACCEPT) == 0.8
        assert compute_interaction_weight(InteractionType.COMPLETE) == 1.0

        assert compute_interaction_weight(InteractionType.VIEW) < compute_interaction_weight(InteractionType.LIKE)
        assert compute_interaction_weight(InteractionType.LIKE) < compute_interaction_weight(InteractionType.REQUEST)
        assert compute_interaction_weight(InteractionType.REQUEST) < compute_interaction_weight(InteractionType.ACCEPT)
        assert compute_interaction_weight(InteractionType.ACCEPT) < compute_interaction_weight(InteractionType.COMPLETE)

    def test_identical_interaction_patterns_high_similarity(self):
        """
        TEST 1: Two users with identical interaction patterns have similarity 1.0.
        """
        target_1 = uuid.uuid4()
        target_2 = uuid.uuid4()

        vec_a = {target_1: 0.6, target_2: 1.0}
        vec_b = {target_1: 0.6, target_2: 1.0}

        sim = calculate_user_user_cosine_similarity(vec_a, vec_b)
        assert math.isclose(sim, 1.0, abs_tol=1e-5), f"Expected 1.0, got {sim}"

    def test_disjoint_interaction_patterns_zero_similarity(self):
        """
        TEST 2: Users with no overlapping interaction history have zero similarity.
        """
        target_1 = uuid.uuid4()
        target_2 = uuid.uuid4()
        target_3 = uuid.uuid4()
        target_4 = uuid.uuid4()

        vec_a = {target_1: 1.0, target_2: 0.8}
        vec_b = {target_3: 1.0, target_4: 0.8}

        sim = calculate_user_user_cosine_similarity(vec_a, vec_b)
        assert sim == 0.0

    def test_partial_overlap_similarity(self):
        """
        Partial overlap gives correct cosine angle between non-negative vectors.
        """
        target_common = uuid.uuid4()
        target_a_only = uuid.uuid4()
        target_b_only = uuid.uuid4()

        # Both rated target_common with 1.0
        vec_a = {target_common: 1.0, target_a_only: 1.0}  # norm = sqrt(2)
        vec_b = {target_common: 1.0, target_b_only: 1.0}  # norm = sqrt(2)

        # dot = 1.0; sim = 1.0 / (sqrt(2)*sqrt(2)) = 0.5
        sim = calculate_user_user_cosine_similarity(vec_a, vec_b)
        assert math.isclose(sim, 0.5, abs_tol=1e-5)

    def test_zero_vector_and_none_safety(self):
        """
        Ensure zero vectors, empty dictionaries, and empty vectors never raise exceptions or NaN.
        """
        target_1 = uuid.uuid4()
        vec_valid = {target_1: 1.0}

        assert calculate_user_user_cosine_similarity({}, {}) == 0.0
        assert calculate_user_user_cosine_similarity(vec_valid, {}) == 0.0
        assert calculate_user_user_cosine_similarity({}, vec_valid) == 0.0
        assert calculate_user_user_cosine_similarity(None, vec_valid) == 0.0
        assert calculate_user_user_cosine_similarity(vec_valid, None) == 0.0

    def test_similarity_strictly_bounded(self):
        """
        Verify similarity is always clamped within [0.0, 1.0].
        """
        t1, t2, t3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        vec_a = {t1: 0.1, t2: 0.8, t3: 0.3}
        vec_b = {t1: 0.6, t2: 1.0, t3: 0.1}

        sim = calculate_user_user_cosine_similarity(vec_a, vec_b)
        assert 0.0 <= sim <= 1.0
