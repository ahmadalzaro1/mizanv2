from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.deps import get_current_user, require_admin
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    CreateModeratorRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role.value,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    request: CreateModeratorRequest,
    current_user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    """Admin creates a user account within their institution."""
    if current_user.role == UserRole.super_admin:
        if request.institution_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Super-admin must provide institution_id when creating a user",
            )
        institution_id = request.institution_id
    else:
        institution_id = current_user.institution_id

    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    new_user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
        role=request.role,
        institution_id=institution_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    current_user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    """Admin lists all users in their institution."""
    if current_user.role == UserRole.super_admin:
        users = db.query(User).all()
    else:
        users = db.query(User).filter(
            User.institution_id == current_user.institution_id
        ).all()
    return users
