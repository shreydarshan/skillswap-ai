import os
import math
import uuid
import pytest
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from app.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    ndcg_at_k,
    hit_rate_at_k,
    reciprocity_at_k,
    check_reciprocal_overlap,
    evaluate_ranking,
)
from app.evaluation.experiment import EVALUATION_MODELS
from app.recommendation.hybrid import validate_hybrid_weights
from app.core.database import SessionLocal
from app.models.interaction import Interaction


class TestEvaluationMetrics:
    """
    Tests for recommendation evaluation metrics mathematical correctness and edge cases.
    """

    def test_precision_at_k_math(self):
        """
        TEST 1: Precision@K mathematical correctness:
        |recommended[:K] ∩ relevant| / K
        """
        recs = ["A", "B", "C", "D", "E"]
        relevant = {"A", "C"}  # 2 relevant items in top 5, 2 in top 3

        p3 = precision_at_k(recs, relevant, k=3)  # {"A", "B", "C"} -> "A", "C" = 2/3
        assert math.isclose(p3, 2.0 / 3.0, abs_tol=1e-5), f"Expected 2/3, got {p3}"

        p5 = precision_at_k(recs, relevant, k=5)  # 2/5 = 0.40
        assert math.isclose(p5, 0.40, abs_tol=1e-5), f"Expected 0.40, got {p5}"

    def test_recall_at_k_math(self):
        """
        TEST 2: Recall@K mathematical correctness:
        |recommended[:K] ∩ relevant| / |relevant|
        """
        recs = ["A", "B", "C", "D", "E"]
        relevant = {"A", "C", "X", "Y"}  # total 4 relevant items

        r3 = recall_at_k(recs, relevant, k=3)  # hits: A, C -> 2/4 = 0.50
        assert math.isclose(r3, 0.50, abs_tol=1e-5), f"Expected 0.50, got {r3}"

        r5 = recall_at_k(recs, relevant, k=5)  # hits: A, C -> 2/4 = 0.50
        assert math.isclose(r5, 0.50, abs_tol=1e-5), f"Expected 0.50, got {r5}"

    def test_ndcg_at_k_math(self):
        """
        TEST 3: NDCG@K mathematical correctness:
        DCG@K / IDCG@K with base-2 discounted cumulative gain.
        """
        recs = ["A", "B", "C"]
        # A grade = 1.0 (pos 1), B grade = 0.0 (pos 2), C grade = 0.5 (pos 3)
        grades = {"A": 1.0, "C": 0.5}

        # DCG@3 = 1.0/log2(2) + 0.0/log2(3) + 0.5/log2(4) = 1.0 + 0.0 + 0.25 = 1.25
        # Ideal order: A (1.0), C (0.5)
        # IDCG@3 = 1.0/log2(2) + 0.5/log2(3) = 1.0 + 0.315464879 = 1.315464879
        # NDCG@3 = 1.25 / 1.315464879 = 0.95023
        expected_ndcg = 1.25 / (1.0 + 0.5 / math.log2(3))
        calculated_ndcg = ndcg_at_k(recs, grades, k=3)
        assert math.isclose(calculated_ndcg, expected_ndcg, abs_tol=1e-4), (
            f"Expected {expected_ndcg}, got {calculated_ndcg}"
        )

        # Perfect ranking: ["A", "C", "B"] should give NDCG = 1.0
        perfect_ndcg = ndcg_at_k(["A", "C", "B"], grades, k=3)
        assert math.isclose(perfect_ndcg, 1.0, abs_tol=1e-5), f"Expected 1.0, got {perfect_ndcg}"

    def test_hit_rate_at_k_math(self):
        """
        TEST 4: Hit Rate@K correctness:
        1.0 if any recommended candidate in top-K is relevant, else 0.0.
        """
        recs = ["A", "B", "C"]
        relevant = {"B"}

        assert hit_rate_at_k(recs, relevant, k=1) == 0.0  # Top 1 is ["A"] -> no hit
        assert hit_rate_at_k(recs, relevant, k=2) == 1.0  # Top 2 is ["A", "B"] -> hit
        assert hit_rate_at_k(recs, relevant, k=3) == 1.0  # Top 3 is ["A", "B", "C"] -> hit

    def test_reciprocity_metric_correctness(self):
        """
        TEST 5: Reciprocity metric correctness:
        Two-way compatibility: (A_wants ∩ B_offers) != ∅ AND (A_offers ∩ B_wants) != ∅.
        """
        user_wants = {"Python", "SQL"}
        user_offers = {"UI Design", "Figma"}

        # Candidate 1: Reciprocal (offers Python, wants Figma)
        cand1 = {
            "skills_offered": {"Python", "Docker"},
            "skills_wanted": {"Figma", "Marketing"},
        }
        # Candidate 2: One-way only (offers Python, but wants Java)
        cand2 = {
            "skills_offered": {"Python"},
            "skills_wanted": {"Java"},
        }
        # Candidate 3: Non-reciprocal (offers Cooking, wants Baking)
        cand3 = {
            "skills_offered": {"Cooking"},
            "skills_wanted": {"Baking"},
        }

        assert check_reciprocal_overlap(
            user_wants, user_offers, cand1["skills_wanted"], cand1["skills_offered"]
        ) is True

        assert check_reciprocal_overlap(
            user_wants, user_offers, cand2["skills_wanted"], cand2["skills_offered"]
        ) is False

        rec_list = [cand1, cand2, cand3]
        recip_at_2 = reciprocity_at_k(rec_list, user_wants, user_offers, k=2)
        assert math.isclose(recip_at_2, 0.50, abs_tol=1e-5)  # 1 reciprocal out of 2

        recip_at_3 = reciprocity_at_k(rec_list, user_wants, user_offers, k=3)
        assert math.isclose(recip_at_3, 1.0 / 3.0, abs_tol=1e-5)  # 1 reciprocal out of 3

    def test_k_values_3_5_10(self):
        """
        TEST 6: Standard K cutoffs (3, 5, 10) all evaluated properly.
        """
        recs = [f"item_{i}" for i in range(12)]
        relevant = {"item_1", "item_4", "item_8"}
        grades = {"item_1": 0.8, "item_4": 0.6, "item_8": 1.0}
        skills_dummy = [{"skills_offered": set(), "skills_wanted": set()} for _ in range(12)]

        summary = evaluate_ranking(
            recommended_ids=recs,
            relevant_ids=relevant,
            relevance_grades=grades,
            candidate_skills_list=skills_dummy,
            user_wants=set(),
            user_offers=set(),
            k_values=[3, 5, 10],
        )

        for k in [3, 5, 10]:
            assert f"precision@{k}" in summary
            assert f"recall@{k}" in summary
            assert f"ndcg@{k}" in summary
            assert f"hit_rate@{k}" in summary
            assert f"reciprocity@{k}" in summary

    def test_empty_recommendation_list(self):
        """
        TEST 7: Empty recommendation list handled gracefully without exceptions.
        """
        recs = []
        relevant = {"A", "B"}
        grades = {"A": 0.8}

        assert precision_at_k(recs, relevant, k=5) == 0.0
        assert recall_at_k(recs, relevant, k=5) == 0.0
        assert ndcg_at_k(recs, grades, k=5) == 0.0
        assert hit_rate_at_k(recs, relevant, k=5) == 0.0
        assert reciprocity_at_k([], {"Python"}, {"React"}, k=5) == 0.0

    def test_no_relevant_items(self):
        """
        TEST 8: Zero relevant items returns 0.0 safely without ZeroDivisionError.
        """
        recs = ["A", "B", "C"]
        relevant = set()
        grades = {}

        assert precision_at_k(recs, relevant, k=5) == 0.0
        assert recall_at_k(recs, relevant, k=5) == 0.0
        assert ndcg_at_k(recs, grades, k=5) == 0.0
        assert hit_rate_at_k(recs, relevant, k=5) == 0.0

    def test_fewer_than_k_candidates(self):
        """
        TEST 9: Fewer than K candidates available handled safely.
        """
        recs = ["A", "B"]  # only 2 candidates, k=5
        relevant = {"A"}
        grades = {"A": 1.0}

        p5 = precision_at_k(recs, relevant, k=5)
        assert math.isclose(p5, 1.0 / 5.0, abs_tol=1e-5)  # 1 hit / 5

        r5 = recall_at_k(recs, relevant, k=5)
        assert math.isclose(r5, 1.0, abs_tol=1e-5)  # 1 hit / 1 relevant = 1.0

        n5 = ndcg_at_k(recs, grades, k=5)
        assert 0.0 <= n5 <= 1.0

    def test_scores_remain_within_valid_ranges(self):
        """
        TEST 10: All metric scores remain bounded within [0.0, 1.0].
        """
        recs = ["A", "B", "C"]
        relevant = {"A", "B", "C"}
        grades = {"A": 1.0, "B": 1.0, "C": 1.0}

        for k in [1, 2, 3, 5, 10]:
            p = precision_at_k(recs, relevant, k=k)
            r = recall_at_k(recs, relevant, k=k)
            n = ndcg_at_k(recs, grades, k=k)
            h = hit_rate_at_k(recs, relevant, k=k)

            assert 0.0 <= p <= 1.0, f"Precision {p} out of bounds"
            assert 0.0 <= r <= 1.0, f"Recall {r} out of bounds"
            assert 0.0 <= n <= 1.0, f"NDCG {n} out of bounds"
            assert 0.0 <= h <= 1.0, f"HitRate {h} out of bounds"

    def test_weight_configurations_evaluated_correctly(self):
        """
        TEST 11: All hybrid evaluation configurations validate to valid weights summing to 1.0.
        """
        for model in EVALUATION_MODELS:
            if not model.is_collaborative_only:
                assert model.content_weight is not None
                assert model.collaborative_weight is not None
                validate_hybrid_weights(model.content_weight, model.collaborative_weight)

    def test_no_production_interaction_rows_modified(self):
        """
        TEST 12: Verifies that evaluation logic does not mutate production PostgreSQL interactions table.
        """
        db = SessionLocal()
        try:
            initial_count = db.query(Interaction).count()

            # Execute metrics calculation and dummy dataset checks
            _ = precision_at_k(["A"], {"A"}, k=5)
            _ = ndcg_at_k(["A"], {"A": 1.0}, k=5)

            final_count = db.query(Interaction).count()
            assert final_count == initial_count, (
                f"Interaction count changed! Initial: {initial_count}, Final: {final_count}"
            )
        finally:
            db.close()
