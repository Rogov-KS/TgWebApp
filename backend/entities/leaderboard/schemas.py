from pydantic import BaseModel, ConfigDict


class LeaderboardPlace(BaseModel):
    user_id: int
    max_score: int
    place: int

    model_config = ConfigDict(from_attributes=True)
