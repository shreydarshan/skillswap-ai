import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.user import User
from app.models.skill import Skill
from app.models.user_skill import UserSkill, SkillType
from app.schemas.user_skill import UserSkillRead, UserSkillCreate
from app.api.deps import get_current_user

router = APIRouter(tags=["User Skills"])


@router.get("/profile/me/skills", response_model=List[UserSkillRead], summary="Get my skills (offered & wanted)")
def get_my_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all skills offered and wanted by the authenticated student.
    """
    user_skills = db.scalars(
        select(UserSkill).where(UserSkill.user_id == current_user.id)
    ).all()

    # Populate skill_name & skill_category for clean serialization
    result = []
    for us in user_skills:
        skill = db.get(Skill, us.skill_id)
        res = UserSkillRead(
            id=us.id,
            user_id=us.user_id,
            skill_id=us.skill_id,
            skill_type=us.skill_type,
            proficiency=us.proficiency,
            created_at=us.created_at,
            skill_name=skill.name if skill else None,
            skill_category=skill.category if skill else None
        )
        result.append(res)
    return result


@router.post("/profile/me/skills", response_model=UserSkillRead, status_code=status.HTTP_201_CREATED, summary="Add a skill to my profile")
def add_my_skill(
    skill_in: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a skill (OFFER or WANT) with proficiency (1-5) to the authenticated student's profile.
    Automatically creates the skill in the catalog if it does not exist yet.
    """
    if not (1 <= skill_in.proficiency <= 5):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proficiency must be between 1 and 5"
        )

    # 1. Resolve or create Skill record
    skill = None
    if skill_in.skill_id:
        skill = db.get(Skill, skill_in.skill_id)

    if not skill and skill_in.skill_name:
        name_clean = skill_in.skill_name.strip()
        skill = db.scalar(select(Skill).where(Skill.name.ilike(name_clean)))
        if not skill:
            skill = Skill(
                name=name_clean,
                category=skill_in.category or "General"
            )
            db.add(skill)
            db.flush()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill name or valid skill_id must be provided"
        )

    # 2. Check for duplicate (user_id, skill_id, skill_type)
    existing = db.scalar(
        select(UserSkill).where(
            and_(
                UserSkill.user_id == current_user.id,
                UserSkill.skill_id == skill.id,
                UserSkill.skill_type == skill_in.skill_type
            )
        )
    )
    if existing:
        # Update proficiency instead of throwing duplicate constraint error
        existing.proficiency = skill_in.proficiency
        db.commit()
        db.refresh(existing)
        return UserSkillRead(
            id=existing.id,
            user_id=existing.user_id,
            skill_id=existing.skill_id,
            skill_type=existing.skill_type,
            proficiency=existing.proficiency,
            created_at=existing.created_at,
            skill_name=skill.name,
            skill_category=skill.category
        )

    # 3. Create UserSkill record
    new_user_skill = UserSkill(
        user_id=current_user.id,
        skill_id=skill.id,
        skill_type=skill_in.skill_type,
        proficiency=skill_in.proficiency
    )
    db.add(new_user_skill)
    db.commit()
    db.refresh(new_user_skill)

    return UserSkillRead(
        id=new_user_skill.id,
        user_id=new_user_skill.user_id,
        skill_id=new_user_skill.skill_id,
        skill_type=new_user_skill.skill_type,
        proficiency=new_user_skill.proficiency,
        created_at=new_user_skill.created_at,
        skill_name=skill.name,
        skill_category=skill.category
    )


@router.delete("/profile/me/skills/{user_skill_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove a skill from my profile")
def remove_my_skill(
    user_skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a skill entry from the authenticated student's profile.
    Enforces user ownership.
    """
    user_skill = db.get(UserSkill, user_skill_id)
    if not user_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill record not found"
        )

    if user_skill.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this skill record"
        )

    db.delete(user_skill)
    db.commit()
    return None


# Public endpoint
@router.get("/users/{user_id}/skills", response_model=List[UserSkillRead], summary="Get skills for any user")
def get_user_skills(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve offered & wanted skills for any student user_id.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    user_skills = db.scalars(select(UserSkill).where(UserSkill.user_id == user_id)).all()
    result = []
    for us in user_skills:
        skill = db.get(Skill, us.skill_id)
        result.append(UserSkillRead(
            id=us.id,
            user_id=us.user_id,
            skill_id=us.skill_id,
            skill_type=us.skill_type,
            proficiency=us.proficiency,
            created_at=us.created_at,
            skill_name=skill.name if skill else None,
            skill_category=skill.category if skill else None
        ))
    return result
