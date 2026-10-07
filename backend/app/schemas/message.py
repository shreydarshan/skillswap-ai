import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MessageRead(BaseModel):
    id: uuid.UUID
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
