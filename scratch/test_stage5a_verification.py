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
    print("=== STARTING STAGE 5A RECOMMENDATION ENGINE INTEGRATION TESTS ===")

    # 1. Register User A (Alice - offers Python, wants Figma)
    email_a = f"alice_recip_{uuid.uuid4().hex[:6]}@example.com"
    pass_a = "Password123!"

    reg_a = client.post("/api/auth/register", json={
        "email": email_a,
        "password": pass_a
    })
    assert reg_a.status_code in (200, 201), f"Register Alice failed: {reg_a.text}"
    token_a = reg_a.json()["access_token"]
    user_a_id = reg_a.json()["user"]["id"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Set profile for Alice
    client.put("/api/profile/me", headers=headers_a, json={
        "full_name": "Alice Tester",
        "college": "Stanford University",
        "branch": "Computer Science",
        "year": 3
    })

    # Add Alice's skills: offers Python, wants Figma
    res_off = client.post("/api/profile/me/skills", headers=headers_a, json={
        "skill_name": "Python",
        "skill_type": "OFFER",
        "proficiency": 5
    })
    assert res_off.status_code in (200, 201), f"Add offer failed: {res_off.text}"

    res_wnt = client.post("/api/profile/me/skills", headers=headers_a, json={
        "skill_name": "Figma",
        "skill_type": "WANT",
        "proficiency": 4
    })
    assert res_wnt.status_code in (200, 201), f"Add want failed: {res_wnt.text}"
    print("[OK] 1. Registered Alice with OFFER=['Python'] and WANT=['Figma']")

    # 2. Register User B (Test account - with is_test = True)
    email_test = f"test_user_{uuid.uuid4().hex[:6]}@example.com"
    reg_b = client.post("/api/auth/register", json={
        "email": email_test,
        "password": pass_a
    })
    token_b = reg_b.json()["access_token"]
    user_b_id = reg_b.json()["user"]["id"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    client.put("/api/profile/me", headers=headers_b, json={
        "full_name": "Test Account B",
        "college": "Test College",
        "branch": "QA",
        "year": 1,
        "is_test": True
    })
    client.post("/api/profile/me/skills", headers=headers_b, json={
        "skill_name": "Figma",
        "skill_type": "OFFER",
        "proficiency": 5
    })
    print("[OK] 2. Registered test account (is_test=True) with matching skill")

    # 3. Call GET /api/recommendations for Alice
    rec_res = client.get("/api/recommendations", headers=headers_a)
    assert rec_res.status_code == 200, f"Get recommendations failed: {rec_res.text}"
    recommendations = rec_res.json()
    assert isinstance(recommendations, list), "Expected list of recommendations"

    # Exclude self
    assert not any(r["user_id"] == user_a_id for r in recommendations), "Authenticated user MUST be excluded"
    print("[OK] 3. Authenticated user is excluded from recommendations")

    # Exclude is_test = True
    assert not any(r["user_id"] == user_b_id for r in recommendations), "Test account (is_test=True) MUST be excluded"
    print("[OK] 4. Test account (is_test=True) is strictly excluded")

    # Demo profiles present
    demo_cands = [r for r in recommendations if r.get("is_demo")]
    assert len(demo_cands) >= 3, f"Expected demo profiles in recommendations, got {len(demo_cands)}"
    print(f"[OK] 5. Demo profiles included in recommendations (found {len(demo_cands)})")

    # 4. Check reciprocal match calculation on Sophia Chen
    # Sophia Chen offers Figma (which Alice wants!) and wants Python & React.js (Alice offers Python!)
    sophia = next((r for r in recommendations if "Sophia" in r["full_name"]), None)
    assert sophia is not None, "Sophia Chen should be in candidates"

    scores = sophia["match_scores"]
    print(f"[DEBUG] Sophia match scores: forward={scores['forward_score']:.4f}, reverse={scores['reverse_score']:.4f}, reciprocal={scores['reciprocal_score']:.4f}")

    # Alice wants Figma. Sophia offers [Figma, UI/UX Design].
    # Alice_wants = [1, 0], Sophia_offers = [1, 1].
    # Cosine(Alice_wants, Sophia_offers) = 1 / (1 * sqrt(2)) = 1 / sqrt(2) ≈ 0.7071
    # Alice offers Python. Sophia wants [React.js, Python].
    # Cosine(Alice_offers, Sophia_wants) = 1 / (1 * sqrt(2)) = 1 / sqrt(2) ≈ 0.7071
    # Reciprocal = (0.7071 + 0.7071) / 2 = 0.7071
    assert scores["forward_score"] > 0.0, "Alice wants Figma, Sophia offers Figma -> forward_score should be > 0"
    assert scores["reverse_score"] > 0.0, "Alice offers Python, Sophia wants Python -> reverse_score should be > 0"
    assert scores["reciprocal_score"] > 0.5, "Strong reciprocal match expected"
    print("[OK] 6. Sophia Chen reciprocal match computed accurately")

    # 5. Check ranking: recommendations are sorted by reciprocal_score descending
    reciprocal_scores = [r["match_scores"]["reciprocal_score"] for r in recommendations]
    assert reciprocal_scores == sorted(reciprocal_scores, reverse=True), "Candidates MUST be sorted by reciprocal_score descending"
    print("[OK] 7. Candidates correctly ranked by reciprocal_score descending")

    # 6. Test specific candidate match endpoint: GET /api/recommendations/match/{candidate_id}
    cand_match_res = client.get(f"/api/recommendations/match/{sophia['user_id']}", headers=headers_a)
    assert cand_match_res.status_code == 200, f"Match query failed: {cand_match_res.text}"
    single_match_scores = cand_match_res.json()
    assert math.isclose(single_match_scores["reciprocal_score"], scores["reciprocal_score"], abs_tol=1e-4)
    print("[OK] 8. Candidate match endpoint returns matching score object")

    # 7. Test simulation endpoint: POST /api/recommendations/simulate
    sim_res = client.post("/api/recommendations/simulate", json={
        "user_a_offers": ["Python"],
        "user_a_wants": ["Figma"],
        "user_b_offers": ["Figma"],
        "user_b_wants": ["Python"]
    })
    assert sim_res.status_code == 200
    sim_scores = sim_res.json()
    assert sim_scores["forward_score"] == 1.0
    assert sim_scores["reverse_score"] == 1.0
    assert sim_scores["reciprocal_score"] == 1.0
    print("[OK] 9. Simulation endpoint calculates perfect match correctly")

    # 8. Test clean account deletion
    del_a = client.delete("/api/auth/account", headers=headers_a)
    assert del_a.status_code == 200
    del_b = client.delete("/api/auth/account", headers=headers_b)
    assert del_b.status_code == 200
    print("[OK] 10. Account deletion cleanups succeeded")

    print("\nALL 10 STAGE 5A RECOMMENDATION INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
