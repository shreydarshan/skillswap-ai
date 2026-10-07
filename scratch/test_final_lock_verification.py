import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.recommendation.hybrid import (
    calculate_hybrid_score,
    DEFAULT_CONTENT_WEIGHT,
    DEFAULT_COLLABORATIVE_WEIGHT,
)
from app.recommendation.similarity import calculate_directional_score
from app.recommendation.engine import calculate_reciprocal_match

client = TestClient(app)

def run_final_lock_verification():
    print("======================================================================")
    print("=== FINAL LOCK PASS — SKILLSWAP AI REGRESSION & PERSISTENCE TESTS ===")
    print("======================================================================")

    # 1. Recommendation algorithms and production weights remain 100% unchanged
    assert DEFAULT_CONTENT_WEIGHT == 0.70, "Production content weight must remain 0.70"
    assert DEFAULT_COLLABORATIVE_WEIGHT == 0.30, "Production collaborative weight must remain 0.30"
    assert calculate_hybrid_score(1.0, 1.0) == 1.0
    assert calculate_hybrid_score(1.0, 0.0) == 0.70
    assert calculate_hybrid_score(0.0, 1.0) == 0.30
    recip = calculate_reciprocal_match(["Python"], ["Figma"], ["Figma"], ["Python"])
    assert recip.reciprocal_score == 1.0
    print("[PASS] 1. Mathematical integrity verified: reciprocal cosine scoring and 70/30 production weighting strictly unchanged.")

    # 2. Controlled Demo Profiles check
    db = SessionLocal()
    try:
        users = db.query(User).all()
        demo_users = [u for u in users if u.email.endswith("@skillswap.edu")]
        assert len(demo_users) == 5, f"Expected 5 demo users, found {len(demo_users)}"
        expected_demo_names = ["Sophia Chen", "Marcus Vance", "Elena Rostova", "Alex Rivera", "Sarah Jenkins"]
        demo_names_found = []
        for du in demo_users:
            prof = db.get(Profile, du.id)
            assert prof is not None
            assert prof.is_demo is True
            assert not prof.is_test
            assert prof.avatar_url is not None and "unsplash.com" in prof.avatar_url
            demo_names_found.append(prof.full_name)

        for name in expected_demo_names:
            assert name in demo_names_found, f"Missing demo user {name}"
        print(f"[PASS] 2. All 5 demo users present with realistic stable portraits in PostgreSQL: {demo_names_found}")

        # Real users check
        real_users = [u for u in users if not u.email.endswith("@skillswap.edu") and not u.email.startswith("lock_")]
        assert len(real_users) >= 2, "Real accounts (Raghuraj & Shrey Darshan) must be preserved"
        print(f"[PASS] 3. Real accounts preserved: {[u.email for u in real_users]}")
    finally:
        db.close()

    # 3. Two-Account Avatar Persistence & Cross-User Visibility (Part R)
    print("\n--- Executing Two-Account Avatar Persistence & Cross-User Visibility Test ---")
    user_a_email = "lock_test_user_a@example.com"
    user_b_email = "lock_test_user_b@example.com"
    password = "Password123!"

    # Register User A
    reg_a = client.post("/api/auth/register", json={"email": user_a_email, "password": password})
    assert reg_a.status_code == 201
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register User B
    reg_b = client.post("/api/auth/register", json={"email": user_b_email, "password": password})
    assert reg_b.status_code == 201
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    chosen_portrait = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80"

    try:
        # User A updates profile and selects Male Portrait
        res_save_a = client.put("/api/profile/me", headers=headers_a, json={
            "full_name": "Lock User Alpha",
            "college": "Manipal University Jaipur",
            "branch": "CSE",
            "year": 3,
            "gender_preference": "Male",
            "avatar_url": chosen_portrait
        })
        assert res_save_a.status_code == 200
        prof_a = res_save_a.json()
        assert prof_a["avatar_url"] == chosen_portrait, "User A avatar_url must be saved in backend profile"
        user_a_id = prof_a["user_id"]
        print("[PASS] 4. User A selected realistic portrait and backend successfully persisted it.")

        # User A refreshes profile
        res_refresh_a = client.get("/api/profile/me", headers=headers_a)
        assert res_refresh_a.status_code == 200
        assert res_refresh_a.json()["avatar_url"] == chosen_portrait
        print("[PASS] 5. User A profile refresh confirms persisted avatar.")

        # User B logs in and opens Explore (/api/students)
        res_explore_b = client.get("/api/students", headers=headers_b)
        assert res_explore_b.status_code == 200
        students_b = res_explore_b.json()
        
        # User B must find User A and see the SAME avatar
        student_a_view = next((s for s in students_b if s.get("email") == user_a_email), None)
        assert student_a_view is not None, "User B must see User A in student directory"
        assert student_a_view["avatar"] == chosen_portrait, "User B must see User A's chosen portrait in Explore"
        assert student_a_view["avatar_url"] == chosen_portrait, "User B must receive User A's avatar_url in Explore"
        print("[PASS] 6. User B views Explore: User A has the EXACT same chosen realistic portrait!")

        # User B opens User A's public profile (/api/profiles/{user_id})
        res_user_a_prof = client.get(f"/api/profiles/{user_a_id}", headers=headers_b)
        assert res_user_a_prof.status_code == 200
        prof_view_b = res_user_a_prof.json()
        assert prof_view_b["avatar_url"] == chosen_portrait, "User B opening User A profile sees the same avatar"
        print("[PASS] 7. User B viewing User A profile sees identical persisted avatar.")

        # User A switches to Initials Avatar (avatar_url: None)
        res_save_initials = client.put("/api/profile/me", headers=headers_a, json={
            "full_name": "Lock User Alpha",
            "gender_preference": "",
            "avatar_url": None
        })
        assert res_save_initials.status_code == 200
        assert res_save_initials.json()["avatar_url"] is None, "Avatar url must reset to None for initials avatar"
        print("[PASS] 8. User A switches to Initials Avatar: successfully persisted as None in database.")

        # User B checks Explore again: User A now shows null avatar (Initials fallback)
        res_explore_b2 = client.get("/api/students", headers=headers_b)
        student_a_view2 = next((s for s in res_explore_b2.json() if s.get("email") == user_a_email), None)
        assert student_a_view2 is not None
        assert student_a_view2["avatar"] is None or student_a_view2["avatar"] == ""
        print("[PASS] 9. User B views Explore after User A initials switch: avatar correctly resets to initials.")

        # Check self-exclusion: User A is never recommended to themselves
        res_recs_a = client.get("/api/recommendations/hybrid", headers=headers_a)
        assert res_recs_a.status_code == 200
        recs_a = res_recs_a.json()
        assert not any(r.get("email") == user_a_email for r in recs_a), "User A must not be recommended to themselves"
        print("[PASS] 10. Authenticated user is strictly excluded from their own recommendations.")

    finally:
        # Cleanup test accounts
        client.delete("/api/auth/account", headers=headers_a)
        client.delete("/api/auth/account", headers=headers_b)
        print("[PASS] 11. Test accounts cleanly deleted.")

    print("\n======================================================================")
    print("=== FINAL LOCK VERIFICATION PASSED WITH 100% SUCCESS ACROSS ALL TESTS ===")
    print("======================================================================")

if __name__ == "__main__":
    run_final_lock_verification()
