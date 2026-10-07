import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from app.models.user import User
from app.models.profile import Profile
from app.models.interaction import Interaction, InteractionType

logger = logging.getLogger("skillswap.interactions")

# Minimum cooldown window to prevent rapid duplicate VIEW spam
VIEW_COOLDOWN_MINUTES = 5


def record_interaction(
    db: Session,
    user_id: uuid.UUID,
    target_user_id: uuid.UUID,
    interaction_type: InteractionType,
    allow_cooldown_bypass: bool = False
) -> Optional[Interaction]:
    """
    Safely records a genuine user interaction in PostgreSQL for future collaborative filtering:
    
    Rules enforced:
    1. Rejects self-interactions (user_id == target_user_id).
    2. Rejects interactions if either actor is a test account (is_test == True).
    3. Rejects interactions if target user does not exist or is inactive.
    4. Handles repeated/duplicate events gracefully (VIEW cooldown window).
    5. Fails safely without raising exceptions or breaking the calling feature.
    
    :param db: SQLAlchemy Session
    :param user_id: Authenticated user initiating the interaction
    :param target_user_id: Candidate/partner student receiving the interaction
    :param interaction_type: VIEW, LIKE, REQUEST, ACCEPT, COMPLETE
    :param allow_cooldown_bypass: Force record even if within cooldown (useful for explicit tests)
    :return: The recorded Interaction or None if skipped/failed
    """
    try:
        # Rule 1: Never record self-interactions
        if user_id == target_user_id:
            logger.warning("Rejected self-interaction: user_id=%s equals target_user_id", user_id)
            return None

        # Rule 2: Validate initiating user and check is_test
        source_user = db.get(User, user_id)
        if not source_user or not source_user.is_active:
            logger.warning("Interaction rejected: source user %s not found or inactive", user_id)
            return None

        source_profile = db.get(Profile, user_id)
        if source_profile and source_profile.is_test:
            logger.debug("Skipping interaction tracking for source test account %s", user_id)
            return None

        # Rule 3: Validate target user and check is_test
        target_user = db.get(User, target_user_id)
        if not target_user or not target_user.is_active:
            logger.warning("Interaction rejected: target user %s not found or inactive", target_user_id)
            return None

        target_profile = db.get(Profile, target_user_id)
        if target_profile and target_profile.is_test:
            logger.debug("Skipping interaction tracking for target test account %s", target_user_id)
            return None

        # Rule 4: Handle duplicate/repeated VIEW actions safely with cooldown
        if interaction_type == InteractionType.VIEW and not allow_cooldown_bypass:
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=VIEW_COOLDOWN_MINUTES)
            recent_view = db.scalar(
                select(Interaction).where(
                    and_(
                        Interaction.user_id == user_id,
                        Interaction.target_user_id == target_user_id,
                        Interaction.interaction_type == InteractionType.VIEW,
                        Interaction.created_at >= cutoff
                    )
                ).order_by(desc(Interaction.created_at)).limit(1)
            )
            if recent_view:
                logger.debug(
                    "Duplicate VIEW within %d min cooldown: user=%s target=%s. Returning existing.",
                    VIEW_COOLDOWN_MINUTES, user_id, target_user_id
                )
                return recent_view

        # Insert new interaction
        interaction = Interaction(
            user_id=user_id,
            target_user_id=target_user_id,
            interaction_type=interaction_type
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        logger.info(
            "Interaction recorded | type=%s user=%s target=%s id=%s",
            interaction_type.value, user_id, target_user_id, interaction.id
        )
        return interaction

    except Exception as exc:
        # Rule 5: Fail safely without crashing calling feature
        db.rollback()
        logger.error(
            "Failed to record interaction: type=%s user=%s target=%s error=%s",
            getattr(interaction_type, "value", str(interaction_type)),
            user_id,
            target_user_id,
            exc,
            exc_info=True
        )
        return None


def get_user_interactions_history(
    db: Session,
    user_id: uuid.UUID,
    limit: int = 100
) -> List[Interaction]:
    """
    Retrieves interaction history for the user (only accessible by the user themselves).
    """
    return db.scalars(
        select(Interaction)
        .where(Interaction.user_id == user_id)
        .order_by(desc(Interaction.created_at))
        .limit(limit)
    ).all()
