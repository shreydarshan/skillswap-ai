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
    DEFAULT_CONTENT_WEIGHT,
    DEFAULT_COLLABORATIVE_WEIGHT,
)

client = TestClient(app)


def run_stage7_tests():
    print("=== STARTING STAGE 7 PRODUCT UX & REFINEMENT VERIFICATION TESTS ===")

    # 1. Verify algorithms & weights intact
    assert DEFAULT_CONTENT_WEIGHT == 0.70
    assert DEFAULT_COLLABORATIVE_WEIGHT == 0.30
    print("[PASS] 1. Production 70/30 weighting and hybrid configuration completely intact")

    # 2. Verify database demo profiles preserved
    db = SessionLocal()
    try:
        demo_profiles = db.query(Profile).filter(Profile.is_demo == True).all()
        demo_names = [p.full_name for p in demo_profiles]
        for expected in ["Sophia Chen", "Marcus Vance", "Elena Rostova", "Alex Rivera", "Sarah Jenkins"]:
            assert expected in demo_names, f"Expected demo profile {expected} missing!"
        print(f"[PASS] 2. Believable demo profiles preserved ({len(demo_names)} verified: {demo_names})")

        # Verify real registered user preserved
        real_user = db.query(User).filter(User.email == "shreydarshan1@gmail.com").first()
        assert real_user is not None, "Real user shreydarshan1@gmail.com must be preserved"
        print("[PASS] 3. Real registered user account preserved")
    finally:
        db.close()

    # 3. Test Student Explore API — Returns all available students without requiring match score > 0
    resp_students = client.get("/api/students")
    assert resp_students.status_code == 200
    students_list = resp_students.json()
    assert len(students_list) >= 5, "Explore should return campus student community"

    # Verify no test accounts (is_test=True) in /students
    for s in students_list:
        assert not s.get("is_test", False)
        assert "user5e_" not in s.get("email", "")
        assert "test_" not in s.get("email", "")
    print("[PASS] 4. Explore student directory excludes test accounts and development artifacts")

    # 4. Avatar generation behavior: female vs male distinct styles
    # Register temporary user
    reg = client.post("/api/auth/register", json={
        "email": "stage7_avatar_test@example.com",
        "password": "Password123!"
    })
    data = reg.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Female Preference
    res_fem = client.put("/api/profile/me", headers=headers, json={
        "full_name": "Test Female Student",
        "gender_preference": "Female"
    })
    assert res_fem.status_code == 200
    fem_avatar = res_fem.json()["avatar_url"]
    assert "gender=female" in fem_avatar
    assert "top=" in fem_avatar, "Female avatar must have top hairstyle styling"

    # Test Male Preference
    res_male = client.put("/api/profile/me", headers=headers, json={
        "full_name": "Test Male Student",
        "gender_preference": "Male"
    })
    assert res_male.status_code == 200
    male_avatar = res_male.json()["avatar_url"]
    assert "gender=male" in male_avatar
    assert "facialHairProbability" in male_avatar, "Male avatar must have male hairstyle/beard styling"

    # Test Neutral/Prefer not to specify
    res_neutral = client.put("/api/profile/me", headers=headers, json={
        "gender_preference": "Prefer not to specify"
    })
    assert res_neutral.status_code == 200
    assert res_neutral.json()["avatar_url"] is None, "Prefer not to specify resets to neutral initials"

    # Cleanup temporary user
    client.delete("/api/auth/account", headers=headers)
    print("[PASS] 5. Deterministic avatar generation verified: Female, Male, and Neutral initials")

    print("\n=== ALL STAGE 7 VERIFICATION CHECKS PASSED WITH 100% COMPLIANCE ===")


if __name__ == "__main__":
    run_stage7_tests()
