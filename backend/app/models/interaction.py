import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import DateTime, ForeignKey, Enum, CheckConstraint, Index, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class InteractionType(str, PyEnum):
    VIEW = "VIEW"
    LIKE = "LIKE"
    REQUEST = "REQUEST"
    ACCEPT = "ACCEPT"
    COMPLETE = "COMPLETE"


class Interaction(Base):
    """
    User Interaction History ORM Model
    Tracks profile views, likes, swap requests, acceptances, and completions for analytics & ML.
    """
    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    target_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    interaction_type: Mapped[InteractionType] = mapped_column(
        Enum(InteractionType, name="interaction_type_enum"),
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
        foreign_keys=[user_id],
        back_populates="sent_interactions"
    )
    target_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[target_user_id],
        back_populates="received_interactions"
    )

    __table_args__ = (
        CheckConstraint("user_id != target_user_id", name="ck_interaction_not_self"),
        Index("ix_interactions_user_type", "user_id", "interaction_type"),
        Index("ix_interactions_target_user", "target_user_id"),
        Index("ix_interactions_user_target", "user_id", "target_user_id"),
        Index("ix_interactions_created_at", "created_at"),
    )
