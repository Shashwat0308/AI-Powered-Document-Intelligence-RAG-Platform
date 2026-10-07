from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.core.security import create_access_token


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_user(
    db: Session,
    name: str,
    email: str,
    password: str
):

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        return None

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


def create_user_token(user: User) -> str:

    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name
    })