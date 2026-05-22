from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Banner(Base):
    __tablename__ = "banners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    title_ru: Mapped[str | None] = mapped_column(String(255))
    title_kk: Mapped[str | None] = mapped_column(String(255))
    title_ky: Mapped[str | None] = mapped_column(String(255))
    subtitle: Mapped[str | None] = mapped_column(String(255))
    subtitle_ru: Mapped[str | None] = mapped_column(String(255))
    subtitle_kk: Mapped[str | None] = mapped_column(String(255))
    subtitle_ky: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    body_ru: Mapped[str | None] = mapped_column(Text)
    body_kk: Mapped[str | None] = mapped_column(Text)
    body_ky: Mapped[str | None] = mapped_column(Text)
    image_path: Mapped[str | None] = mapped_column(String(512))
    link_url: Mapped[str | None] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __str__(self) -> str:
        return self.title


class FlightInfo(Base):
    __tablename__ = "flight_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    origin_iata: Mapped[str] = mapped_column(String(10), nullable=False)
    origin_city: Mapped[str] = mapped_column(String(100), nullable=False)
    origin_city_ru: Mapped[str | None] = mapped_column(String(100))
    origin_city_kk: Mapped[str | None] = mapped_column(String(100))
    origin_city_ky: Mapped[str | None] = mapped_column(String(100))
    destination_iata: Mapped[str] = mapped_column(String(10), nullable=False)
    destination_city: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_city_ru: Mapped[str | None] = mapped_column(String(100))
    destination_city_kk: Mapped[str | None] = mapped_column(String(100))
    destination_city_ky: Mapped[str | None] = mapped_column(String(100))
    departure_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    arrival_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    aircraft_type: Mapped[str | None] = mapped_column(String(100))
    altitude_ft: Mapped[int | None] = mapped_column(Integer)
    speed_kmh: Mapped[int | None] = mapped_column(Integer)
    temperature_c: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __str__(self) -> str:
        return f"{self.flight_number} ({self.origin_iata} → {self.destination_iata})"
