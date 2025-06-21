from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
    telegram_id: int
    username: str | None = None
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
