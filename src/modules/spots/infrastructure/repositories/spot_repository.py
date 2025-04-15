from uuid import UUID

from sqlalchemy import select

from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.spots.domain.entities import Spot
from src.modules.spots.domain.repositories import SpotRepository
from src.modules.spots.infrastructure.orm.models import SpotModel


class SpotRepositoryImpl(BaseRepositoryImpl[Spot, SpotModel], SpotRepository):
    model_type = SpotModel

    def _map_to_domain(self, obj: SpotModel) -> Spot:
        return Spot(
            id=obj.id,
            coworking_id=obj.coworking_id,
            name=obj.name,
            description=obj.description,
            position=obj.position,
            status=obj.status,
        )

    def _map_to_orm(self, obj: Spot) -> SpotModel:
        return SpotModel(
            id=obj.id,
            coworking_id=obj.coworking_id,
            name=obj.name,
            description=obj.description,
            position=obj.position,
            status=obj.status,
        )

    async def get_by_coworking_id(self, coworking_id: UUID) -> list[Spot]:
        stmt = select(self.model_type).where(self.model_type.coworking_id == coworking_id)
        result = (await self.db.execute(stmt)).scalars().all()
        return [self._map_to_domain(model) for model in result]
