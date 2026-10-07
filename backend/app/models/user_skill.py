import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Integer, DateTime, ForeignKey, Enum, UniqueConstraint, CheckConstraint, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SkillType(str, PyEnum):
    OFFER = "OFFER"
    WANT = "WANT"


class UserSkill(Base):
    """
    User Skill Association ORM Model
    Maps skills to users with skill_type (OFFER vs WANT) and proficiency rating (1-5).
    """
    __tablename__ = "user_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_type: Mapped[SkillType] = mapped_column(
        Enum(SkillType, name="skill_type_enum"),
        nullable=False,
        index=True
    )
    proficiency: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="user_skills"
    )
    skill: Mapped["Skill"] = relationship(
        "Skill",
        back_populates="user_skills"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", "skill_type", name="uq_user_skill_type"),
        CheckConstraint("proficiency >= 1 AND proficiency <= 5", name="ck_user_skill_proficiency_range"),
    )
