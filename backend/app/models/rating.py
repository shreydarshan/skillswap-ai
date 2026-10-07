import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Text, Integer, DateTime, ForeignKey, UniqueConstraint, CheckConstraint, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Rating(Base):
    """
    Student Review & Rating ORM Model
    Stores post-swap peer reviews and score ratings (1-5 stars).
    """
    __tablename__ = "ratings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    reviewed_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    review: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    reviewer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reviewer_id],
        back_populates="ratings_given"
    )
    reviewed: Mapped["User"] = relationship(
        "User",
        foreign_keys=[reviewed_id],
        back_populates="ratings_received"
    )

    __table_args__ = (
        UniqueConstraint("reviewer_id", "reviewed_id", name="uq_rating_reviewer_reviewed"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
        CheckConstraint("reviewer_id != reviewed_id", name="ck_rating_not_self"),
    )
