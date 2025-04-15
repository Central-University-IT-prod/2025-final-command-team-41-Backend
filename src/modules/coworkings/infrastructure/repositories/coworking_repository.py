from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.coworkings.domain.entities import Coworking
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.coworkings.infrastructure.orm.models import CoworkingModel


class CoworkingRepositoryImpl(BaseRepositoryImpl[Coworking, CoworkingModel], CoworkingRepository):
    model_type = CoworkingModel

    def _map_to_domain(self, obj: CoworkingModel) -> Coworking:
        return Coworking(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            address=obj.address,
            opens_at=obj.opens_at,
            closes_at=obj.closes_at,
            images=obj.images,
        )

    def _map_to_orm(self, obj: Coworking) -> CoworkingModel:
        return CoworkingModel(
            id=obj.id,
            name=obj.name,
            description=obj.description,
            address=obj.address,
            opens_at=obj.opens_at,
            closes_at=obj.closes_at,
            images=obj.images,
        )
