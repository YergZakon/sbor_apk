"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.crud import user as crud_user
from app.schemas.user import (
    UserRegister,
    UserRead,
    Token,
    UserUpdatePassword
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_token
)
from app.models.user import User


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register new user

    - **username**: unique username (3-50 characters)
    - **email**: unique email address
    - **password**: password (min 8 characters)
    - **full_name**: optional full name
    """
    # Check if username exists
    if crud_user.get_user_by_username(db, username=user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    if crud_user.get_user_by_email(db, email=user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    from app.schemas.user import UserCreate
    user_create = UserCreate(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role="farmer"  # Default role
    )

    user = crud_user.create_user(db=db, user=user_create)
    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login

    - **username**: username or email
    - **password**: password

    Returns access_token and refresh_token
    """
    # Authenticate user
    user = crud_user.authenticate_user(
        db,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    # Update last login
    crud_user.update_last_login(db, user.id)

    # Create tokens
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    - **refresh_token**: valid refresh token

    Returns new access_token and refresh_token
    """
    # Decode refresh token
    payload = decode_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user
    user_id = payload.get("sub")
    user = crud_user.get_user(db, user_id=user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserRead)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information

    Requires authentication
    """
    return current_user


@router.post("/change-password")
def change_password(
    password_update: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change current user's password

    - **current_password**: current password
    - **new_password**: new password (min 8 characters)
    """
    # Verify current password
    if not verify_password(password_update.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Update password
    crud_user.update_password(db, user_id=current_user.id, new_password=password_update.new_password)

    return {"message": "Password updated successfully"}


@router.post("/logout")
def logout():
    """
    Logout user

    Note: With JWT tokens, logout is handled client-side by removing the token.
    This endpoint exists for API completeness.
    """
    return {"message": "Successfully logged out"}
