import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillRead

router = APIRouter(prefix="/skills", tags=["Skills Catalog"])


@router.get("", response_model=List[SkillRead], summary="List all skills in catalog")
def get_skills(db: Session = Depends(get_db)):
    """
    Retrieve all skills from master skill catalog.
    Returns an empty array if no skills exist.
    """
    skills = db.scalars(select(Skill)).all()
    return skills


@router.get("/categories", summary="Get database-driven skill categories with counts")
def get_skill_categories(db: Session = Depends(get_db)):
    """
    Calculates actual PostgreSQL skill counts for categories.
    """
    all_skills = db.scalars(select(Skill)).all()
    total_count = len(all_skills)

    categories_def = [
        {"id": "all", "name": "All Skills", "category_matches": []},
        {"id": "coding", "name": "Programming & Web Dev", "category_matches": ["coding", "programming", "web", "frontend", "backend", "software"]},
        {"id": "design", "name": "UI/UX & Graphic Design", "category_matches": ["design", "ui/ux", "graphic", "figma", "illustration"]},
        {"id": "data", "name": "Data Science & AI", "category_matches": ["data", "ai", "machine learning", "python", "analytics"]},
        {"id": "languages", "name": "Foreign Languages", "category_matches": ["languages", "language", "spanish", "french", "german", "english"]},
        {"id": "math", "name": "Math & Physics", "category_matches": ["math", "physics", "calculus", "algebra", "science"]},
        {"id": "media", "name": "Video & Audio Production", "category_matches": ["media", "video", "audio", "film", "editing"]},
        {"id": "business", "name": "Marketing & Finance", "category_matches": ["business", "marketing", "finance", "seo"]}
    ]

    result = []
    for cat in categories_def:
        if cat["id"] == "all":
            count = total_count
        else:
            matches = cat["category_matches"]
            count = sum(
                1 for s in all_skills
                if any(m in (s.category or "").lower() or m in s.name.lower() for m in matches)
            )
        result.append({
            "id": cat["id"],
            "name": cat["name"],
            "count": count
        })

    return result


@router.get("/{skill_id}", response_model=SkillRead, summary="Get skill by ID")
def get_skill(skill_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a skill record by skill_id UUID.
    Returns HTTP 404 if the skill is not found.
    """
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with ID '{skill_id}' not found"
        )
    return skill
