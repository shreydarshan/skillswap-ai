from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import (
    health,
    auth,
    users,
    profiles,
    skills,
    user_skills,
    interactions,
    swap_requests,
    messages,
    ratings,
    recommendations,
)

# Initialize FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SkillSwap AI - Web-based Student Skill Exchange and Recommendation REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware using environment settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_db_init():
    from sqlalchemy import text
    from app.core.database import SessionLocal, engine, Base
    from app.core.seed_demo_data import seed_demo_profiles

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Ensure new columns on profiles table
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE profiles ADD COLUMN IF NOT EXISTS gender_preference VARCHAR(50);"))
        conn.execute(text("ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_demo BOOLEAN DEFAULT false NOT NULL;"))
        conn.execute(text("ALTER TABLE profiles ADD COLUMN IF NOT EXISTS is_test BOOLEAN DEFAULT false NOT NULL;"))
        conn.commit()

    db = SessionLocal()
    try:
        seed_demo_profiles(db)
    finally:
        db.close()

# Root route
@app.get("/", tags=["Root"])
async def root():
    """
    Root API health and status check.
    """
    return {
        "service": "SkillSwap AI API",
        "status": "running"
    }

# Register API routes under /api
api_prefix = settings.API_V1_STR  # /api

app.include_router(health.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(profiles.router, prefix=api_prefix)
app.include_router(skills.router, prefix=api_prefix)
app.include_router(user_skills.router, prefix=api_prefix)
app.include_router(interactions.router, prefix=api_prefix)
app.include_router(swap_requests.router, prefix=api_prefix)
app.include_router(messages.router, prefix=api_prefix)
app.include_router(ratings.router, prefix=api_prefix)
app.include_router(recommendations.router, prefix=api_prefix)
