import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, or_, and_, desc

from app.core.database import get_db
from app.models.user import User
from app.models.skill import Skill
from app.models.swap_request import SwapRequest, SwapStatus
from app.models.interaction import InteractionType
from app.schemas.swap_request import SwapRequestRead, SwapRequestCreate, SwapRequestStatusUpdate
from app.api.deps import get_current_user
from app.services.interaction_service import record_interaction

router = APIRouter(prefix="/swap-requests", tags=["Swap Requests"])


def _format_swap_read(swap: SwapRequest, db: Session) -> SwapRequestRead:
    off_skill = db.get(Skill, swap.skill_offered_id)
    req_skill = db.get(Skill, swap.skill_requested_id)
    return SwapRequestRead(
        id=swap.id,
        sender_id=swap.sender_id,
        receiver_id=swap.receiver_id,
        skill_offered_id=swap.skill_offered_id,
        skill_requested_id=swap.skill_requested_id,
        skill_offered_name=off_skill.name if off_skill else None,
        skill_requested_name=req_skill.name if req_skill else None,
        message=swap.message,
        status=swap.status,
        created_at=swap.created_at,
        updated_at=swap.updated_at
    )


@router.post("", response_model=SwapRequestRead, status_code=status.HTTP_201_CREATED, summary="Propose a skill swap request")
def create_swap_request(
    swap_in: SwapRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new skill swap proposal from the authenticated user to a target student.
    Automatically logs a genuine REQUEST interaction.
    """
    if swap_in.receiver_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot propose a skill swap to yourself"
        )

    receiver = db.get(User, swap_in.receiver_id)
    if not receiver or not receiver.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target receiver '{swap_in.receiver_id}' not found"
        )

    # 1. Resolve Offered Skill
    skill_off = None
    if swap_in.skill_offered_id:
        skill_off = db.get(Skill, swap_in.skill_offered_id)
    elif swap_in.skill_offered_name:
        name_clean = swap_in.skill_offered_name.strip()
        skill_off = db.scalar(select(Skill).where(Skill.name.ilike(name_clean)))
        if not skill_off:
            skill_off = Skill(name=name_clean, category="General")
            db.add(skill_off)
            db.flush()

    if not skill_off:
        # Fallback to existing catalog skill if not specified
        skill_off = db.scalar(select(Skill))
        if not skill_off:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offered skill must be specified"
            )

    # 2. Resolve Requested Skill
    skill_req = None
    if swap_in.skill_requested_id:
        skill_req = db.get(Skill, swap_in.skill_requested_id)
    elif swap_in.skill_requested_name:
        name_clean = swap_in.skill_requested_name.strip()
        skill_req = db.scalar(select(Skill).where(Skill.name.ilike(name_clean)))
        if not skill_req:
            skill_req = Skill(name=name_clean, category="General")
            db.add(skill_req)
            db.flush()

    if not skill_req:
        skill_req = db.scalar(select(Skill))
        if not skill_req:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested skill must be specified"
            )

    # 3. Create SwapRequest record
    swap = SwapRequest(
        sender_id=current_user.id,
        receiver_id=swap_in.receiver_id,
        skill_offered_id=skill_off.id,
        skill_requested_id=skill_req.id,
        message=swap_in.message,
        status=SwapStatus.PENDING
    )
    db.add(swap)
    db.commit()
    db.refresh(swap)

    # 4. Safely track genuine REQUEST interaction
    record_interaction(
        db=db,
        user_id=current_user.id,
        target_user_id=swap_in.receiver_id,
        interaction_type=InteractionType.REQUEST
    )

    return _format_swap_read(swap, db)


@router.put("/{swap_id}/accept", response_model=SwapRequestRead, summary="Accept an incoming swap request")
def accept_swap_request(
    swap_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Accepts a pending swap request. Only the intended recipient can accept.
    Automatically logs a genuine ACCEPT interaction.
    """
    swap = db.get(SwapRequest, swap_id)
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Swap request '{swap_id}' not found"
        )

    if swap.receiver_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the recipient of this swap request can accept it"
        )

    if swap.status != SwapStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot accept swap request with status '{swap.status}'"
        )

    swap.status = SwapStatus.ACCEPTED
    db.commit()
    db.refresh(swap)

    # Track genuine ACCEPT interaction (recipient accepting sender's request)
    record_interaction(
        db=db,
        user_id=current_user.id,
        target_user_id=swap.sender_id,
        interaction_type=InteractionType.ACCEPT
    )

    return _format_swap_read(swap, db)


@router.put("/{swap_id}/complete", response_model=SwapRequestRead, summary="Mark an accepted swap request as completed")
def complete_swap_request(
    swap_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Marks an accepted skill swap as completed. Either participating student can complete.
    Automatically logs a genuine COMPLETE interaction.
    """
    swap = db.get(SwapRequest, swap_id)
    if not swap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Swap request '{swap_id}' not found"
        )

    if current_user.id not in (swap.sender_id, swap.receiver_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a participant in this swap request"
        )

    if swap.status != SwapStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete swap request with status '{swap.status}'. Must be ACCEPTED."
        )

    swap.status = SwapStatus.COMPLETED
    db.commit()
    db.refresh(swap)

    partner_id = swap.sender_id if current_user.id == swap.receiver_id else swap.receiver_id

    # Track genuine COMPLETE interaction
    record_interaction(
        db=db,
        user_id=current_user.id,
        target_user_id=partner_id,
        interaction_type=InteractionType.COMPLETE
    )

    return _format_swap_read(swap, db)


@router.get("/me", response_model=List[SwapRequestRead], summary="Get my swap requests (sent and received)")
def get_my_swap_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all swap requests sent or received by the authenticated student.
    """
    swaps = db.scalars(
        select(SwapRequest).where(
            or_(
                SwapRequest.sender_id == current_user.id,
                SwapRequest.receiver_id == current_user.id
            )
        ).order_by(desc(SwapRequest.created_at))
    ).all()

    return [_format_swap_read(s, db) for s in swaps]


# Legacy endpoint for backward compatibility
@router.get("/users/{user_id}/swap-requests", response_model=List[SwapRequestRead], summary="Get swap requests for a user")
def get_user_swap_requests(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve skill swap requests for a specific user_id.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found"
        )

    swaps = db.scalars(
        select(SwapRequest).where(
            or_(
                SwapRequest.sender_id == user_id,
                SwapRequest.receiver_id == user_id
            )
        ).order_by(desc(SwapRequest.created_at))
    ).all()
    return [_format_swap_read(s, db) for s in swaps]
