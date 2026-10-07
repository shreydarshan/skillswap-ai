import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import Text, DateTime, ForeignKey, Enum, CheckConstraint, Index, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SwapStatus(str, PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SwapRequest(Base):
    """
    Skill Swap Request ORM Model
    Manages 1-on-1 swap proposals between students with offered and requested skills.
    """
    __tablename__ = "swap_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    skill_offered_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False
    )
    skill_requested_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="RESTRICT"),
        nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    status: Mapped[SwapStatus] = mapped_column(
        Enum(SwapStatus, name="swap_status_enum"),
        default=SwapStatus.PENDING,
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_swap_requests"
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_swap_requests"
    )

    skill_offered: Mapped["Skill"] = relationship(
        "Skill",
        foreign_keys=[skill_offered_id],
        back_populates="offered_in_swap_requests"
    )
    skill_requested: Mapped["Skill"] = relationship(
        "Skill",
        foreign_keys=[skill_requested_id],
        back_populates="requested_in_swap_requests"
    )

    __table_args__ = (
        CheckConstraint("sender_id != receiver_id", name="ck_swap_request_not_self"),
        Index("ix_swap_requests_sender_status", "sender_id", "status"),
        Index("ix_swap_requests_receiver_status", "receiver_id", "status"),
    )
