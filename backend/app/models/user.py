import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Boolean, DateTime, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    """
    User Account ORM Model
    Stores core authentication and identity data.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
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

    # One-to-One relationship with Profile
    profile: Mapped[Optional["Profile"]] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # One-to-Many relationship with UserSkill
    user_skills: Mapped[List["UserSkill"]] = relationship(
        "UserSkill",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # Relationships with Interactions
    sent_interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction",
        foreign_keys="[Interaction.user_id]",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    received_interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction",
        foreign_keys="[Interaction.target_user_id]",
        back_populates="target_user",
        cascade="all, delete-orphan"
    )

    # Relationships with Swap Requests
    sent_swap_requests: Mapped[List["SwapRequest"]] = relationship(
        "SwapRequest",
        foreign_keys="[SwapRequest.sender_id]",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_swap_requests: Mapped[List["SwapRequest"]] = relationship(
        "SwapRequest",
        foreign_keys="[SwapRequest.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )

    # Relationships with Messages
    sent_messages: Mapped[List["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.sender_id]",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_messages: Mapped[List["Message"]] = relationship(
        "Message",
        foreign_keys="[Message.receiver_id]",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )

    # Relationships with Ratings
    ratings_given: Mapped[List["Rating"]] = relationship(
        "Rating",
        foreign_keys="[Rating.reviewer_id]",
        back_populates="reviewer",
        cascade="all, delete-orphan"
    )
    ratings_received: Mapped[List["Rating"]] = relationship(
        "Rating",
        foreign_keys="[Rating.reviewed_id]",
        back_populates="reviewed",
        cascade="all, delete-orphan"
    )
