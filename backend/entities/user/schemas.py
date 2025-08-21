from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class User(BaseModel):
    id: int
    telegram_id: int | None = None
    email: str | None = None
    username: str | None = None
    hashed_password: str | None = None
    is_admin: bool = False
    is_bot: bool = False
    is_active: bool = True
    max_score: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserAuth(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username_or_email: str
    password: str
