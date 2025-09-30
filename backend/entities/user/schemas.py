from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class SUser(BaseModel):
    id: int
    telegram_id: int | None = None
    email: str | None = None
    username: str | None = None
    hashed_password: str | None = None
    is_admin: bool = False
    is_bot: bool = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SUserRegister(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str


class SUserAuth(BaseModel):
    username: str
    email: EmailStr
    password: str


class SUserAuthViaTelegram(BaseModel):
    username: str
    telegram_id: int


class SUserLogin(BaseModel):
    username_or_email: str
    password: str
