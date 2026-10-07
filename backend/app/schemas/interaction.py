import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.interaction import InteractionType


class InteractionCreate(BaseModel):
    """
    Schema for recording an interaction with a target student.
    Initiating user_id is always extracted from the authenticated JWT token.
    """
    target_user_id: uuid.UUID
    interaction_type: InteractionType


class InteractionRead(BaseModel):
    """
    Schema for reading a recorded interaction.
    """
    id: uuid.UUID
    user_id: uuid.UUID
    target_user_id: uuid.UUID
    interaction_type: InteractionType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InteractionResponse(BaseModel):
    """
    Standard response wrapper for interaction recording.
    """
    status: str = "success"
    recorded: bool
    interaction: Optional[InteractionRead] = None
    message: Optional[str] = None
