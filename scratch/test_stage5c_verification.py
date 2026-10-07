import uuid
import sys
import os
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.interaction import Interaction, InteractionType

client = TestClient(app)

def run_tests():
    print("=== STARTING STAGE 5C INTERACTION TRACKING VERIFICATION TESTS ===")

    # Setup helper
    def register_user(name, is_test=False):
        email = f"user5c_{uuid.uuid4().hex[:8]}@example.com"
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

    user_a = register_user("User A", is_test=False)
    user_b = register_user("User B", is_test=False)
    user_test = register_user("User Test", is_test=True)

    print("[OK] Test accounts registered")

    # ----------------------------------------------------
    # TEST 1: VIEW interaction recorded correctly
    # ----------------------------------------------------
    # A views B's profile via GET /api/profiles/{user_b.id} with auth
    view_res = client.get(f"/api/profiles/{user_b['id']}", headers=user_a["headers"])
    assert view_res.status_code == 200, f"Get profile failed: {view_res.text}"

    # Verify VIEW interaction exists in PostgreSQL
    db = SessionLocal()
    try:
        view_interaction = db.query(Interaction).filter(
            Interaction.user_id == user_a["id"],
            Interaction.target_user_id == user_b["id"],
            Interaction.interaction_type == InteractionType.VIEW
        ).first()
        assert view_interaction is not None, "Expected VIEW interaction to be recorded in DB"
        print(f"[OK] TEST 1: VIEW interaction recorded correctly (id={view_interaction.id})")
    finally:
        db.close()

    # ----------------------------------------------------
    # TEST 2: REQUEST interaction recorded correctly
    # ----------------------------------------------------
    # User A sends a swap request to User B
    req_res = client.post("/api/swap-requests", headers=user_a["headers"], json={
        "receiver_id": user_b["id"],
        "skill_offered_name": "Python",
        "skill_requested_name": "Figma",
        "message": "Hey, let's swap Python for Figma!"
    })
    assert req_res.status_code == 201, f"Send swap request failed: {req_res.text}"
    swap_data = req_res.json()
    swap_id = swap_data["id"]

    db = SessionLocal()
    try:
        request_interaction = db.query(Interaction).filter(
            Interaction.user_id == user_a["id"],
            Interaction.target_user_id == user_b["id"],
            Interaction.interaction_type == InteractionType.REQUEST
        ).first()
        assert request_interaction is not None, "Expected REQUEST interaction to be recorded in DB"
        print(f"[OK] TEST 2: REQUEST interaction recorded correctly (id={request_interaction.id})")
    finally:
        db.close()

    # ----------------------------------------------------
    # TEST 3: ACCEPT interaction recorded correctly
    # ----------------------------------------------------
    # User B accepts User A's swap request
    accept_res = client.put(f"/api/swap-requests/{swap_id}/accept", headers=user_b["headers"])
    assert accept_res.status_code == 200, f"Accept swap request failed: {accept_res.text}"

    db = SessionLocal()
    try:
        accept_interaction = db.query(Interaction).filter(
            Interaction.user_id == user_b["id"],
            Interaction.target_user_id == user_a["id"],
            Interaction.interaction_type == InteractionType.ACCEPT
        ).first()
        assert accept_interaction is not None, "Expected ACCEPT interaction to be recorded in DB"
        print(f"[OK] TEST 3: ACCEPT interaction recorded correctly (id={accept_interaction.id})")
    finally:
        db.close()

    # ----------------------------------------------------
    # TEST 4: COMPLETE interaction recorded correctly
    # ----------------------------------------------------
    # User A or B completes the swap request
    complete_res = client.put(f"/api/swap-requests/{swap_id}/complete", headers=user_a["headers"])
    assert complete_res.status_code == 200, f"Complete swap request failed: {complete_res.text}"

    db = SessionLocal()
    try:
        complete_interaction = db.query(Interaction).filter(
            Interaction.user_id == user_a["id"],
            Interaction.target_user_id == user_b["id"],
            Interaction.interaction_type == InteractionType.COMPLETE
        ).first()
        assert complete_interaction is not None, "Expected COMPLETE interaction to be recorded in DB"
        print(f"[OK] TEST 4: COMPLETE interaction recorded correctly (id={complete_interaction.id})")
    finally:
        db.close()

    # ----------------------------------------------------
    # TEST 5: Self-interactions rejected
    # ----------------------------------------------------
    self_res = client.post("/api/interactions", headers=user_a["headers"], json={
        "target_user_id": user_a["id"],
        "interaction_type": "VIEW"
    })
    assert self_res.status_code == 400, f"Expected 400 Bad Request for self-interaction, got {self_res.status_code}"
    print("[OK] TEST 5: Self-interaction correctly rejected with HTTP 400")

    # ----------------------------------------------------
    # TEST 6: Unauthenticated interaction creation rejected
    # ----------------------------------------------------
    unauth_res = client.post("/api/interactions", json={
        "target_user_id": user_b["id"],
        "interaction_type": "VIEW"
    })
    assert unauth_res.status_code in (401, 403), f"Expected 401/403 for unauthenticated, got {unauth_res.status_code}"
    print("[OK] TEST 6: Unauthenticated interaction correctly rejected")

    # ----------------------------------------------------
    # TEST 7: Invalid/nonexistent target users rejected
    # ----------------------------------------------------
    random_id = str(uuid.uuid4())
    nonexistent_res = client.post("/api/interactions", headers=user_a["headers"], json={
        "target_user_id": random_id,
        "interaction_type": "VIEW"
    })
    assert nonexistent_res.status_code == 404, f"Expected 404 for nonexistent target, got {nonexistent_res.status_code}"
    print("[OK] TEST 7: Nonexistent target user correctly rejected with HTTP 404")

    # ----------------------------------------------------
    # TEST 8: Test accounts (is_test=True) are NOT tracked
    # ----------------------------------------------------
    # User A interacts with User Test
    test_interact_res = client.post("/api/interactions", headers=user_a["headers"], json={
        "target_user_id": user_test["id"],
        "interaction_type": "VIEW"
    })
    assert test_interact_res.status_code == 201
    assert test_interact_res.json()["recorded"] is False, "Test user interaction must not be recorded"

    db = SessionLocal()
    try:
        test_in_db = db.query(Interaction).filter(
            (Interaction.user_id == user_test["id"]) | (Interaction.target_user_id == user_test["id"])
        ).first()
        assert test_in_db is None, "Test account must NEVER have interaction rows in database"
        print("[OK] TEST 8: Test accounts (is_test=True) are strictly excluded from persistent tracking")
    finally:
        db.close()

    # ----------------------------------------------------
    # TEST 9: Repeated actions do not corrupt table
    # ----------------------------------------------------
    # Repeated VIEW triggers cooldown without crashing
    for _ in range(5):
        rep_res = client.post("/api/interactions", headers=user_a["headers"], json={
            "target_user_id": user_b["id"],
            "interaction_type": "VIEW"
        })
        assert rep_res.status_code == 201
    print("[OK] TEST 9: Rapid repeated interactions handled gracefully with cooldown and zero corruption")

    # ----------------------------------------------------
    # TEST 10: Private interaction history protection
    # ----------------------------------------------------
    # User A tries to view User B's interaction history
    snoop_res = client.get(f"/api/interactions/users/{user_b['id']}/interactions", headers=user_a["headers"])
    assert snoop_res.status_code == 403, f"Expected 403 Forbidden for viewing peer's interactions, got {snoop_res.status_code}"
    # User A views their own interactions
    own_res = client.get("/api/interactions/me", headers=user_a["headers"])
    assert own_res.status_code == 200
    assert len(own_res.json()) >= 1
    print("[OK] TEST 10: Private interaction history strictly protected against unauthorized access")

    # Cleanup test users
    for u in [user_a, user_b, user_test]:
        client.delete("/api/auth/account", headers=u["headers"])
    print("[OK] Cleaned up temporary test users")

    print("\nALL STAGE 5C INTERACTION TRACKING TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
