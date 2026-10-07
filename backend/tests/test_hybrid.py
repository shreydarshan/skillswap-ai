import math
import pytest
from app.recommendation.hybrid import (
    DEFAULT_CONTENT_WEIGHT,
    DEFAULT_COLLABORATIVE_WEIGHT,
    validate_hybrid_weights,
    calculate_hybrid_score,
)


class TestHybridScoringMath:
    """
    Mathematical tests for Stage 5E hybrid recommendation score calculation.
    """

    def test_perfect_content_and_perfect_collaborative(self):
        """
        TEST 1: Perfect content (1.0) + perfect collaborative (1.0) = hybrid 1.0.
        """
        score = calculate_hybrid_score(1.0, 1.0, 0.70, 0.30)
        assert math.isclose(score, 1.0, abs_tol=1e-5), f"Expected 1.0, got {score}"

    def test_content_max_collaborative_zero(self):
        """
        TEST 2: Content 1.0 + collaborative 0.0 using 70/30 = 0.70.
        """
        score = calculate_hybrid_score(1.0, 0.0, 0.70, 0.30)
        assert math.isclose(score, 0.70, abs_tol=1e-5), f"Expected 0.70, got {score}"

    def test_content_zero_collaborative_max(self):
        """
        TEST 3: Content 0.0 + collaborative 1.0 using 70/30 = 0.30.
        """
        score = calculate_hybrid_score(0.0, 1.0, 0.70, 0.30)
        assert math.isclose(score, 0.30, abs_tol=1e-5), f"Expected 0.30, got {score}"

    def test_both_scores_zero(self):
        """
        TEST 4: Both scores 0 = 0.0.
        """
        score = calculate_hybrid_score(0.0, 0.0, 0.70, 0.30)
        assert score == 0.0

    def test_missing_collaborative_uses_content_only_fallback(self):
        """
        TEST 5: Missing collaborative score uses content-only fallback (cold start).
        Candidate is NOT penalized with 0.0 for collaborative component.
        """
        score = calculate_hybrid_score(0.85, None, 0.70, 0.30)
        assert math.isclose(score, 0.85, abs_tol=1e-5), f"Expected fallback 0.85, got {score}"

        # Even with different weights, fallback to content remains unchanged
        score_50_50 = calculate_hybrid_score(0.65, None, 0.50, 0.50)
        assert math.isclose(score_50_50, 0.65, abs_tol=1e-5), f"Expected fallback 0.65, got {score_50_50}"

    def test_hybrid_scores_remain_bounded_in_unit_interval(self):
        """
        TEST 8: Hybrid scores remain strictly in [0.0, 1.0] even with out-of-bounds inputs.
        """
        test_inputs = [
            (1.5, 1.2),
            (-0.5, 0.5),
            (0.0, 0.0),
            (1.0, 1.0),
            (0.45, 0.85),
            (-1.0, -1.0),
            (2.0, None),
        ]
        for c, col in test_inputs:
            h = calculate_hybrid_score(c, col, 0.70, 0.30)
            assert 0.0 <= h <= 1.0, f"Score {h} out of bounds for inputs ({c}, {col})"

    def test_invalid_negative_weights_rejected(self):
        """
        TEST 9: Invalid negative weights are rejected with ValueError.
        """
        with pytest.raises(ValueError, match="Content weight cannot be negative"):
            validate_hybrid_weights(-0.1, 1.1)

        with pytest.raises(ValueError, match="Collaborative weight cannot be negative"):
            validate_hybrid_weights(1.1, -0.1)

        with pytest.raises(ValueError):
            calculate_hybrid_score(0.8, 0.8, content_weight=-0.5, collaborative_weight=1.5)

    def test_weights_must_sum_to_one(self):
        """
        TEST 10: Weights must sum to 1.0.
        """
        with pytest.raises(ValueError, match="Hybrid weights must sum to 1.0"):
            validate_hybrid_weights(0.60, 0.30)  # Sums to 0.90

        with pytest.raises(ValueError, match="Hybrid weights must sum to 1.0"):
            validate_hybrid_weights(0.80, 0.40)  # Sums to 1.20

        # Valid sum: 0.70 + 0.30 == 1.0
        validate_hybrid_weights(0.70, 0.30)
        # Valid sum: 0.50 + 0.50 == 1.0
        validate_hybrid_weights(0.50, 0.50)
        # Valid sum: 1.0 + 0.0 == 1.0
        validate_hybrid_weights(1.0, 0.0)

    def test_candidate_ordering_changes_appropriately_when_weights_change(self):
        """
        TEST 16: Candidate ordering changes appropriately when weights change.
        Candidate A: high content (0.9), low collaborative (0.2)
        Candidate B: low content (0.3), high collaborative (0.9)
        Under 70/30 (content-heavy): Candidate A wins
        Under 20/80 (collab-heavy): Candidate B wins
        """
        score_a_content_heavy = calculate_hybrid_score(0.9, 0.2, 0.70, 0.30)  # 0.70*0.9 + 0.30*0.2 = 0.63 + 0.06 = 0.69
        score_b_content_heavy = calculate_hybrid_score(0.3, 0.9, 0.70, 0.30)  # 0.70*0.3 + 0.30*0.9 = 0.21 + 0.27 = 0.48
        assert score_a_content_heavy > score_b_content_heavy, "Candidate A should win under content-heavy weighting"

        score_a_collab_heavy = calculate_hybrid_score(0.9, 0.2, 0.20, 0.80)  # 0.20*0.9 + 0.80*0.2 = 0.18 + 0.16 = 0.34
        score_b_collab_heavy = calculate_hybrid_score(0.3, 0.9, 0.20, 0.80)  # 0.20*0.3 + 0.80*0.9 = 0.06 + 0.72 = 0.78
        assert score_b_collab_heavy > score_a_collab_heavy, "Candidate B should win under collaborative-heavy weighting"

    def test_no_nan_or_division_by_zero_occurs(self):
        """
        TEST 17: No NaN or division-by-zero occurs even with float('nan') or zero division attempts.
        """
        score_nan_content = calculate_hybrid_score(float('nan'), 0.5, 0.70, 0.30)
        assert not math.isnan(score_nan_content)
        assert 0.0 <= score_nan_content <= 1.0

        score_nan_collab = calculate_hybrid_score(0.8, float('nan'), 0.70, 0.30)
        assert not math.isnan(score_nan_collab)
        assert 0.0 <= score_nan_collab <= 1.0

        score_nan_both = calculate_hybrid_score(float('nan'), float('nan'), 0.70, 0.30)
        assert not math.isnan(score_nan_both)
        assert score_nan_both == 0.0
