# mypy: ignore-errors
from typing import Generic, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import Base, async_session_maker
from backend.logger import get_logger

ModelType = TypeVar("ModelType", bound=Base)

logger = get_logger(__name__)


class BaseDAO(Generic[ModelType]):
    """Базовый класс для работы с базой данных."""

    model: type[ModelType]

    @classmethod
    async def get_all(cls, **filter_by) -> list[ModelType]:
        """Получить все записи."""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_one_or_none(cls, **filter_by) -> ModelType | None:
        """Получить запись по ID."""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def create(cls, **data) -> ModelType | None:
        """Создать новую запись."""
        try:
            query = insert(cls.model).values(**data).returning(cls.model)
            async with async_session_maker() as session:
                result = await session.execute(query)
                await session.commit()
                # return result.mappings().first() # noqa
                return result.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            logger.exception(msg, extra={"table": cls.model.__tablename__})
            return None

    @classmethod
    async def update(cls, **kwargs) -> ModelType | None:
        """Обновить запись."""
        async with async_session_maker() as session:
            query = update(cls.model).values(**kwargs)
            await session.execute(query)
            await session.commit()
            return await cls.get_one_or_none(session, **kwargs)

    @classmethod
    async def delete(cls, **filter_by) -> bool:
        """Удалить запись."""
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            await session.commit()
            return bool(result.rowcount > 0)
