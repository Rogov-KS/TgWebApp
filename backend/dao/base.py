from typing import Generic, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseDAO(Generic[ModelType]):
    """Базовый класс для работы с базой данных."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get_all(self, session: AsyncSession) -> list[ModelType]:
        """Получить все записи."""
        query = select(self.model)
        result = await session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, obj_id: int) -> ModelType | None:
        """Получить запись по ID."""
        query = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, **kwargs) -> ModelType:
        """Создать новую запись."""
        instance = self.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def update(
        self, session: AsyncSession, obj_id: int, **kwargs
    ) -> ModelType | None:
        """Обновить запись."""
        query = update(self.model).where(self.model.id == obj_id).values(**kwargs)
        await session.execute(query)
        await session.commit()
        return await self.get_by_id(session, obj_id)

    async def delete(self, session: AsyncSession, obj_id: int) -> bool:
        """Удалить запись."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0
