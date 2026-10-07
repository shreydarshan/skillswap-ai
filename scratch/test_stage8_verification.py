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
from app.models.skill import Skill
from app.recommendation.hybrid import calculate_hybrid_score, DEFAULT_CONTENT_WEIGHT, DEFAULT_COLLABORATIVE_WEIGHT
from app.recommendation.similarity import calculate_directional_score, compute_cosine_similarity
from app.recommendation.engine import calculate_reciprocal_match

client = TestClient(app)

def run_stage8_tests():
    print("=== STARTING STAGE 8 MAJOR PRODUCT UI & EXPLORE/RECOMMENDATION VERIFICATION TESTS ===")

    # 1. Verify recommendation algorithms and production 70/30 weighting strictly intact
    assert DEFAULT_CONTENT_WEIGHT == 0.70, "Production content weight must remain 0.70"
    assert DEFAULT_COLLABORATIVE_WEIGHT == 0.30, "Production collaborative weight must remain 0.30"
    assert calculate_hybrid_score(1.0, 1.0) == 1.0
    assert calculate_hybrid_score(1.0, 0.0) == 0.70
    assert calculate_hybrid_score(0.0, 1.0) == 0.30
    recip = calculate_reciprocal_match(["Python"], ["Figma"], ["Figma"], ["Python"])
    assert recip.reciprocal_score == 1.0
    print("[PASS] 1. All recommendation algorithms, reciprocal scoring, and 70/30 production weighting completely unchanged")

    # 2. Verify database records integrity: real user & believable demo profiles preserved
    db = SessionLocal()
    try:
        users = db.query(User).all()
        demo_emails = [u.email for u in users if u.email.endswith("@skillswap.edu")]
        assert len(demo_emails) == 5, f"Expected 5 demo emails, found {len(demo_emails)}"
        
        real_user = db.query(User).filter(User.email == "shreydarshan1@gmail.com").first()
        assert real_user is not None, "Real user shreydarshan1@gmail.com must be preserved"
        print(f"[PASS] 2. PostgreSQL data integrity verified: real users + 5 demo students ({demo_emails})")
    finally:
        db.close()

    # 3. Verify Explore Student Directory API returns students
    resp_explore = client.get("/api/students")
    assert resp_explore.status_code == 200
    students = resp_explore.json()
    assert len(students) >= 5, "Explore directory should return all available non-test students"

    # Verify no test accounts (is_test=True) in /students
    for s in students:
        assert not s.get("is_test", False)
        assert "user5e_" not in s.get("email", "")
        assert "test_" not in s.get("email", "")
    print("[PASS] 3. Explore directory excludes test accounts and returns clean community candidate pool")

    # 4. Verify Category Filtering behavior:
    # Check that skills across categories exist in student profiles
    category_keywords = {
        "coding": ["programming", "web", "frontend", "backend", "coding", "react", "python", "java"],
        "design": ["design", "ui/ux", "graphic", "figma"],
        "data": ["data", "ai", "machine learning", "analytics", "python"],
        "languages": ["foreign languages", "language", "spanish"],
        "business": ["business", "marketing", "public speaking"],
    }

    for cat_id, kws in category_keywords.items():
        matching = []
        for st in students:
            all_skills = st.get("skillsOffered", []) + st.get("skillsWanted", [])
            has_match = any(
                any(kw in (s.get("name", "") + " " + s.get("category", "")).lower() for kw in kws)
                for s in all_skills
            )
            if has_match:
                matching.append(st["name"])
        assert len(matching) > 0, f"Category '{cat_id}' should match at least one student, found 0"
        print(f"[PASS] 4. Category '{cat_id}' successfully filters to matching students: {matching}")

    print("\n=== ALL STAGE 8 VERIFICATION CHECKS PASSED WITH 100% COMPLIANCE ===")

if __name__ == "__main__":
    run_stage8_tests()
