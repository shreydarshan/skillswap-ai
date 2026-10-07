import uuid
from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Skill(Base):
    """
    Skill Catalog ORM Model
    Master list of skills available for offering or learning.
    """
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )

    offered_in_swap_requests: Mapped[List["SwapRequest"]] = relationship(
        "SwapRequest",
        foreign_keys="[SwapRequest.skill_offered_id]",
        back_populates="skill_offered"
    )

    requested_in_swap_requests: Mapped[List["SwapRequest"]] = relationship(
        "SwapRequest",
        foreign_keys="[SwapRequest.skill_requested_id]",
        back_populates="skill_requested"
    )
