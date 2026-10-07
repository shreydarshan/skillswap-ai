import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Profile(Base):
    """
    Student Profile ORM Model
    One-to-One extension of User table containing biographical & campus details.
    """
    __tablename__ = "profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    avatar_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    college: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    branch: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    location: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    experience_level: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    availability: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    gender_preference: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    is_demo: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false"
    )
    is_test: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="false"
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

    # Relationship back to User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile"
    )
