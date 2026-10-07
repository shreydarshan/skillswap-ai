import pytest
import math
from app.recommendation.similarity import (
    normalize_skill_name,
    build_skill_vector,
    compute_cosine_similarity,
    calculate_directional_score,
)
from app.recommendation.engine import calculate_reciprocal_match


class TestSkillNormalization:
    """
    Tests for skill name normalization to ensure semantic consistency.
    """

    def test_whitespace_and_case_normalization(self):
        assert normalize_skill_name("Python") == "python"
        assert normalize_skill_name("python") == "python"
        assert normalize_skill_name(" PYTHON ") == "python"
        assert normalize_skill_name("   React.js   ") == "react.js"

    def test_repeated_whitespace_normalization(self):
        assert normalize_skill_name("Machine   Learning") == "machine learning"
        assert normalize_skill_name("UI/UX \t Design") == "ui/ux design"

    def test_skill_distinction_preserved(self):
        # Do not assume React == React.js unless explicitly mapped
        assert normalize_skill_name("React") != normalize_skill_name("React.js")
        assert normalize_skill_name("C") != normalize_skill_name("C++")

    def test_empty_and_none_input(self):
        assert normalize_skill_name("") == ""
        assert normalize_skill_name("   ") == ""
        assert normalize_skill_name(None) == ""


class TestCosineSimilarityAndVectors:
    """
    Tests for vector construction and cosine similarity behavior.
    """

    def test_zero_vector_safety(self):
        import numpy as np

        vec_zero = np.zeros(5)
        vec_ones = np.ones(5)

        # Zero vector vs zero vector
        assert compute_cosine_similarity(vec_zero, vec_zero) == 0.0

        # Zero vector vs non-zero vector
        assert compute_cosine_similarity(vec_zero, vec_ones) == 0.0
        assert compute_cosine_similarity(vec_ones, vec_zero) == 0.0

    def test_empty_vector_safety(self):
        import numpy as np

        assert compute_cosine_similarity(np.array([]), np.array([])) == 0.0
        assert compute_cosine_similarity(None, np.ones(3)) == 0.0


class TestStage5ARequiredCases:
    """
    Direct implementation of the 5 required test cases in Stage 5A specification.
    """

    def test_case_1_perfect_reciprocal_match(self):
        """
        TEST 1 — Perfect reciprocal match
        A offers: Python; A wants: Figma
        B offers: Figma;  B wants: Python
        Expected: forward_score = 1.0, reverse_score = 1.0, reciprocal_score = 1.0
        """
        a_offers = ["Python"]
        a_wants = ["Figma"]
        b_offers = ["Figma"]
        b_wants = ["Python"]

        result = calculate_reciprocal_match(
            user_a_offers=a_offers,
            user_a_wants=a_wants,
            user_b_offers=b_offers,
            user_b_wants=b_wants
        )

        assert math.isclose(result.forward_score, 1.0, abs_tol=1e-5), f"Expected forward_score 1.0, got {result.forward_score}"
        assert math.isclose(result.reverse_score, 1.0, abs_tol=1e-5), f"Expected reverse_score 1.0, got {result.reverse_score}"
        assert math.isclose(result.reciprocal_score, 1.0, abs_tol=1e-5), f"Expected reciprocal_score 1.0, got {result.reciprocal_score}"

    def test_case_2_one_way_match_only(self):
        """
        TEST 2 — One-way match only
        A offers: Python; A wants: Figma
        B offers: Figma;  B wants: Spanish
        Expected: forward_score = 1.0, reverse_score = 0.0, reciprocal_score = 0.5
        """
        a_offers = ["Python"]
        a_wants = ["Figma"]
        b_offers = ["Figma"]
        b_wants = ["Spanish"]

        result = calculate_reciprocal_match(
            user_a_offers=a_offers,
            user_a_wants=a_wants,
            user_b_offers=b_offers,
            user_b_wants=b_wants
        )

        assert math.isclose(result.forward_score, 1.0, abs_tol=1e-5), f"Expected forward_score 1.0, got {result.forward_score}"
        assert math.isclose(result.reverse_score, 0.0, abs_tol=1e-5), f"Expected reverse_score 0.0, got {result.reverse_score}"
        assert math.isclose(result.reciprocal_score, 0.5, abs_tol=1e-5), f"Expected reciprocal_score 0.5, got {result.reciprocal_score}"

    def test_case_3_no_overlap(self):
        """
        TEST 3 — No overlap
        A offers: Python; A wants: Figma
        B offers: Spanish; B wants: Java
        Expected: forward_score = 0.0, reverse_score = 0.0, reciprocal_score = 0.0
        """
        a_offers = ["Python"]
        a_wants = ["Figma"]
        b_offers = ["Spanish"]
        b_wants = ["Java"]

        result = calculate_reciprocal_match(
            user_a_offers=a_offers,
            user_a_wants=a_wants,
            user_b_offers=b_offers,
            user_b_wants=b_wants
        )

        assert math.isclose(result.forward_score, 0.0, abs_tol=1e-5), f"Expected forward_score 0.0, got {result.forward_score}"
        assert math.isclose(result.reverse_score, 0.0, abs_tol=1e-5), f"Expected reverse_score 0.0, got {result.reverse_score}"
        assert math.isclose(result.reciprocal_score, 0.0, abs_tol=1e-5), f"Expected reciprocal_score 0.0, got {result.reciprocal_score}"

    def test_case_4_multiple_skills_match(self):
        """
        TEST 4 — Multiple skills
        A offers: Python, React.js; A wants: Figma, UI/UX Design
        B offers: Figma, UI/UX Design; B wants: Python, React.js
        Expected: forward_score = 1.0, reverse_score = 1.0, reciprocal_score = 1.0
        """
        a_offers = ["Python", "React.js"]
        a_wants = ["Figma", "UI/UX Design"]
        b_offers = ["Figma", "UI/UX Design"]
        b_wants = ["Python", "React.js"]

        result = calculate_reciprocal_match(
            user_a_offers=a_offers,
            user_a_wants=a_wants,
            user_b_offers=b_offers,
            user_b_wants=b_wants
        )

        assert math.isclose(result.forward_score, 1.0, abs_tol=1e-5), f"Expected forward_score 1.0, got {result.forward_score}"
        assert math.isclose(result.reverse_score, 1.0, abs_tol=1e-5), f"Expected reverse_score 1.0, got {result.reverse_score}"
        assert math.isclose(result.reciprocal_score, 1.0, abs_tol=1e-5), f"Expected reciprocal_score 1.0, got {result.reciprocal_score}"

    def test_case_5_empty_skills_safety(self):
        """
        TEST 5 — Empty skills
        If either side has no skills: The algorithm must not crash.
        Return 0 for the affected directional similarity.
        """
        # User A has empty skills
        result_empty_a = calculate_reciprocal_match(
            user_a_offers=[],
            user_a_wants=[],
            user_b_offers=["Figma"],
            user_b_wants=["Python"]
        )
        assert result_empty_a.forward_score == 0.0
        assert result_empty_a.reverse_score == 0.0
        assert result_empty_a.reciprocal_score == 0.0

        # User B has empty skills
        result_empty_b = calculate_reciprocal_match(
            user_a_offers=["Python"],
            user_a_wants=["Figma"],
            user_b_offers=[],
            user_b_wants=[]
        )
        assert result_empty_b.forward_score == 0.0
        assert result_empty_b.reverse_score == 0.0
        assert result_empty_b.reciprocal_score == 0.0

        # Only one directional side empty
        # A offers Python, wants nothing. B offers nothing, wants Python.
        result_partial_empty = calculate_reciprocal_match(
            user_a_offers=["Python"],
            user_a_wants=[],
            user_b_offers=[],
            user_b_wants=["Python"]
        )
        assert result_partial_empty.forward_score == 0.0
        assert math.isclose(result_partial_empty.reverse_score, 1.0, abs_tol=1e-5)
        assert math.isclose(result_partial_empty.reciprocal_score, 0.5, abs_tol=1e-5)


class TestExtendedScenarios:
    """
    Additional tests covering partial matching, normalization handling, and vocabulary alignment.
    """

    def test_case_insensitivity_and_whitespace_matching(self):
        """
        Verify that ' python ' matches 'Python' and 'UI/UX   design' matches 'ui/ux design'.
        """
        result = calculate_reciprocal_match(
            user_a_offers=["  PYTHON  "],
            user_a_wants=[" ui/ux   design "],
            user_b_offers=["UI/UX Design"],
            user_b_wants=["python"]
        )
        assert math.isclose(result.forward_score, 1.0, abs_tol=1e-5)
        assert math.isclose(result.reverse_score, 1.0, abs_tol=1e-5)
        assert math.isclose(result.reciprocal_score, 1.0, abs_tol=1e-5)

    def test_partial_directional_overlap(self):
        """
        A wants [Python, Rust]. B offers [Python, Go].
        Shared vocabulary: [go, python, rust]
        A_wants vector: [0, 1, 1], norm = sqrt(2)
        B_offers vector: [1, 1, 0], norm = sqrt(2)
        Dot product: 1
        Cosine similarity: 1 / (sqrt(2)*sqrt(2)) = 1 / 2 = 0.5
        """
        a_wants = ["Python", "Rust"]
        b_offers = ["Python", "Go"]
        score = calculate_directional_score(a_wants, b_offers)
        assert math.isclose(score, 0.5, abs_tol=1e-5), f"Expected 0.5, got {score}"

    def test_explicit_external_vocabulary(self):
        """
        Ensure passing an external shared vocabulary (such as from PostgreSQL)
        produces identical cosine similarity results.
        """
        vocab = ["python", "figma", "react.js", "spanish", "docker", "c++"]
        result = calculate_reciprocal_match(
            user_a_offers=["Python"],
            user_a_wants=["Figma"],
            user_b_offers=["Figma"],
            user_b_wants=["Python"],
            vocabulary=vocab
        )
        assert math.isclose(result.forward_score, 1.0, abs_tol=1e-5)
        assert math.isclose(result.reverse_score, 1.0, abs_tol=1e-5)
        assert math.isclose(result.reciprocal_score, 1.0, abs_tol=1e-5)

    def test_score_bounds_guaranteed(self):
        """
        Ensure scores never exceed [0.0, 1.0] under any circumstances.
        """
        result = calculate_reciprocal_match(
            user_a_offers=["A", "B", "C", "D"],
            user_a_wants=["E", "F", "G"],
            user_b_offers=["E", "F", "H"],
            user_b_wants=["A", "B", "Z"]
        )
        assert 0.0 <= result.forward_score <= 1.0
        assert 0.0 <= result.reverse_score <= 1.0
        assert 0.0 <= result.reciprocal_score <= 1.0
