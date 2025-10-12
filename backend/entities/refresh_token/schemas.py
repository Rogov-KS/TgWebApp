from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SRefreshToken(BaseModel):
    id: int
    token: str
    user_id: int
    expires_at: datetime
    created_at: datetime
    is_revoked: bool

    model_config = ConfigDict(from_attributes=True)
