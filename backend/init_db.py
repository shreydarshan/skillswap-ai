import sys
import os
from sqlalchemy import inspect, text

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Register all 8 ORM models in Base.metadata

REQUIRED_TABLES = [
    "users",
    "profiles",
    "skills",
    "user_skills",
    "interactions",
    "swap_requests",
    "messages",
    "ratings"
]


def init_db():
    print("=" * 60)
    print("SkillSwap AI — Database Initialization & Verification")
    print("=" * 60)

    # Sanity check for placeholder password
    if "<YOUR_POSTGRES_PASSWORD>" in settings.DATABASE_URL or "CHANGE_THIS" in settings.DATABASE_URL:
        print("[!] ERROR: Real DATABASE_URL password has not been configured in backend/.env yet.")
        print("Please edit backend/.env and replace <YOUR_POSTGRES_PASSWORD> with your local PostgreSQL password.")
        print("Example: DATABASE_URL=\"postgresql+psycopg://postgres:yourpass@localhost:5432/skillswap_db\"")
        sys.exit(1)

    print(f"Connecting to database at target database: '{settings.DATABASE_URL.split('/')[-1]}'...")

    try:
        # Test connection liveness
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version_str = result.fetchone()[0]
            print(f"[✓] Database connection established successfully!")
            print(f"    PostgreSQL Version: {version_str}")

        # Run Base.metadata.create_all(bind=engine)
        print("\nCreating / verifying SQLAlchemy ORM table schemas...")
        Base.metadata.create_all(bind=engine)

        # Inspect database tables using SQLAlchemy Inspector
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        print("\n" + "-" * 60)
        print("VERIFIED POSTGRESQL TABLES IN 'skillswap_db':")
        print("-" * 60)

        all_passed = True
        for table in REQUIRED_TABLES:
            if table in existing_tables:
                fks = inspector.get_foreign_keys(table)
                fk_names = [fk['constrained_columns'] for fk in fks]
                print(f"  [✓] Table '{table}': Created & Verified (Foreign Keys: {len(fks)})")
            else:
                print(f"  [✗] Table '{table}': MISSING")
                all_passed = False

        print("-" * 60)

        if all_passed:
            print("\n[SUCCESS] All 8 database tables created and verified successfully!")
            return True
        else:
            print("\n[!] WARNING: Some database tables were not created.")
            sys.exit(1)

    except Exception as e:
        print(f"\n[!] Database connection / initialization failed:")
        print(f"    {e}")
        print("\nPlease ensure your local PostgreSQL server is running on port 5432 and backend/.env contains valid credentials.")
        sys.exit(1)


if __name__ == "__main__":
    init_db()
