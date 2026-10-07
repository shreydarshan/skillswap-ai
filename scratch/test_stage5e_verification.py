import uuid
import sys
import os
import math
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.recommendation.hybrid import (
    DEFAULT_CONTENT_WEIGHT,
    DEFAULT_COLLABORATIVE_WEIGHT,
    validate_hybrid_weights,
    calculate_hybrid_score,
)

client = TestClient(app)


def run_tests():
    print("=== STARTING STAGE 5E HYBRID RECOMMENDATION ENGINE VERIFICATION TESTS ===")

    # --------------------------------------------------------------------------
    # 1. Pure Scoring Utility & Weight Validation (Tests 1, 2, 3, 4, 5, 8, 9, 10, 16, 17)
    # --------------------------------------------------------------------------
    print("\n--- 1. Testing Pure Scoring Utility & Weights ---")

    # Test 1: Perfect content + perfect collaborative = hybrid 1.0
    h1 = calculate_hybrid_score(1.0, 1.0, 0.70, 0.30)
    assert math.isclose(h1, 1.0, abs_tol=1e-5), f"Expected 1.0, got {h1}"
    print("[PASS] Test 1: Perfect content + perfect collaborative = 1.0")

    # Test 2: Content 1.0 + collaborative 0.0 using 70/30 = 0.70
    h2 = calculate_hybrid_score(1.0, 0.0, 0.70, 0.30)
    assert math.isclose(h2, 0.70, abs_tol=1e-5), f"Expected 0.70, got {h2}"
    print("[PASS] Test 2: Content 1.0 + collaborative 0.0 (70/30) = 0.70")

    # Test 3: Content 0.0 + collaborative 1.0 using 70/30 = 0.30
    h3 = calculate_hybrid_score(0.0, 1.0, 0.70, 0.30)
    assert math.isclose(h3, 0.30, abs_tol=1e-5), f"Expected 0.30, got {h3}"
    print("[PASS] Test 3: Content 0.0 + collaborative 1.0 (70/30) = 0.30")

    # Test 4: Both scores 0 = 0
    h4 = calculate_hybrid_score(0.0, 0.0, 0.70, 0.30)
    assert h4 == 0.0, f"Expected 0.0, got {h4}"
    print("[PASS] Test 4: Both scores 0 = 0.0")

    # Test 5: Missing collaborative score uses content-only fallback (cold start)
    h5 = calculate_hybrid_score(0.85, None, 0.70, 0.30)
    assert math.isclose(h5, 0.85, abs_tol=1e-5), f"Expected 0.85, got {h5}"
    print("[PASS] Test 5: Missing collaborative score uses content-only fallback (0.85 -> 0.85)")

    # Test 8: Hybrid scores remain in [0, 1]
    for c_val, col_val in [(1.5, 2.0), (-1.0, 0.5), (0.0, 0.0), (1.0, 1.0), (0.33, 0.67)]:
        score = calculate_hybrid_score(c_val, col_val, 0.70, 0.30)
        assert 0.0 <= score <= 1.0, f"Score {score} not bounded"
    print("[PASS] Test 8: Hybrid scores bounded strictly in [0.0, 1.0]")

    # Test 9: Invalid weights are rejected
    try:
        validate_hybrid_weights(-0.1, 1.1)
        assert False, "Should reject negative content weight"
    except ValueError:
        pass
    try:
        validate_hybrid_weights(1.1, -0.1)
        assert False, "Should reject negative collaborative weight"
    except ValueError:
        pass
    print("[PASS] Test 9: Invalid negative weights rejected")

    # Test 10: Weights must sum to 1.0
    try:
        validate_hybrid_weights(0.60, 0.30)
        assert False, "Should reject weights not summing to 1.0"
    except ValueError:
        pass
    validate_hybrid_weights(0.70, 0.30)
    print("[PASS] Test 10: Weights must sum to 1.0")

    # Test 16: Candidate ordering changes appropriately when weights change
    # Cand 1: high content 0.95, low collab 0.10 -> 0.70*0.95 + 0.30*0.10 = 0.665 + 0.03 = 0.695
    # Cand 2: low content 0.20, high collab 0.90 -> 0.70*0.20 + 0.30*0.90 = 0.14 + 0.27 = 0.410
    cand1_content_heavy = calculate_hybrid_score(0.95, 0.10, 0.70, 0.30)
    cand2_content_heavy = calculate_hybrid_score(0.20, 0.90, 0.70, 0.30)
    assert cand1_content_heavy > cand2_content_heavy

    # Collab-heavy weights: 0.10 content / 0.90 collab
    cand1_collab_heavy = calculate_hybrid_score(0.95, 0.10, 0.10, 0.90)  # 0.095 + 0.09 = 0.185
    cand2_collab_heavy = calculate_hybrid_score(0.20, 0.90, 0.10, 0.90)  # 0.02 + 0.81 = 0.830
    assert cand2_collab_heavy > cand1_collab_heavy
    print("[PASS] Test 16: Candidate ordering changes appropriately when weights change")

    # Test 17: No NaN or division-by-zero occurs
    nan_score = calculate_hybrid_score(float("nan"), float("nan"), 0.70, 0.30)
    assert not math.isnan(nan_score) and nan_score == 0.0
    print("[PASS] Test 17: No NaN or division-by-zero occurs")

    # --------------------------------------------------------------------------
    # 2. End-to-End API and Database Setup (Tests 6, 7, 11, 12, 13, 14, 15)
    # --------------------------------------------------------------------------
    print("\n--- 2. Setting up Database Candidates for End-to-End Verification ---")

    def register_user(name, offered, wanted, is_test=False):
        email = f"user5e_{uuid.uuid4().hex[:8]}@example.com"
        reg = client.post("/api/auth/register", json={
            "email": email,
            "password": "Password123!"
        })
        assert reg.status_code in (200, 201), f"Register failed: {reg.text}"
        data = reg.json()
        token = data["access_token"]
        user_id = data["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update profile
        client.put("/api/profile/me", headers=headers, json={
            "full_name": name,
            "college": "MIT",
            "branch": "Computer Science",
            "year": 3,
            "is_test": is_test
        })

        # Add skills
        for sk in offered:
            client.post("/api/profile/me/skills", headers=headers, json={
                "skill_name": sk,
                "skill_type": "OFFER",
                "proficiency": 5
            })
        for sk in wanted:
            client.post("/api/profile/me/skills", headers=headers, json={
                "skill_name": sk,
                "skill_type": "WANT",
                "proficiency": 4
            })

        return {
            "id": user_id,
            "email": email,
            "token": token,
            "headers": headers,
            "name": name,
            "is_test": is_test
        }

    # Setup students:
    # student_a: Target user (Offers: Python, Wants: Graphic Design)
    student_a = register_user("Alice Hybrid", ["Python"], ["Graphic Design"])

    # student_b: Reciprocal partner (Offers: Graphic Design, Wants: Python) -> Perfect content match
    student_b = register_user("Bob Reciprocal", ["Graphic Design"], ["Python"])

    # student_c: Non-reciprocal partner (Offers: Cooking, Wants: Gardening)
    student_c = register_user("Charlie Other", ["Cooking"], ["Gardening"])

    # student_peer: Peer who shares interactions with Alice
    student_peer = register_user("Peer Student", ["Data Science"], ["Machine Learning"])

    # student_target_shared: An anchor student that both Alice and Peer interact with
    student_target_shared = register_user("David Shared", ["Java"], ["Kotlin"])

    # student_test: is_test=True account
    student_test = register_user("Test Account 5E", ["Graphic Design"], ["Python"], is_test=True)

    # student_cold: User with no interactions
    student_cold = register_user("Cold Start Student", ["Python"], ["Graphic Design"])

    # Alice interacts with David Shared
    res_a_act = client.post("/api/interactions", headers=student_a["headers"], json={
        "target_user_id": student_target_shared["id"],
        "interaction_type": "REQUEST"
    })
    assert res_a_act.status_code == 201

    # Peer interacts with David Shared (creates cosine similarity with Alice!)
    res_peer_act1 = client.post("/api/interactions", headers=student_peer["headers"], json={
        "target_user_id": student_target_shared["id"],
        "interaction_type": "REQUEST"
    })
    assert res_peer_act1.status_code == 201

    # Peer also interacts positively with Bob Reciprocal (creates collaborative recommendation for Alice!)
    res_peer_act2 = client.post("/api/interactions", headers=student_peer["headers"], json={
        "target_user_id": student_b["id"],
        "interaction_type": "COMPLETE"
    })
    assert res_peer_act2.status_code == 201

    # --------------------------------------------------------------------------
    # Test 6: New user with no interaction history receives valid recommendations (Cold start)
    # --------------------------------------------------------------------------
    print("\n--- Testing Cold-Start User (Test 6) ---")
    resp_cold = client.get("/api/recommendations/hybrid", headers=student_cold["headers"])
    assert resp_cold.status_code == 200, f"Expected 200, got {resp_cold.status_code}: {resp_cold.text}"
    cold_recs = resp_cold.json()
    assert len(cold_recs) > 0, "Cold start user must receive recommendations from content pool"
    first_cold = cold_recs[0]
    assert first_cold["content_score"] > 0
    assert first_cold["hybrid_score"] == first_cold["content_score"], (
        f"Cold start hybrid score ({first_cold['hybrid_score']}) should equal content score ({first_cold['content_score']})"
    )
    assert first_cold["collaborative_score"] is None
    assert first_cold["is_collaborative_available"] is False
    assert "Recommended based on reciprocal skill compatibility" in first_cold["recommendation_explanation"]
    print("[PASS] Test 6: Cold start user with no interaction history receives valid fallback recommendations")

    # --------------------------------------------------------------------------
    # Test 7: Existing user with collaborative data receives combined ranking
    # --------------------------------------------------------------------------
    print("\n--- Testing User with Collaborative Data (Test 7) ---")
    resp_hybrid = client.get("/api/recommendations/hybrid", headers=student_a["headers"])
    assert resp_hybrid.status_code == 200
    hybrid_recs = resp_hybrid.json()
    assert len(hybrid_recs) > 0

    # Find Bob in recommendations
    bob_rec = next((r for r in hybrid_recs if r["candidate_id"] == student_b["id"]), None)
    assert bob_rec is not None, "Bob should be in Alice's hybrid recommendations"
    assert bob_rec["content_score"] > 0, f"Bob should have content score > 0, got {bob_rec['content_score']}"
    assert bob_rec["collaborative_score"] is not None, "Bob should have collaborative score from Peer's interaction"
    assert bob_rec["is_collaborative_available"] is True
    assert bob_rec["similar_user_count"] >= 1
    assert bob_rec["interaction_evidence_count"] >= 1

    # Verify formula on Bob: hybrid_score = 0.70 * content_score + 0.30 * collaborative_score
    expected_hybrid = (0.70 * bob_rec["content_score"]) + (0.30 * bob_rec["collaborative_score"])
    assert math.isclose(bob_rec["hybrid_score"], expected_hybrid, abs_tol=1e-3), (
        f"Bob hybrid score {bob_rec['hybrid_score']} does not match formula {expected_hybrid}"
    )
    print("[PASS] Test 7: User with collaborative data receives combined ranking with exact formula")

    # --------------------------------------------------------------------------
    # Test 9 & 10 via API Query Params
    # --------------------------------------------------------------------------
    print("\n--- Testing API Weight Validation (Tests 9 & 10) ---")
    resp_bad_neg = client.get("/api/recommendations/hybrid?content_weight=-0.2&collaborative_weight=1.2", headers=student_a["headers"])
    assert resp_bad_neg.status_code == 400
    assert "negative" in resp_bad_neg.json()["detail"].lower()
    print("[PASS] API correctly rejects negative weights (400)")

    resp_bad_sum = client.get("/api/recommendations/hybrid?content_weight=0.5&collaborative_weight=0.2", headers=student_a["headers"])
    assert resp_bad_sum.status_code == 400
    assert "sum to 1.0" in resp_bad_sum.json()["detail"].lower()
    print("[PASS] API correctly rejects weights that do not sum to 1.0 (400)")

    # --------------------------------------------------------------------------
    # Test 11: Authenticated user is excluded
    # --------------------------------------------------------------------------
    print("\n--- Testing Exclusion of Authenticated User (Test 11) ---")
    for r in hybrid_recs:
        assert r["candidate_id"] != student_a["id"], "Authenticated user must not appear in recommendations"
        assert r["email"] != student_a["email"]
    print("[PASS] Test 11: Authenticated user is excluded from hybrid recommendations")

    # --------------------------------------------------------------------------
    # Test 12: is_test=True users are excluded
    # --------------------------------------------------------------------------
    print("\n--- Testing Exclusion of is_test=True Users (Test 12) ---")
    test_cand = next((r for r in hybrid_recs if r["candidate_id"] == student_test["id"]), None)
    assert test_cand is None, "Test account must NOT appear in hybrid recommendations"
    for r in hybrid_recs:
        assert r.get("is_test") is False
    print("[PASS] Test 12: is_test=True users are excluded from hybrid recommendations")

    # --------------------------------------------------------------------------
    # Test 13: Private interaction history is not exposed
    # --------------------------------------------------------------------------
    print("\n--- Testing Privacy: No Raw Interaction Records Exposed (Test 13) ---")
    for r in hybrid_recs:
        assert "interactions" not in r
        assert "interaction_history" not in r
        assert "target_user_id" not in r
        assert "peer_users" not in r
        # Explanation does not reveal who similar students are
        if r.get("collaborative_explanation"):
            assert student_peer["name"] not in r["collaborative_explanation"]
            assert student_peer["email"] not in r["collaborative_explanation"]
    print("[PASS] Test 13: Private interaction history is not exposed")

    # --------------------------------------------------------------------------
    # Test 14: Stage 5A content score remains unchanged
    # --------------------------------------------------------------------------
    print("\n--- Testing Stage 5A Content Score Intact (Test 14) ---")
    resp_5a = client.get("/api/recommendations", headers=student_a["headers"])
    assert resp_5a.status_code == 200
    recs_5a = resp_5a.json()
    bob_5a = next((r for r in recs_5a if r["candidate_id"] == student_b["id"] or r["user_id"] == student_b["id"]), None)
    assert bob_5a is not None
    assert math.isclose(bob_5a["reciprocal_score"], bob_rec["content_score"], abs_tol=1e-5), (
        f"Stage 5A reciprocal score {bob_5a['reciprocal_score']} differs from hybrid content_score {bob_rec['content_score']}"
    )
    print("[PASS] Test 14: Stage 5A content score remains completely intact and identical")

    # --------------------------------------------------------------------------
    # Test 15: Stage 5D collaborative score remains unchanged
    # --------------------------------------------------------------------------
    print("\n--- Testing Stage 5D Collaborative Score Intact (Test 15) ---")
    resp_5d = client.get("/api/recommendations/collaborative", headers=student_a["headers"])
    assert resp_5d.status_code == 200
    recs_5d = resp_5d.json()
    bob_5d = next((r for r in recs_5d if r["candidate_id"] == student_b["id"]), None)
    assert bob_5d is not None
    assert math.isclose(bob_5d["collaborative_score"], bob_rec["collaborative_score"], abs_tol=1e-5), (
        f"Stage 5D score {bob_5d['collaborative_score']} differs from hybrid collaborative_score {bob_rec['collaborative_score']}"
    )
    print("[PASS] Test 15: Stage 5D collaborative score remains completely intact and identical")

    # Clean up temporary test users created during Stage 5E verification
    for st in [student_a, student_b, student_c, student_peer, student_target_shared, student_test, student_cold]:
        client.delete("/api/auth/account", headers=st["headers"])
    print("[PASS] Temporary test users cleaned up successfully")

    print("\n=== ALL STAGE 5E VERIFICATION TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    run_tests()
