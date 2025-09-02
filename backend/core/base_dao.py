# mypy: ignore-errors
from typing import Any, Generic, List, Protocol, TypeVar

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import Base
from backend.core.logger import get_logger

ModelType = TypeVar("ModelType", bound=Base)

logger = get_logger(__name__)


class IBaseDAO(Protocol[ModelType]):
    """Базовый интерфейс для DAO."""

    async def get_all(self, **filter_by: Any) -> List[ModelType]:
        """Получить все записи."""

    async def get_one_or_none(self, **filter_by: Any) -> ModelType | None:
        """Получить запись по фильтру или None."""

    async def create(self, **data: Any) -> ModelType | None:
        """Создать новую запись."""

    async def delete(self, **filter_by: Any) -> bool:
        """Удалить запись."""

    async def update(
        self,
        filters: dict[str, Any],
        update_data: dict[str, Any],
    ) -> ModelType | None:
        """Обновить запись."""


class BaseDAO(Generic[ModelType]):
    """Базовый класс для работы с базой данных."""

    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, **filter_by) -> list[ModelType]:
        """Получить все записи."""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by) -> ModelType | None:
        """Получить запись по ID."""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, **data) -> ModelType | None:
        """Создать новую запись."""
        try:
            query = insert(self.model).values(**data).returning(self.model)
            result = await self.session.execute(query)
            await self.session.commit()
            return result.scalar_one_or_none()
        except (SQLAlchemyError, Exception) as e:
            await self.session.rollback()
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            logger.exception(
                msg, extra={"table": self.model.__tablename__}, exc_info=True
            )
            raise

    async def delete(self, **filter_by) -> bool:
        """Удалить запись."""
        query = delete(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        await self.session.commit()
        return bool(result.rowcount > 0)

    async def update(
        self,
        filters: dict,  # Условия для выбора записи (например, {"id": 1})
        update_data: dict,  # Данные для обновления
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
            logger.exception(
                msg,
                exc_info=True,
                extra={"filters": filters, "update_data": update_data},
            )
            raise ValueError(msg)

        try:
            # Формируем условие WHERE из фильтров
            where_clause = and_(
                *[
                    getattr(self.model, key) == value
                    for key, value in filters.items()
                ]
            )

            # Выполняем обновление
            query = (
                update(self.model)
                .where(where_clause)
                .values(**update_data)
                .returning(
                    self.model
                )  # Возвращаем обновленную запись (если СУБД поддерживает)
            )

            result = await self.session.execute(query)
            updated_record = result.scalar_one_or_none()

            await self.session.commit()
            return updated_record  # noqa

        except SQLAlchemyError:
            await self.session.rollback()
            msg = "Error updating record"
            logger.exception(
                msg, extra={"table": self.model.__tablename__}, exc_info=True
            )
            raise
