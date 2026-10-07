import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=== STARTING CONTROLLED DATA INTEGRITY & DEMO PROFILES VERIFICATION TESTS ===")
    
    # 1. Register User A (new account)
    email_a = f"test_cleanup_a_{uuid.uuid4().hex[:6]}@example.com"
    pass_a = "Password123!"
    
    reg_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email_a,
        "password": pass_a
    })
    assert reg_res.status_code in (200, 201), f"Register A failed: {reg_res.text}"
    token_a = reg_res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    print("[OK] 1. New account registration succeeded")

    # 2. Verify new account profile fields are blank and no demo avatar assigned
    prof_a_res = requests.get(f"{BASE_URL}/api/profile/me", headers=headers_a)
    assert prof_a_res.status_code == 200, f"Get Profile A failed: {prof_a_res.text}"
    prof_a = prof_a_res.json()
    
    assert prof_a.get("full_name") is None or prof_a.get("full_name") == "", f"Expected blank full_name, got {prof_a.get('full_name')}"
    assert prof_a.get("college") is None or prof_a.get("college") == "", f"Expected blank college, got {prof_a.get('college')}"
    assert prof_a.get("branch") is None or prof_a.get("branch") == "", f"Expected blank branch, got {prof_a.get('branch')}"
    assert prof_a.get("year") is None or prof_a.get("year") == "", f"Expected blank year, got {prof_a.get('year')}"
    assert prof_a.get("avatar_url") is None or prof_a.get("avatar_url") == "", f"Expected no fake avatar_url, got {prof_a.get('avatar_url')}"
    print("[OK] 2. New account starts with blank profile and no fake avatar")

    # 3. Check incomplete profile state
    is_complete_a = bool(prof_a.get("full_name") and prof_a.get("college") and prof_a.get("branch") and prof_a.get("year"))
    assert not is_complete_a, "New profile should be marked incomplete"
    print("[OK] 3. Incomplete profile status detected correctly for setup redirect")

    # 4. Gender/Avatar Preference Selection Test
    setup_res = requests.put(f"{BASE_URL}/api/profile/me", headers=headers_a, json={
        "full_name": "Cleanup User A",
        "college": "Tech University",
        "branch": "Computer Science",
        "year": 3,
        "bio": "Bio for user A",
        "location": "New York, NY",
        "availability": "Weekends",
        "gender_preference": "Female"
    })
    assert setup_res.status_code == 200, f"Setup A failed: {setup_res.text}"
    prof_a_updated = setup_res.json()
    assert prof_a_updated.get("avatar_url") and "female" in prof_a_updated["avatar_url"], f"Expected female avatar URL, got {prof_a_updated.get('avatar_url')}"
    print("[OK] 4. Female avatar preference generates deterministic female avatar URL")

    # Reset avatar to Prefer not to specify
    neutral_res = requests.put(f"{BASE_URL}/api/profile/me", headers=headers_a, json={
        "gender_preference": "Prefer not to specify"
    })
    assert neutral_res.status_code == 200
    assert neutral_res.json().get("avatar_url") is None, "Prefer not to specify should reset to neutral initials avatar (avatar_url = null)"
    print("[OK] 5. 'Prefer not to specify' resets to neutral initials avatar")

    # Add skills for User A
    requests.post(f"{BASE_URL}/api/skills/me", headers=headers_a, json={
        "skill_name": "CSS",
        "skill_type": "WANT",
        "proficiency": 3
    })
    requests.post(f"{BASE_URL}/api/skills/me", headers=headers_a, json={
        "skill_name": "Python",
        "skill_type": "OFFER",
        "proficiency": 5
    })

    # 5. Register Test User B (with is_test = True)
    email_b = f"test_cleanup_b_{uuid.uuid4().hex[:6]}@example.com"
    reg_b_res = requests.post(f"{BASE_URL}/api/auth/register", json={
        "email": email_b,
        "password": pass_a
    })
    assert reg_b_res.status_code in (200, 201), f"Register B failed: {reg_b_res.text}"
    token_b = reg_b_res.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    requests.put(f"{BASE_URL}/api/profile/me", headers=headers_b, json={
        "full_name": "Test Account B",
        "college": "State College",
        "branch": "Testing",
        "year": 2,
        "is_test": True
    })

    # 6. Test GET /api/students (Explore DB Endpoint)
    students_a_res = requests.get(f"{BASE_URL}/api/students", headers=headers_a)
    assert students_a_res.status_code == 200, f"Students query failed: {students_a_res.text}"
    students_a = students_a_res.json()
    
    # Exclude current user (User A) check
    user_a_in_students = any(s["id"] == str(prof_a["user_id"]) for s in students_a)
    assert not user_a_in_students, "Explore endpoint MUST exclude the authenticated user"
    
    # Exclude is_test=True user check
    user_b_in_students = any(s["id"] == str(reg_b_res.json()["user"]["id"]) for s in students_a)
    assert not user_b_in_students, "Test account (is_test=True) MUST be excluded from Explore/Recommendations"
    print("[OK] 6. Explore endpoint excludes authenticated user and test accounts (is_test=True)")

    # Check Demo profiles are present in PostgreSQL Explore query
    demo_names = [s["name"] for s in students_a if s.get("is_demo")]
    assert len(demo_names) >= 3, f"Expected demo profiles (Sophia Chen, Marcus Vance, Elena Rostova), found {demo_names}"
    print(f"[OK] 7. Database-driven demo profiles present in Explore ({', '.join(demo_names[:3])})")

    # 7. Test GET /api/skills/categories
    cat_res = requests.get(f"{BASE_URL}/api/skills/categories", headers=headers_a)
    assert cat_res.status_code == 200, f"Categories query failed: {cat_res.text}"
    categories = cat_res.json()
    total_count = sum(c["count"] for c in categories)
    assert total_count >= 2, f"Total skill count should reflect DB skills, got {total_count}"
    print(f"[OK] 8. Skill categories endpoint returns PostgreSQL skill counts (total = {total_count})")

    # 8. Test Messages & Unread Count APIs for User A
    msgs_res = requests.get(f"{BASE_URL}/api/messages/me", headers=headers_a)
    assert msgs_res.status_code == 200
    assert msgs_res.json() == [], "No fake messages should be returned"
    
    unread_res = requests.get(f"{BASE_URL}/api/messages/me/unread-count", headers=headers_a)
    assert unread_res.status_code == 200, f"Unread count query failed ({unread_res.status_code}): {unread_res.text}"
    assert unread_res.json()["unread_count"] == 0, "Unread count for new user should be 0"
    print("[OK] 9. Real messages & unread counts returned empty state cleanly")

    # 9. Test Account Deletion for User B
    del_b_res = requests.delete(f"{BASE_URL}/api/auth/account", headers=headers_b)
    assert del_b_res.status_code == 200, f"Account deletion failed: {del_b_res.text}"
    print("[OK] 10. Account deletion API returned 200 OK")

    # Delete User A as well
    del_a_res = requests.delete(f"{BASE_URL}/api/auth/account", headers=headers_a)
    assert del_a_res.status_code == 200
    print("[OK] 11. Account deletion for user A succeeded")

    print("\nALL 11 CONTROLLED DATA INTEGRITY & DEMO PROFILES TEST CASES PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
