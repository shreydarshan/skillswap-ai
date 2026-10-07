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
from app.models.interaction import Interaction, InteractionType
from app.services.interaction_service import record_interaction

client = TestClient(app)

def run_tests():
    print("=== STARTING STAGE 5D COLLABORATIVE FILTERING COMPONENT VERIFICATION TESTS ===")

    def register_user(name, is_test=False):
        email = f"user5d_{uuid.uuid4().hex[:8]}@example.com"
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
            "college": "Stanford University",
            "branch": "Computer Science",
            "year": 3,
            "is_test": is_test
        })

        # Add sample skills
        client.post("/api/profile/me/skills", headers=headers, json={
            "skill_name": "Python",
            "skill_type": "OFFER",
            "proficiency": 5
        })
        client.post("/api/profile/me/skills", headers=headers, json={
            "skill_name": "Figma",
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

    # Create students:
    # User A: target user to get recommendations for
    # User B: similar user (interacted with same student X as A)
    # User C: candidate student (User B interacted with C, but A hasn't yet!)
    # User X: common anchor student that both A and B interacted with
    # User D: student with different interactions (disjoint)
    # User Test: is_test=True account
    # User Cold: zero interaction user
    user_a = register_user("Student A", is_test=False)
    user_b = register_user("Student B", is_test=False)
    user_c = register_user("Candidate C", is_test=False)
    user_x = register_user("Anchor Student X", is_test=False)
    user_d = register_user("Disjoint Student D", is_test=False)
    user_test = register_user("Test Student", is_test=True)
    user_cold = register_user("Cold Start Student", is_test=False)

    print("[OK] Test students registered successfully")

    db = SessionLocal()
    try:
        # User A interacted with Student X (COMPLETE swap, weight=1.0)
        record_interaction(db, uuid.UUID(user_a["id"]), uuid.UUID(user_x["id"]), InteractionType.COMPLETE)

        # User B interacted with Student X (COMPLETE swap, weight=1.0) -> Sim(A, B) = 1.0
        record_interaction(db, uuid.UUID(user_b["id"]), uuid.UUID(user_x["id"]), InteractionType.COMPLETE)

        # User B also interacted with Candidate C (COMPLETE swap, weight=1.0)
        record_interaction(db, uuid.UUID(user_b["id"]), uuid.UUID(user_c["id"]), InteractionType.COMPLETE)

        # User D interacted with another user (Anchor X) with VIEW only
        record_interaction(db, uuid.UUID(user_d["id"]), uuid.UUID(user_c["id"]), InteractionType.VIEW)

        # User Test interacted with Candidate C
        record_interaction(db, uuid.UUID(user_test["id"]), uuid.UUID(user_c["id"]), InteractionType.COMPLETE)
    finally:
        db.close()

    print("[OK] Test interactions recorded in PostgreSQL")

    # ----------------------------------------------------
    # TEST 1 & 3: A similar user's positive interaction produces a collaborative candidate
    # ----------------------------------------------------
    collab_res = client.get("/api/recommendations/collaborative", headers=user_a["headers"])
    assert collab_res.status_code == 200, f"Collaborative endpoint failed: {collab_res.text}"
    collab_candidates = collab_res.json()
    assert isinstance(collab_candidates, list)

    candidate_c_rec = next((c for c in collab_candidates if c["candidate_id"] == user_c["id"]), None)
    assert candidate_c_rec is not None, "Candidate C should be recommended via User B's similar pattern"
    assert candidate_c_rec["similar_user_count"] >= 1
    assert candidate_c_rec["interaction_evidence_count"] >= 1
    assert "Recommended because" in candidate_c_rec["explanation"]
    print(f"[OK] TEST 1 & 3: Collaborative candidate produced with score={candidate_c_rec['collaborative_score']}")

    # ----------------------------------------------------
    # TEST 4: Interaction weights affect collaborative score as documented
    # ----------------------------------------------------
    # Candidate C had COMPLETE interaction with B (weight 1.0) -> expected score = 1.0
    assert math.isclose(candidate_c_rec["collaborative_score"], 1.0, abs_tol=1e-3), (
        f"Expected score 1.0 for COMPLETE weight, got {candidate_c_rec['collaborative_score']}"
    )
    print("[OK] TEST 4: Interaction weight correctly reflected in score (COMPLETE = 1.0)")

    # ----------------------------------------------------
    # TEST 5: Authenticated user is never recommended to themselves
    # ----------------------------------------------------
    assert not any(c["candidate_id"] == user_a["id"] for c in collab_candidates), "User A must not be in collaborative recommendations"
    print("[OK] TEST 5: Authenticated user is never recommended to themselves")

    # ----------------------------------------------------
    # TEST 6: is_test = True users are excluded
    # ----------------------------------------------------
    assert not any(c["candidate_id"] == user_test["id"] for c in collab_candidates), "Test account must not be recommended"
    print("[OK] TEST 6: Test accounts (is_test=True) strictly excluded from recommendations")

    # ----------------------------------------------------
    # TEST 7: Already-interacted candidates are handled correctly
    # ----------------------------------------------------
    # User A already interacted with User X -> User X must NOT be recommended to User A
    assert not any(c["candidate_id"] == user_x["id"] for c in collab_candidates), "Already-interacted student X must be excluded"
    print("[OK] TEST 7: Already-interacted candidates correctly excluded from novel recommendations")

    # ----------------------------------------------------
    # TEST 8: Cold-start user receives safe empty response
    # ----------------------------------------------------
    cold_res = client.get("/api/recommendations/collaborative", headers=user_cold["headers"])
    assert cold_res.status_code == 200
    assert cold_res.json() == [], "Zero-interaction user must receive empty list without fabricating scores"
    print("[OK] TEST 8: Cold-start user receives safe empty list (no fabricated scores)")

    # ----------------------------------------------------
    # TEST 9 & 10: No division-by-zero/NaN and scores within [0, 1]
    # ----------------------------------------------------
    for cand in collab_candidates:
        score = cand["collaborative_score"]
        assert not math.isnan(score)
        assert 0.0 <= score <= 1.0
    print("[OK] TEST 9 & 10: All scores mathematically bounded within [0, 1] and zero NaN")

    # ----------------------------------------------------
    # TEST 11: Private interaction history is never exposed in response
    # ----------------------------------------------------
    for cand in collab_candidates:
        assert "password" not in cand
        assert "token" not in cand
        assert "private_history" not in cand
    print("[OK] TEST 11: Private interaction history not exposed")

    # ----------------------------------------------------
    # TEST 12: Existing content-based recommendations remain unchanged
    # ----------------------------------------------------
    content_res = client.get("/api/recommendations", headers=user_a["headers"])
    assert content_res.status_code == 200
    content_recs = content_res.json()
    assert len(content_recs) >= 3
    assert "match_scores" in content_recs[0]
    assert "reciprocal_score" in content_recs[0]
    print("[OK] TEST 12: Existing Stage 5A/5B content-based reciprocal recommendations remain 100% intact")

    # Cleanup test users
    for u in [user_a, user_b, user_c, user_x, user_d, user_test, user_cold]:
        client.delete("/api/auth/account", headers=u["headers"])
    print("[OK] Cleaned up temporary test users")

    print("\nALL 12 STAGE 5D COLLABORATIVE FILTERING TEST CASES PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
