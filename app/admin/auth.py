from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import select
from starlette.requests import Request

from app.core.security import verify_password
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email_or_username = str(form.get("username", "")).strip()
        password = str(form.get("password", ""))

        if not email_or_username or not password:
            return False

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(
                    (User.email == email_or_username) | (User.username == email_or_username)
                )
            )
            user = result.scalar_one_or_none()

        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        if user.role != UserRole.admin:
            return False
        if not user.is_active:
            return False

        request.session.update({"admin_id": str(user.id), "admin_email": user.email})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin_id"))
