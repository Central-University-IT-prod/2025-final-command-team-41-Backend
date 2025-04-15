from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionProtocol, BaseModel
from src.core.domain import BaseDomain
from src.core.exceptions import NotFoundError
from src.modules.base.domain.repositories import BaseRepository
from src.modules.base.domain.value_objects import Pagination


class BaseRepositoryImpl[D: BaseDomain, M: BaseModel](ABC, BaseRepository[D]):
    model_type: M

    def __init__(self, db: AsyncSession | AsyncSessionProtocol) -> None:
        self.db = db

    @abstractmethod
    def _map_to_orm(self, obj: D) -> M: ...

    @abstractmethod
    def _map_to_domain(self, obj: M) -> D: ...

    async def get_by_id(self, obj_id: UUID) -> D:
        stmt = select(self.model_type).where(self.model_type.id == obj_id)
        result = (await self.db.execute(stmt)).scalar_one_or_none()

        if result is None:
            msg = f'Model {self.model_type.__name__} with ID {obj_id} not found'
            raise NotFoundError(msg)

        return self._map_to_domain(result)

    async def get_all(self) -> list[D]:
        stmt = select(self.model_type)
        result = (await self.db.execute(stmt)).scalars().all()
        return [self._map_to_domain(model) for model in result]  # type: ignore

    async def get_all_paginated(self, pagination: Pagination) -> list[M]:
        stmt = select(self.model_type).limit(pagination.limit).offset(pagination.offset)
        result = (await self.db.execute(stmt)).scalars().all()
        return [self._map_to_domain(model) for model in result]  # type: ignore

    async def create(self, obj: D) -> D:
        model = self._map_to_orm(obj)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._map_to_domain(model)

    async def update(self, obj: D) -> D:
        model = self._map_to_orm(obj)
        model = await self.db.merge(model)  # type: ignore
        await self.db.commit()
        await self.db.refresh(model)
        return self._map_to_domain(model)

    async def delete(self, obj_id: UUID) -> None:
        stmt = select(self.model_type).where(self.model_type.id == obj_id)
        result = (await self.db.execute(stmt)).scalar_one_or_none()

        if result is None:
            raise NotFoundError

        await self.db.delete(result)
        await self.db.commit()
