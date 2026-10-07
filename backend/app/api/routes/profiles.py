import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.profile import Profile
from app.models.user import User
from app.models.user_skill import UserSkill, SkillType
from app.models.skill import Skill
from app.schemas.profile import ProfileRead, ProfileCreate, ProfileUpdate
from app.api.deps import get_current_user
from app.core.security import decode_access_token
from app.models.interaction import InteractionType
from app.services.interaction_service import record_interaction

router = APIRouter(tags=["Profiles"])


@router.get("/profile/me", response_model=ProfileRead, summary="Get current student's profile")
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve the authenticated student's profile.
    """
    profile = db.get(Profile, current_user.id)
    if not profile:
        profile = Profile(
            user_id=current_user.id,
            full_name=""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.post("/profile/me", response_model=ProfileRead, summary="Create or initialize current student's profile")
def create_my_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or initialize profile data for the authenticated student.
    """
    profile = db.get(Profile, current_user.id)
    if profile:
        for field, value in profile_in.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        profile = Profile(
            user_id=current_user.id,
            **profile_in.model_dump()
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.put("/profile/me", response_model=ProfileRead, summary="Update current student's profile")
def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update profile details for the authenticated student.
    """
    profile = db.get(Profile, current_user.id)
    if not profile:
        profile = Profile(user_id=current_user.id, full_name="")
        db.add(profile)

    fields_set = profile_in.model_fields_set

    for field, value in profile_in.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(profile, field, value)

    # If avatar_url was explicitly provided in the request payload (including None/null)
    if "avatar_url" in fields_set:
        profile.avatar_url = profile_in.avatar_url

    # Handle deterministic avatar generation if gender_preference is updated and avatar_url was not explicitly set
    # (Maintains compatibility with test_stage7_verification.py which tests gender_preference with dicebear parameters)
    elif profile_in.gender_preference is not None:
        pref = profile_in.gender_preference.lower()
        seed = (profile.full_name or current_user.email).replace(" ", "_")
        if "female" in pref:
            profile.avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}&gender=female&top=bigHair,bob,bun,curly,curvy,dreads01,frida,froBand,longHair,miaWallace,straight01,straight02"
        elif "male" in pref:
            profile.avatar_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={seed}&gender=male&top=shortFlat,shortRound,shortWaved,sides,theCaesar,theCaesarAndSidePart,frizzle&facialHairProbability=25"
        elif "non-binary" in pref or "neutral" in pref:
            profile.avatar_url = f"https://api.dicebear.com/7.x/bottts/svg?seed={seed}"
        elif "prefer not" in pref:
            profile.avatar_url = None

    db.commit()
    db.refresh(profile)
    return profile


# Database-driven Student Candidates Endpoint
@router.get("/students", summary="Get database-driven student candidate profiles")
def get_students(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Returns actual registered student candidate profiles from PostgreSQL.
    Excludes test profiles (is_test == True) and the currently authenticated user.
    """
    current_user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                current_user_id = uuid.UUID(payload["sub"])
            except ValueError:
                pass

    query = select(Profile).where(Profile.is_test == False)
    if current_user_id:
        query = query.where(Profile.user_id != current_user_id)

    profiles = db.scalars(query).all()

    candidates = []
    for prof in profiles:
        user = db.get(User, prof.user_id)
        if not user or not user.is_active:
            continue

        # Fetch user's skills
        user_skills = db.scalars(select(UserSkill).where(UserSkill.user_id == prof.user_id)).all()
        skills_offered = []
        skills_wanted = []

        for us in user_skills:
            skill = db.get(Skill, us.skill_id)
            if not skill:
                continue
            skill_dict = {
                "id": str(us.id),
                "name": skill.name,
                "category": skill.category or "General"
            }
            if us.skill_type == SkillType.OFFER:
                skill_dict["level"] = f"Proficiency: {us.proficiency}/5"
                skills_offered.append(skill_dict)
            else:
                skill_dict["urgency"] = "High"
                skills_wanted.append(skill_dict)

        year_str = f"Year {prof.year}" if prof.year else "Student"
        role_str = f"{prof.branch or 'Student'} ({prof.college or 'Campus'})"

        candidates.append({
            "id": str(prof.user_id),
            "name": prof.full_name or "Student",
            "email": user.email,
            "role": role_str,
            "major": prof.branch or "",
            "university": prof.college or "",
            "year": year_str,
            "location": prof.location or "On Campus",
            "bio": prof.bio or "",
            "availability": prof.availability or "",
            "avatar": prof.avatar_url,
            "avatar_url": prof.avatar_url,
            "gender_preference": prof.gender_preference,
            "rating": 5.0,
            "reviewCount": 0,
            "completedSwaps": 0,
            "skillsOffered": skills_offered,
            "skillsWanted": skills_wanted,
            "is_demo": prof.is_demo,
            "is_test": prof.is_test
        })

    return candidates


# Public Profile Read Endpoints
@router.get("/profiles", response_model=List[ProfileRead], summary="List all public profiles")
def get_profiles(db: Session = Depends(get_db)):
    """
    Retrieve all student profiles.
    """
    return db.scalars(select(Profile)).all()


@router.get("/profiles/{user_id}", response_model=ProfileRead, summary="Get public profile by User ID")
def get_profile_by_id(
    user_id: uuid.UUID,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Retrieve public student profile by user_id.
    Safely logs a genuine VIEW interaction if requested by an authenticated peer student.
    """
    profile = db.get(Profile, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile for user_id '{user_id}' not found"
        )

    # Safely track genuine VIEW interaction if viewer is authenticated and viewing a peer
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_access_token(token)
        if payload and "sub" in payload:
            try:
                viewer_id = uuid.UUID(payload["sub"])
                if viewer_id != user_id:
                    record_interaction(
                        db=db,
                        user_id=viewer_id,
                        target_user_id=user_id,
                        interaction_type=InteractionType.VIEW
                    )
            except (ValueError, TypeError):
                pass

    return profile
