from pydantic import BaseModel


class LeaderboardPlace(BaseModel):
    user_id: int
    max_score: int
    place: int

    class Config:
        from_attributes = True
