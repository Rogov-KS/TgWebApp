# Методы для рейтинга
@router.get("/leaderboard/snake")
async def get_snake_leaderboard(limit: int = 10) -> list[GameSession]:
    """Получить топ игроков в змейке."""
    top_scores = await GameSessionDAO.get_top_scores("snake", limit)
    return top_scores


@router.get("/leaderboard/snake/user/{user_id}/position")
async def get_user_snake_position(user_id: int) -> dict[str, int | None]:
    """Получить позицию пользователя в рейтинге змейки."""
    position = await GameSessionDAO.get_user_position(user_id, "snake")
    return {"position": position}


@router.get("/user/{user_id}/best-score/snake")
async def get_user_best_snake_score(user_id: int) -> GameSession | None:
    """Получить лучший результат пользователя в змейке."""
    best_score = await GameSessionDAO.get_user_best_score(user_id, "snake")
    return best_score
