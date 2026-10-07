import uuid
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


CREATED_TEST_USER_IDS = []


@pytest.fixture(scope="module", autouse=True)
def cleanup_after_suite():
    yield
    from app.core.database import SessionLocal
    from app.models.user import User
    import uuid as _uuid
    db = SessionLocal()
    try:
        for uid_str in CREATED_TEST_USER_IDS:
            try:
                u = db.get(User, _uuid.UUID(str(uid_str)))
                if u:
                    db.delete(u)
            except Exception:
                pass
        db.commit()
    finally:
        db.close()


def register_user(client: TestClient, prefix: str):
    email = f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"
    full_name = f"Test Student {prefix.capitalize()}"
    res = client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": full_name, "is_test": True}
    )
    assert res.status_code == 201, res.text
    data = res.json()
    token = data["access_token"]
    user_id = data["user"]["id"]
    CREATED_TEST_USER_IDS.append(user_id)
    return {
        "email": email,
        "password": password,
        "full_name": full_name,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "user_id": user_id
    }


class TestAuthLifecycle:
    """
    Automated verification of authentication registration, login, JWT validation, and expiration.
    """

    def test_registration_and_login(self, client: TestClient):
        user = register_user(client, "auth_test")

        # Login with correct credentials
        login_res = client.post(
            "/api/auth/login",
            json={"email": user["email"], "password": user["password"]}
        )
        assert login_res.status_code == 200
        assert "access_token" in login_res.json()

        # Login with incorrect password
        bad_login = client.post(
            "/api/auth/login",
            json={"email": user["email"], "password": "WrongPassword"}
        )
        assert bad_login.status_code == 401

    def test_get_current_user_me(self, client: TestClient):
        user = register_user(client, "me_test")
        res = client.get("/api/auth/me", headers=user["headers"])
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == user["user_id"]
        assert data["email"] == user["email"]

    def test_invalid_token_rejected(self, client: TestClient):
        res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
        assert res.status_code == 401

    def test_expired_token_rejected(self, client: TestClient):
        user = register_user(client, "exp_test")
        # Create token expired 1 hour ago
        expired_token = create_access_token(
            subject=user["user_id"],
            expires_delta=timedelta(minutes=-60)
        )
        res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert res.status_code == 401


class TestAccountIsolation:
    """
    Automated verification that accounts are completely isolated:
    - User A's skills do not leak to User B
    - User A's profile updates do not affect User B
    - User A cannot delete or modify User B's skills (HTTP 403)
    """

    def test_skills_and_profile_isolation(self, client: TestClient):
        user_a = register_user(client, "user_a")
        user_b = register_user(client, "user_b")

        # User A adds skills: CSS (OFFER) and ML (WANT)
        res_a1 = client.post(
            "/api/profile/me/skills",
            headers=user_a["headers"],
            json={"skill_name": "CSS Styling", "skill_type": "OFFER", "proficiency": 4}
        )
        assert res_a1.status_code == 201
        res_a2 = client.post(
            "/api/profile/me/skills",
            headers=user_a["headers"],
            json={"skill_name": "Machine Learning", "skill_type": "WANT", "proficiency": 1}
        )
        assert res_a2.status_code == 201

        # User B adds skills: Python (OFFER) and Data Science (WANT)
        res_b1 = client.post(
            "/api/profile/me/skills",
            headers=user_b["headers"],
            json={"skill_name": "Python", "skill_type": "OFFER", "proficiency": 5}
        )
        assert res_b1.status_code == 201
        user_b_skill_id = res_b1.json()["id"]

        res_b2 = client.post(
            "/api/profile/me/skills",
            headers=user_b["headers"],
            json={"skill_name": "Data Science", "skill_type": "WANT", "proficiency": 1}
        )
        assert res_b2.status_code == 201

        # Check User A's skills: Must only have CSS Styling and Machine Learning
        a_skills = client.get("/api/profile/me/skills", headers=user_a["headers"]).json()
        a_names = [s["skill_name"] for s in a_skills]
        assert "CSS Styling" in a_names
        assert "Machine Learning" in a_names
        assert "Python" not in a_names
        assert "Data Science" not in a_names

        # Check User B's skills: Must only have Python and Data Science
        b_skills = client.get("/api/profile/me/skills", headers=user_b["headers"]).json()
        b_names = [s["skill_name"] for s in b_skills]
        assert "Python" in b_names
        assert "Data Science" in b_names
        assert "CSS Styling" not in b_names
        assert "Machine Learning" not in b_names

        # User A updates their profile
        client.put(
            "/api/profile/me",
            headers=user_a["headers"],
            json={"bio": "User A unique bio", "college": "University A"}
        )

        # User B updates their profile
        client.put(
            "/api/profile/me",
            headers=user_b["headers"],
            json={"bio": "User B unique bio", "college": "University B"}
        )

        # Verify profiles remain independent
        prof_a = client.get("/api/profile/me", headers=user_a["headers"]).json()
        prof_b = client.get("/api/profile/me", headers=user_b["headers"]).json()
        assert prof_a["bio"] == "User A unique bio"
        assert prof_b["bio"] == "User B unique bio"
        assert prof_a["college"] == "University A"
        assert prof_b["college"] == "University B"

        # User A attempts to delete User B's skill -> Must be rejected with 403 Forbidden!
        delete_attempt = client.delete(
            f"/api/profile/me/skills/{user_b_skill_id}",
            headers=user_a["headers"]
        )
        assert delete_attempt.status_code == 403

        # Verify User B's skill was not deleted
        b_skills_after = client.get("/api/profile/me/skills", headers=user_b["headers"]).json()
        b_ids = [s["id"] for s in b_skills_after]
        assert user_b_skill_id in b_ids


class TestSwapRequestSystem:
    """
    Automated verification of the complete real swap request lifecycle:
    - User A sends swap request to User B
    - Self-swap is rejected
    - Duplicate pending request is rejected
    - User B sees the request under incoming requests
    - Unauthorized users cannot accept or decline
    - User B accepts -> status becomes ACCEPTED
    - User A sees updated status as ACCEPTED
    - User B declines -> status becomes REJECTED
    """

    def test_swap_proposal_and_accept_flow(self, client: TestClient):
        user_a = register_user(client, "swap_a")
        user_b = register_user(client, "swap_b")

        # Propose swap from A to B
        req_res = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_b["user_id"],
                "skill_offered_name": "CSS",
                "skill_requested_name": "Python",
                "message": "Let's swap CSS for Python!"
            }
        )
        assert req_res.status_code == 201
        swap_data = req_res.json()
        swap_id = swap_data["id"]
        assert swap_data["status"] == "PENDING"
        assert swap_data["sender_id"] == user_a["user_id"]
        assert swap_data["receiver_id"] == user_b["user_id"]

        # Prevent duplicate pending request
        dup_res = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_b["user_id"],
                "skill_offered_name": "CSS",
                "skill_requested_name": "Python"
            }
        )
        assert dup_res.status_code == 400

        # Self-request prevention
        self_res = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_a["user_id"],
                "skill_offered_name": "CSS",
                "skill_requested_name": "Python"
            }
        )
        assert self_res.status_code == 400

        # User B inspects their swap requests
        b_swaps = client.get("/api/swap-requests/me", headers=user_b["headers"]).json()
        b_incoming = [s for s in b_swaps if s["id"] == swap_id]
        assert len(b_incoming) == 1
        assert b_incoming[0]["status"] == "PENDING"
        assert b_incoming[0]["skill_offered_name"].lower() == "css"
        assert b_incoming[0]["skill_requested_name"].lower() == "python"

        # Unauthorized user (User A trying to accept their own sent request)
        unauth_accept = client.put(f"/api/swap-requests/{swap_id}/accept", headers=user_a["headers"])
        assert unauth_accept.status_code == 403

        # User B accepts the request
        accept_res = client.put(f"/api/swap-requests/{swap_id}/accept", headers=user_b["headers"])
        assert accept_res.status_code == 200
        assert accept_res.json()["status"] == "ACCEPTED"

        # User A verifies the request is now ACCEPTED
        a_swaps = client.get("/api/swap-requests/me", headers=user_a["headers"]).json()
        a_match = [s for s in a_swaps if s["id"] == swap_id][0]
        assert a_match["status"] == "ACCEPTED"

    def test_swap_decline_flow(self, client: TestClient):
        user_c = register_user(client, "swap_c")
        user_d = register_user(client, "swap_d")

        # User C proposes swap to User D
        create_res = client.post(
            "/api/swap-requests",
            headers=user_c["headers"],
            json={
                "receiver_id": user_d["user_id"],
                "skill_offered_name": "React",
                "skill_requested_name": "Go",
                "message": "Interested in swapping?"
            }
        )
        assert create_res.status_code == 201
        swap_id = create_res.json()["id"]

        # User C (sender) cannot decline
        unauth_decline = client.put(f"/api/swap-requests/{swap_id}/decline", headers=user_c["headers"])
        assert unauth_decline.status_code == 403

        # User D (recipient) declines
        decline_res = client.put(f"/api/swap-requests/{swap_id}/decline", headers=user_d["headers"])
        assert decline_res.status_code == 200
        assert decline_res.json()["status"] == "REJECTED"

        # User C checks status: must be REJECTED (Declined)
        c_swaps = client.get("/api/swap-requests/me", headers=user_c["headers"]).json()
        c_match = [s for s in c_swaps if s["id"] == swap_id][0]
        assert c_match["status"] == "REJECTED"


class TestRealMessaging:
    """
    Automated verification of real direct messaging:
    - POST /api/messages creates a real message in PostgreSQL
    - Sender derived from authenticated JWT
    - Self-messaging rejected
    - Empty message rejected
    - Recipient receives message
    - Recipient can reply
    - Sender receives reply
    - Private messages protected from third parties (HTTP 403)
    """

    def test_message_send_and_receive_lifecycle(self, client: TestClient):
        user_a = register_user(client, "msg_a")
        user_b = register_user(client, "msg_b")
        user_c = register_user(client, "msg_c")

        # 1. User A sends message to User B
        msg_text = "Hi User B! I'd love to learn Python from you."
        send_res = client.post(
            "/api/messages",
            headers=user_a["headers"],
            json={"receiver_id": user_b["user_id"], "message": msg_text}
        )
        assert send_res.status_code == 201
        sent_data = send_res.json()
        assert sent_data["sender_id"] == user_a["user_id"]
        assert sent_data["receiver_id"] == user_b["user_id"]
        assert sent_data["message"] == msg_text

        # 2. Self-messaging rejected
        self_msg = client.post(
            "/api/messages",
            headers=user_a["headers"],
            json={"receiver_id": user_a["user_id"], "message": "Note to self"}
        )
        assert self_msg.status_code == 400

        # 3. Empty message rejected
        empty_msg = client.post(
            "/api/messages",
            headers=user_a["headers"],
            json={"receiver_id": user_b["user_id"], "message": "   "}
        )
        assert empty_msg.status_code == 400

        # 4. User B checks messages: receives User A's message
        b_msgs = client.get("/api/messages/me", headers=user_b["headers"]).json()
        b_received = [m for m in b_msgs if m["id"] == sent_data["id"]]
        assert len(b_received) == 1
        assert b_received[0]["message"] == msg_text

        # 5. User B replies to User A
        reply_text = "Sure! Let's connect this Friday afternoon."
        reply_res = client.post(
            "/api/messages",
            headers=user_b["headers"],
            json={"receiver_id": user_a["user_id"], "message": reply_text}
        )
        assert reply_res.status_code == 201

        # 6. User A checks conversation: sees both original message and User B's reply
        conv = client.get(
            f"/api/messages/conversations/{user_b['user_id']}",
            headers=user_a["headers"]
        ).json()
        assert len(conv) == 2
        assert conv[0]["message"] == msg_text
        assert conv[1]["message"] == reply_text
        assert conv[0]["sender_id"] == user_a["user_id"]
        assert conv[1]["sender_id"] == user_b["user_id"]

        # 7. Privacy protection: User C cannot access User A's private messages
        unauth_msgs = client.get(
            f"/api/users/{user_a['user_id']}/messages",
            headers=user_c["headers"]
        )
        assert unauth_msgs.status_code == 403


class TestRelationshipLifecycle:
    """
    Automated verification of relationship lifecycle:
    NO_RELATIONSHIP -> PENDING -> CONNECTED
    and prevention of duplicate active swap requests.
    """

    def test_relationship_lifecycle_and_duplicate_prevention(self, client: TestClient):
        user_a = register_user(client, "rel_a")
        user_b = register_user(client, "rel_b")

        # 1. Initially NO_RELATIONSHIP
        rel_init = client.get(
            f"/api/swap-requests/relationship/{user_b['user_id']}",
            headers=user_a["headers"]
        ).json()
        assert rel_init["status"] == "NO_RELATIONSHIP"
        assert rel_init["is_connected"] is False
        assert rel_init["is_pending"] is False

        # 2. User A sends swap request to User B
        swap_res = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_b["user_id"],
                "skill_offered_name": "Python",
                "skill_requested_name": "React.js",
                "message": "Let's swap!"
            }
        )
        assert swap_res.status_code == 201
        swap_id = swap_res.json()["id"]

        # 3. Both see PENDING status
        rel_a = client.get(
            f"/api/swap-requests/relationship/{user_b['user_id']}",
            headers=user_a["headers"]
        ).json()
        assert rel_a["status"] == "PENDING"
        assert rel_a["is_pending"] is True
        assert rel_a["direction"] == "OUTGOING"

        rel_b = client.get(
            f"/api/swap-requests/relationship/{user_a['user_id']}",
            headers=user_b["headers"]
        ).json()
        assert rel_b["status"] == "PENDING"
        assert rel_b["is_pending"] is True
        assert rel_b["direction"] == "INCOMING"

        # 4. User A trying to send second swap request to User B is rejected
        dup_a = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_b["user_id"],
                "skill_offered_name": "Python",
                "skill_requested_name": "React.js"
            }
        )
        assert dup_a.status_code == 400
        assert "pending swap request already exists" in dup_a.json()["detail"].lower()

        # 5. User B trying to send swap request back to User A while pending is rejected
        dup_b = client.post(
            "/api/swap-requests",
            headers=user_b["headers"],
            json={
                "receiver_id": user_a["user_id"],
                "skill_offered_name": "React.js",
                "skill_requested_name": "Python"
            }
        )
        assert dup_b.status_code == 400
        assert "pending swap request already exists" in dup_b.json()["detail"].lower()

        # 6. User B accepts swap request
        accept_res = client.put(
            f"/api/swap-requests/{swap_id}/accept",
            headers=user_b["headers"]
        )
        assert accept_res.status_code == 200

        # 7. Both users see CONNECTED status
        conn_a = client.get(
            f"/api/swap-requests/relationship/{user_b['user_id']}",
            headers=user_a["headers"]
        ).json()
        assert conn_a["status"] == "CONNECTED"
        assert conn_a["is_connected"] is True
        assert conn_a["is_pending"] is False

        conn_b = client.get(
            f"/api/swap-requests/relationship/{user_a['user_id']}",
            headers=user_b["headers"]
        ).json()
        assert conn_b["status"] == "CONNECTED"
        assert conn_b["is_connected"] is True
        assert conn_b["is_pending"] is False

        # 8. While connected, sending another swap request is rejected
        conn_dup = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_b["user_id"],
                "skill_offered_name": "Python",
                "skill_requested_name": "React.js"
            }
        )
        assert conn_dup.status_code == 400
        assert "already connected" in conn_dup.json()["detail"].lower()

        # 9. Complete swap flow
        complete_res = client.put(
            f"/api/swap-requests/{swap_id}/complete",
            headers=user_a["headers"]
        )
        assert complete_res.status_code == 200
        assert complete_res.json()["status"] == "COMPLETED"

        # 10. Both users see COMPLETED status
        comp_a = client.get(
            f"/api/swap-requests/relationship/{user_b['user_id']}",
            headers=user_a["headers"]
        ).json()
        assert comp_a["status"] == "COMPLETED"
        assert comp_a["is_connected"] is False

        comp_b = client.get(
            f"/api/swap-requests/relationship/{user_a['user_id']}",
            headers=user_b["headers"]
        ).json()
        assert comp_b["status"] == "COMPLETED"
        assert comp_b["is_connected"] is False

        # 11. After completion, a new swap proposal can be initiated
        new_swap_res = client.post(
            "/api/swap-requests",
            headers=user_a["headers"],
            json={
                "receiver_id": user_b["user_id"],
                "skill_offered_name": "Python",
                "skill_requested_name": "React.js",
                "message": "Let's do another session!"
            }
        )
        assert new_swap_res.status_code == 201


class TestDataIntegrityAndSeeding:
    """
    Automated verification of test-user exclusion, recommendation deduplication,
    and idempotent seeding.
    """

    def test_test_users_excluded_from_public_listings(self, client: TestClient):
        # Register a test student with skills
        test_student = register_user(client, "test_excl")
        client.post(
            "/api/profile/me/skills",
            headers=test_student["headers"],
            json={"skill_name": "Python", "skill_type": "OFFER", "proficiency": 5}
        )

        # Authenticate a regular student
        viewer = register_user(client, "viewer")

        # 1. Explore students must NOT include test_student
        explore_res = client.get("/api/students", headers=viewer["headers"]).json()
        explore_ids = [s["id"] for s in explore_res]
        assert test_student["user_id"] not in explore_ids
        for s in explore_res:
            assert s.get("is_test") is not True

        # 2. Recommendations must NOT include test_student
        rec_res = client.get("/api/recommendations/hybrid", headers=viewer["headers"]).json()
        rec_ids = [r["candidate_id"] for r in rec_res]
        assert test_student["user_id"] not in rec_ids

        # 3. Deduplication check: each candidate ID appears at most once in recommendations
        assert len(rec_ids) == len(set(rec_ids)), "Duplicate candidate IDs returned in recommendations!"

    def test_idempotent_demo_seeding(self):
        from app.core.database import SessionLocal
        from app.models.profile import Profile
        from app.core.seed_demo_data import seed_demo_profiles
        db = SessionLocal()
        try:
            # First seed call
            seed_demo_profiles(db)
            demo_count_1 = len(db.query(Profile).filter(Profile.is_demo == True).all())

            # Second seed call (must be completely idempotent)
            seed_demo_profiles(db)
            demo_count_2 = len(db.query(Profile).filter(Profile.is_demo == True).all())

            assert demo_count_1 == demo_count_2 == 5, f"Expected exactly 5 demo profiles, got {demo_count_2}"
        finally:
            db.close()
