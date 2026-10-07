import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RatingRead(BaseModel):
    id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewed_id: uuid.UUID
    rating: int
    review: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
