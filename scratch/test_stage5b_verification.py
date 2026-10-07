import uuid
import sys
import os
import math
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_tests():
    print("=== STARTING STAGE 5B REAL RECOMMENDATION ENGINE -> FRONTEND VERIFICATION TESTS ===")

    # Setup helper
    def create_user(name, offers, wants, is_test=False, is_demo=False):
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
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

        for off in offers:
            client.post("/api/profile/me/skills", headers=headers, json={
                "skill_name": off,
                "skill_type": "OFFER",
                "proficiency": 5
            })

        for wnt in wants:
            client.post("/api/profile/me/skills", headers=headers, json={
                "skill_name": wnt,
                "skill_type": "WANT",
                "proficiency": 4
            })

        return {
            "id": user_id,
            "email": email,
            "token": token,
            "headers": headers,
            "name": name
        }

    # 1. Register User A: Offers Python, Wants Figma
    user_a = create_user("Student A", offers=["Python"], wants=["Figma"])

    # 2. Register Candidate 1 (Perfect Match): Offers Figma, Wants Python
    cand_1 = create_user("Candidate Perfect", offers=["Figma"], wants=["Python"])

    # 3. Register Candidate 2 (One-Way Match): Offers Figma, Wants Spanish
    cand_2 = create_user("Candidate OneWay", offers=["Figma"], wants=["Spanish"])

    # 4. Register Candidate 3 (No Overlap): Offers Spanish, Wants Java
    cand_3 = create_user("Candidate NoOverlap", offers=["Spanish"], wants=["Java"])

    # 5. Register Candidate 4 (Test Account): is_test = True
    cand_test = create_user("Test Account", offers=["Figma"], wants=["Python"], is_test=True)

    # 6. Register Candidate 5 (Zero Skills user)
    cand_zero = create_user("Zero Skills Student", offers=[], wants=[])

    print("[OK] Test accounts registered successfully")

    # Fetch recommendations for User A
    rec_res = client.get("/api/recommendations", headers=user_a["headers"])
    assert rec_res.status_code == 200, f"Get recommendations failed: {rec_res.text}"
    recommendations = rec_res.json()
    assert isinstance(recommendations, list), "Expected list of recommendations"

    # ----------------------------------------------------
    # TEST 1: Perfect reciprocal match (Offers Python, Wants Figma vs Offers Figma, Wants Python)
    # Expected: reciprocal_score = 1.0, match_percentage = 100%
    # ----------------------------------------------------
    rec_1 = next((r for r in recommendations if r["user_id"] == cand_1["id"]), None)
    assert rec_1 is not None, "Candidate 1 (Perfect match) should be in recommendations"
    assert math.isclose(rec_1["reciprocal_score"], 1.0, abs_tol=1e-4), f"Expected 1.0, got {rec_1['reciprocal_score']}"
    assert rec_1["match_percentage"] == 100, f"Expected 100%, got {rec_1['match_percentage']}"
    assert "Figma" in rec_1["matching_wanted_skills"], "Should identify Figma as matching wanted skill"
    assert "Python" in rec_1["matching_offered_skills"], "Should identify Python as matching offered skill"
    assert any("They offer Figma" in reason for reason in rec_1["match_reasons"]), "Should explain candidate offers Figma"
    assert any("You offer Python" in reason for reason in rec_1["match_reasons"]), "Should explain user offers Python"
    print(f"[OK] TEST 1: Perfect match verified (reciprocal_score=1.0, UI=100%, Reasons={rec_1['match_reasons']})")

    # ----------------------------------------------------
    # TEST 2: One-way match (Offers Python, Wants Figma vs Offers Figma, Wants Spanish)
    # Expected: reciprocal_score = 0.5, match_percentage = 50%
    # ----------------------------------------------------
    rec_2 = next((r for r in recommendations if r["user_id"] == cand_2["id"]), None)
    assert rec_2 is not None, "Candidate 2 (One-way match) should be in recommendations"
    assert math.isclose(rec_2["reciprocal_score"], 0.5, abs_tol=1e-4), f"Expected 0.5, got {rec_2['reciprocal_score']}"
    assert rec_2["match_percentage"] == 50, f"Expected 50%, got {rec_2['match_percentage']}"
    assert "Figma" in rec_2["matching_wanted_skills"]
    assert len(rec_2["matching_offered_skills"]) == 0
    print(f"[OK] TEST 2: One-way match verified (reciprocal_score=0.5, UI=50%, Reasons={rec_2['match_reasons']})")

    # ----------------------------------------------------
    # TEST 3: No overlap (Offers Python, Wants Figma vs Offers Spanish, Wants Java)
    # Expected: reciprocal_score = 0.0, match_percentage = 0%
    # ----------------------------------------------------
    rec_3 = next((r for r in recommendations if r["user_id"] == cand_3["id"]), None)
    assert rec_3 is not None, "Candidate 3 (No overlap) should be in recommendations"
    assert math.isclose(rec_3["reciprocal_score"], 0.0, abs_tol=1e-4), f"Expected 0.0, got {rec_3['reciprocal_score']}"
    assert rec_3["match_percentage"] == 0, f"Expected 0%, got {rec_3['match_percentage']}"
    print(f"[OK] TEST 3: No overlap verified (reciprocal_score=0.0, UI=0%)")

    # ----------------------------------------------------
    # TEST 4: User with no skills (Empty skills safety & profile readiness)
    # ----------------------------------------------------
    rec_zero_res = client.get("/api/recommendations", headers=cand_zero["headers"])
    assert rec_zero_res.status_code == 200, "Should not crash for user with 0 skills"
    zero_skills_res = client.get("/api/profile/me/skills", headers=cand_zero["headers"])
    assert zero_skills_res.status_code == 200
    assert len(zero_skills_res.json()) == 0, "Zero-skills user has 0 skills"
    print("[OK] TEST 4: Zero-skills user query succeeds without crash; readiness condition works cleanly")

    # ----------------------------------------------------
    # TEST 5: Authenticated user never appears in their own recommendations
    # ----------------------------------------------------
    assert not any(r["user_id"] == user_a["id"] for r in recommendations), "Authenticated user MUST NEVER appear in recommendations"
    print("[OK] TEST 5: Authenticated user strictly excluded from own recommendations")

    # ----------------------------------------------------
    # TEST 6: is_test = True profiles never appear
    # ----------------------------------------------------
    assert not any(r["user_id"] == cand_test["id"] for r in recommendations), "Test account MUST NEVER appear in recommendations"
    print("[OK] TEST 6: Test account (is_test=True) strictly excluded from recommendations")

    # ----------------------------------------------------
    # TEST 7: Demo profiles can appear
    # ----------------------------------------------------
    demo_cands = [r for r in recommendations if r.get("is_demo")]
    assert len(demo_cands) >= 3, f"Expected demo profiles in recommendations, found {len(demo_cands)}"
    print(f"[OK] TEST 7: Demo profiles can appear in recommendations (found {len(demo_cands)})")

    # ----------------------------------------------------
    # TEST 8: Real PostgreSQL users can appear
    # ----------------------------------------------------
    real_cands = [r for r in recommendations if not r.get("is_demo") and not r.get("is_test")]
    assert len(real_cands) >= 3, f"Expected real candidate users, found {len(real_cands)}"
    print(f"[OK] TEST 8: Real PostgreSQL registered users appear in recommendations (found {len(real_cands)})")

    # Cleanup created test accounts
    for u in [user_a, cand_1, cand_2, cand_3, cand_test, cand_zero]:
        client.delete("/api/auth/account", headers=u["headers"])
    print("[OK] Cleaned up temporary test accounts")

    print("\nALL 8 STAGE 5B TEST SCENARIOS PASSED WITH 100% COMPLIANCE!")

if __name__ == "__main__":
    run_tests()
