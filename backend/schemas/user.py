from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    telegram_id: int | None = None
    email: str | None = None
    username: str
    hashed_password: str
    first_name: str
    last_name: str | None = None
    language_code: str | None = None
    is_bot: bool = False
    is_active: bool = True
    max_score: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserAuth(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username_or_email: str
    password: str
