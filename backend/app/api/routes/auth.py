from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.profile import Profile
from app.models.user_skill import UserSkill
from app.models.interaction import Interaction
from app.models.swap_request import SwapRequest
from app.models.message import Message
from app.models.rating import Rating
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserAuthRead
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, summary="Register new student account")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new student account, creates the initial profile, and returns a JWT access token.
    Rejects duplicate email addresses.
    """
    # Check if user already exists
    existing_user = db.scalar(select(User).where(User.email == user_in.email.lower()))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash password & create user
    hashed_pwd = hash_password(user_in.password)
    new_user = User(
        email=user_in.email.lower(),
        password_hash=hashed_pwd,
        is_active=True
    )
    db.add(new_user)
    db.flush()  # Generate new_user.id

    # Create associated student profile
    new_profile = Profile(
        user_id=new_user.id,
        full_name=user_in.full_name
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_user)

    # Generate JWT Token
    access_token = create_access_token(subject=new_user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserAuthRead(
            id=new_user.id,
            email=new_user.email,
            full_name=user_in.full_name
        )
    )


@router.post("/login", response_model=TokenResponse, summary="Student login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates a student by email and password, returning a JWT access token.
    """
    user = db.scalar(select(User).where(User.email == user_in.email.lower()))
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Get full name from profile if available
    full_name = user.profile.full_name if user.profile else user.email.split("@")[0]

    access_token = create_access_token(subject=user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserAuthRead(
            id=user.id,
            email=user.email,
            full_name=full_name
        )
    )


@router.get("/me", response_model=UserAuthRead, summary="Get current authenticated user info")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Returns basic details of the currently authenticated student.
    """
    full_name = current_user.profile.full_name if current_user.profile else current_user.email
    return UserAuthRead(
        id=current_user.id,
        email=current_user.email,
        full_name=full_name
    )


@router.delete("/account", status_code=status.HTTP_200_OK, summary="Delete authenticated student account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently deletes the authenticated student account and all dependent database records.
    User ID is strictly derived from the authenticated JWT token.
    """
    user_id = current_user.id

    # 1. Delete dependent messages
    db.execute(delete(Message).where((Message.sender_id == user_id) | (Message.receiver_id == user_id)))

    # 2. Delete dependent swap requests
    db.execute(delete(SwapRequest).where((SwapRequest.sender_id == user_id) | (SwapRequest.receiver_id == user_id)))

    # 3. Delete dependent ratings
    db.execute(delete(Rating).where((Rating.reviewer_id == user_id) | (Rating.reviewed_id == user_id)))

    # 4. Delete dependent interactions
    db.execute(delete(Interaction).where((Interaction.user_id == user_id) | (Interaction.target_user_id == user_id)))

    # 5. Delete user skills
    db.execute(delete(UserSkill).where(UserSkill.user_id == user_id))

    # 6. Delete profile
    db.execute(delete(Profile).where(Profile.user_id == user_id))

    # 7. Delete user record
    db.execute(delete(User).where(User.id == user_id))

    db.commit()
    return {"message": "Account successfully deleted"}
