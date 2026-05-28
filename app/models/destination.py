from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # City name
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str | None] = mapped_column(String(100))
    name_kk: Mapped[str | None] = mapped_column(String(100))
    name_ky: Mapped[str | None] = mapped_column(String(100))

    iata_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Country
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    country_ru: Mapped[str | None] = mapped_column(String(100))
    country_kk: Mapped[str | None] = mapped_column(String(100))
    country_ky: Mapped[str | None] = mapped_column(String(100))

    region: Mapped[str | None] = mapped_column(String(100))  # e.g. "Europe"

    # Editorial copy
    subtitle: Mapped[str | None] = mapped_column(Text)
    subtitle_ru: Mapped[str | None] = mapped_column(Text)
    subtitle_kk: Mapped[str | None] = mapped_column(Text)
    subtitle_ky: Mapped[str | None] = mapped_column(Text)

    description: Mapped[str | None] = mapped_column(Text)
    description_ru: Mapped[str | None] = mapped_column(Text)
    description_kk: Mapped[str | None] = mapped_column(Text)
    description_ky: Mapped[str | None] = mapped_column(Text)

    # Location meta
    coords: Mapped[str | None] = mapped_column(String(200))   # "41°N · 28°E · UTC+3"
    timezone: Mapped[str | None] = mapped_column(String(50))  # "UTC+3"

    # Essentials
    airport_info: Mapped[str | None] = mapped_column(String(200))
    airport_hint: Mapped[str | None] = mapped_column(String(100))
    currency: Mapped[str | None] = mapped_column(String(100))
    currency_hint: Mapped[str | None] = mapped_column(String(100))
    language_info: Mapped[str | None] = mapped_column(String(200))
    language_hint: Mapped[str | None] = mapped_column(String(200))
    plug_info: Mapped[str | None] = mapped_column(String(100))
    plug_hint: Mapped[str | None] = mapped_column(String(100))
    flight_duration: Mapped[str | None] = mapped_column(String(50))  # "3H 50M"

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    photos: Mapped[list["DestinationPhoto"]] = relationship(
        "DestinationPhoto",
        back_populates="destination",
        order_by="DestinationPhoto.display_order",
        cascade="all, delete-orphan",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.iata_code})"


class DestinationPhoto(Base):
    __tablename__ = "destination_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    destination_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    photo_path: Mapped[str] = mapped_column(String(512), nullable=False)

    caption: Mapped[str | None] = mapped_column(String(255))
    caption_ru: Mapped[str | None] = mapped_column(String(255))
    caption_kk: Mapped[str | None] = mapped_column(String(255))
    caption_ky: Mapped[str | None] = mapped_column(String(255))

    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    destination: Mapped["Destination"] = relationship("Destination", back_populates="photos", lazy="selectin")

    def __str__(self) -> str:
        return f"Photo #{self.id} for destination {self.destination_id}"
