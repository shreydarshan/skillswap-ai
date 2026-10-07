import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=2)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    availability: Optional[str] = None
    gender_preference: Optional[str] = None
    is_demo: bool = False
    is_test: bool = False


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    availability: Optional[str] = None
    gender_preference: Optional[str] = None
    is_demo: Optional[bool] = None
    is_test: Optional[bool] = None


class ProfileRead(BaseModel):
    user_id: uuid.UUID
    full_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    location: Optional[str] = None
    experience_level: Optional[str] = None
    availability: Optional[str] = None
    gender_preference: Optional[str] = None
    is_demo: bool = False
    is_test: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
