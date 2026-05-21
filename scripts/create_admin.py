"""Quick helper to create/promote an admin user."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole

engine = create_async_engine(settings.DATABASE_URL, echo=False)
Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def main(email: str, password: str) -> None:
    async with Session() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            user.role = UserRole.admin
            print(f"Promoted {email} to admin")
        else:
            user = User(
                email=email,
                username=email.split("@")[0],
                hashed_password=hash_password(password),
                role=UserRole.admin,
            )
            db.add(user)
            print(f"Created admin: {email}")
        await db.commit()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_admin.py <email> <password>")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2]))
