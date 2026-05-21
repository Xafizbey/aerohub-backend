import logging
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import TokenResponse, UserOut, UserRegister

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def register_user(data: UserRegister, db: AsyncSession) -> TokenResponse:
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_u = await db.execute(select(User).where(User.username == data.username))
    if existing_u.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        seat_number=data.seat_number,
        role=UserRole.passenger,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token(str(user.id))
    logger.info("New user registered: %s", user.email)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


async def login_user(email: str, password: str, db: AsyncSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    token = create_access_token(str(user.id))
    logger.info("User logged in: %s", user.email)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    user_id: str | None = payload.get("sub")
    if not user_id:
        raise credentials_exc

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_exc

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exc
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
