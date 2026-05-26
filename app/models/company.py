from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CompanySettings(Base):
    """Singleton table — always exactly one row with id=1."""

    __tablename__ = "company_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    airline_name: Mapped[str] = mapped_column(String(200), nullable=False, default="AeroHub")
    logo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Stub for sqladmin FileField
    logo_upload = None

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __str__(self) -> str:
        return self.airline_name
