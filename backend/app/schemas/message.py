import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    receiver_id: uuid.UUID
    message: str


class MessageRead(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    message: str
    created_at: datetime
    sender_name: Optional[str] = None
    receiver_name: Optional[str] = None
    sender_avatar: Optional[str] = None
    receiver_avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
