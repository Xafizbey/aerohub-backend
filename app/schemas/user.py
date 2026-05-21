import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8)
    full_name: str | None = None
    seat_number: str | None = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores/hyphens allowed)")
        return v.lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    username: str
    full_name: str | None
    seat_number: str | None
    role: UserRole
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    full_name: str | None = None
    seat_number: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
