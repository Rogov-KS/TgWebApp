# mypy: ignore-errors
from typing import Generic, TypeVar

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError

from backend.core.database import Base, async_session_maker
from backend.core.logger import get_logger

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

            logger.error(
                msg,
                extra={"table": cls.model.__tablename__},
                exc_info=True
            )
            return None

    @classmethod
    async def delete(cls, **filter_by) -> bool:
        """Удалить запись."""
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            await session.commit()
            return bool(result.rowcount > 0)

    @classmethod
    async def update(
        cls,
        filters: dict,  # Условия для выбора записи (например, {"id": 1})
        update_data: dict,  # Данные для обновления (например, {"name": "New Name"})
    ) -> ModelType | None:
        """
        Обновляет запись по фильтру и возвращает обновленный объект.

        :param filters: Условия выборки (обычно по PK, например, {"id": 1}).
        :param update_data: Данные для обновления.
        :return: Обновленная запись или None, если запись не найдена.
        :raises ValueError: Если фильтры или данные обновления пусты.
        """
        if not filters or not update_data:
            msg = "Filters and update data cannot be empty"
            logger.error(msg, exc_info=True, extra={"filters": filters, "update_data": update_data})
            raise ValueError(msg)

        async with async_session_maker() as session:
            try:
                # Формируем условие WHERE из фильтров
                where_clause = and_(
                    *[
                        getattr(cls.model, key) == value
                        for key, value in filters.items()
                    ]
                )

                # Выполняем обновление
                query = (
                    update(cls.model)
                    .where(where_clause)
                    .values(**update_data)
                    .returning(
                        cls.model
                    )  # Возвращаем обновленную запись (если СУБД поддерживает)
                )

                result = await session.execute(query)
                updated_record = result.scalar_one_or_none()

                await session.commit()
                return updated_record  # noqa

            except SQLAlchemyError as e:
                await session.rollback()
                msg = "Error updating record"
                logger.error(
                    msg,
                    extra={"table": cls.model.__tablename__},
                    exc_info=True
                )
                raise ValueError(msg) from e
