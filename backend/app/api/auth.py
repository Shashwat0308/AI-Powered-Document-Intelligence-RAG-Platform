from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.services.auth_service import (
    create_user,
    authenticate_user,
    create_user_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class SignupRequest(BaseModel):

    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):

    email: EmailStr
    password: str


@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    if len(request.password) < 8:

        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )

    user = create_user(
        db=db,
        name=request.name,
        email=request.email,
        password=request.password
    )

    if user is None:

        raise HTTPException(
            status_code=400,
            detail="Email is already registered"
        )

    token = create_user_token(user)

    return {
        "message": "Account created successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_user_token(user)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }