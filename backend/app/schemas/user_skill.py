import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.user_skill import SkillType


class UserSkillCreate(BaseModel):
    skill_name: Optional[str] = Field(default=None, description="Name of skill (e.g. React.js, Python)")
    skill_id: Optional[uuid.UUID] = Field(default=None, description="ID of existing skill")
    skill_type: SkillType = Field(description="OFFER or WANT")
    proficiency: int = Field(ge=1, le=5, description="Skill proficiency from 1 to 5")
    category: Optional[str] = Field(default="General", description="Skill category if creating new skill entry")


class UserSkillRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    skill_id: uuid.UUID
    skill_type: SkillType
    proficiency: int
    created_at: datetime
    skill_name: Optional[str] = None
    skill_category: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
