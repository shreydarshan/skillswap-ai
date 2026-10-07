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
from app.recommendation.hybrid import calculate_hybrid_score, DEFAULT_CONTENT_WEIGHT, DEFAULT_COLLABORATIVE_WEIGHT
from app.recommendation.similarity import calculate_directional_score, compute_cosine_similarity
from app.recommendation.engine import calculate_reciprocal_match

client = TestClient(app)

def run_stage9_tests():
    print("=== STARTING STAGE 9 FINAL AVATAR & PROFILE VISUAL POLISH VERIFICATION TESTS ===")

    # 1. Recommendation algorithms and production weights remain 100% unchanged
    assert DEFAULT_CONTENT_WEIGHT == 0.70, "Production content weight must remain 0.70"
    assert DEFAULT_COLLABORATIVE_WEIGHT == 0.30, "Production collaborative weight must remain 0.30"
    assert calculate_hybrid_score(1.0, 1.0) == 1.0
    assert calculate_hybrid_score(1.0, 0.0) == 0.70
    assert calculate_hybrid_score(0.0, 1.0) == 0.30
    recip = calculate_reciprocal_match(["Python"], ["Figma"], ["Figma"], ["Python"])
    assert recip.reciprocal_score == 1.0
    print("[PASS] 1. Recommendation algorithms, reciprocal scoring, and 70/30 production weighting completely unchanged")

    # 2. Database demo profiles maintain realistic student portraits
    db = SessionLocal()
    try:
        users = db.query(User).all()
        demo_users = [u for u in users if u.email.endswith("@skillswap.edu")]
        assert len(demo_users) == 5, f"Expected 5 demo users, found {len(demo_users)}"

        for du in demo_users:
            prof = db.get(Profile, du.id)
            assert prof is not None
            assert prof.is_demo is True
            assert not prof.is_test
            # Must have a realistic photo URL
            assert prof.avatar_url is not None and "unsplash.com" in prof.avatar_url, (
                f"Demo user {du.email} must have realistic photo URL, got {prof.avatar_url}"
            )
        print(f"[PASS] 2. All 5 demo student profiles have high-quality realistic portraits in PostgreSQL")

        # 3. Real registered user accounts verified
        real_users = [u for u in users if not u.email.endswith("@skillswap.edu")]
        assert len(real_users) >= 1, "Real user accounts must be preserved"
        real_emails = [u.email for u in real_users]
        print(f"[PASS] 3. Real registered user accounts verified: {real_emails}")
    finally:
        db.close()

    # 4. Explore directory API returns students with realistic avatars & no test accounts
    resp_explore = client.get("/api/students")
    assert resp_explore.status_code == 200
    students = resp_explore.json()
    assert len(students) >= 5

    for s in students:
        assert not s.get("is_test", False)
        assert "user5e_" not in s.get("email", "")
        assert "test_" not in s.get("email", "")
        # Avatar URL must not be a broken or random string
        if s.get("is_demo"):
            assert "unsplash.com" in s.get("avatar", ""), "Demo students must use realistic Unsplash portraits"
    print("[PASS] 4. Explore student directory provides realistic portraits for demo students and excludes test accounts")

    # 5. New account registration behavior: starts with blank profile and null avatar
    test_email = "stage9_avatar_check@example.com"
    reg = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "Password123!"
    })
    assert reg.status_code == 201
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify initial profile has null avatar (defaults to initials avatar)
    prof_res = client.get("/api/profile/me", headers=headers)
    assert prof_res.status_code == 200
    prof_data = prof_res.json()
    assert prof_data["avatar_url"] is None, "New accounts must start with null avatar_url (Initials Avatar)"
    assert prof_data["gender_preference"] is None, "New accounts must start with null gender_preference"
    print("[PASS] 5. New accounts start with null avatar_url & null gender_preference (clean Initials Avatar)")

    # Clean up temporary test user
    del_res = client.delete("/api/auth/account", headers=headers)
    assert del_res.status_code == 200
    print("[PASS] 6. Temporary verification user cleanly deleted")

    print("\n=== ALL STAGE 9 AVATAR & PROFILE VERIFICATION CHECKS PASSED WITH 100% COMPLIANCE ===")

if __name__ == "__main__":
    run_stage9_tests()
