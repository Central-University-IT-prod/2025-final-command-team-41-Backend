from uuid import UUID

from sqlalchemy import select

from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.options.domain.entities import Option
from src.modules.options.domain.repositories import OptionRepository
from src.modules.options.infrastructure.orm.models import OptionModel


class OptionRepositoryImpl(BaseRepositoryImpl[Option, OptionModel], OptionRepository):
    model_type = OptionModel

    def _map_to_domain(self, obj: OptionModel) -> Option:
        return Option(
            id=obj.id,
            coworking_id=obj.coworking_id,
            name=obj.name,
        )

    def _map_to_orm(self, obj: Option) -> OptionModel:
        return OptionModel(
            id=obj.id,
            coworking_id=obj.coworking_id,
            name=obj.name,
        )

    async def get_by_coworking_id(self, coworking_id: UUID) -> list[Option]:
        stmt = select(self.model_type).where(self.model_type.coworking_id == coworking_id)
        result = (await self.db.execute(stmt)).scalars().all()
        return [self._map_to_domain(item) for item in result]
