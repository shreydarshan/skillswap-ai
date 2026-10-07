import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.swap_request import SwapStatus


class SwapRequestCreate(BaseModel):
    """
    Schema for proposing a new skill swap request.
    Sender is always determined from authenticated JWT token.
    """
    receiver_id: uuid.UUID
    skill_offered_id: Optional[uuid.UUID] = None
    skill_offered_name: Optional[str] = None
    skill_requested_id: Optional[uuid.UUID] = None
    skill_requested_name: Optional[str] = None
    message: Optional[str] = None


class SwapRequestStatusUpdate(BaseModel):
    """
    Schema for updating swap request lifecycle status (ACCEPTED, REJECTED, COMPLETED, CANCELLED).
    """
    status: SwapStatus


class SwapRequestRead(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    skill_offered_id: uuid.UUID
    skill_requested_id: uuid.UUID
    skill_offered_name: Optional[str] = None
    skill_requested_name: Optional[str] = None
    message: Optional[str] = None
    status: SwapStatus
    created_at: datetime
    updated_at: datetime
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    receiver_avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
