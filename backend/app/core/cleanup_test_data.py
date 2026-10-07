"""
Database Maintenance Utility
Safely removes transient test accounts while preserving genuine student profiles and controlled demo accounts.
"""
from app.core.database import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.core.seed_demo_data import DEMO_STUDENTS, seed_demo_profiles


def cleanup_test_accounts():
    db = SessionLocal()
    try:
        demo_emails = {d["email"].lower() for d in DEMO_STUDENTS}
        legitimate_emails = {"shreydarshan1@gmail.com", "alpha_71b092@campus.edu", "beta_73a30e@campus.edu"}

        users = db.query(User).all()
        deleted_count = 0

        for u in users:
            email = u.email.lower()
            p = u.profile
            name = p.full_name if p else ""

            # Check if this is a legitimate user or demo account
            if (
                email in demo_emails
                or email in legitimate_emails
                or "raghuraj" in email
                or "raghuraj" in name.lower()
                or (p and p.is_demo and not p.is_test)
            ):
                continue

            # Identify test accounts
            if (
                email.endswith("@example.com")
                or name.lower().startswith("test student")
                or (p and p.is_test)
            ):
                db.delete(u)
                deleted_count += 1

        db.commit()
        print(f"Safely purged {deleted_count} transient test accounts.")

        # Re-ensure demo accounts are properly seeded and idempotent
        seed_demo_profiles(db)
        print("Ensured demo profiles are idempotent and up-to-date.")
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_test_accounts()
