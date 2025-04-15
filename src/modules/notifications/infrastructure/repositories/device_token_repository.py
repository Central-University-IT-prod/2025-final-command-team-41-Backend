from uuid import UUID

from sqlalchemy import delete, select

from src.core.exceptions import NotFoundError
from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.notifications.domain.entities import DeviceToken
from src.modules.notifications.domain.repositories import DeviceTokenRepository
from src.modules.notifications.infrastructure.orm.models import DeviceTokenModel


class DeviceTokenRepositoryImpl(BaseRepositoryImpl[DeviceToken, DeviceTokenModel], DeviceTokenRepository):
    model_type = DeviceTokenModel

    def _map_to_domain(
        self,
        obj: DeviceTokenModel,
    ) -> DeviceToken:
        return DeviceToken(
            id=obj.id,
            user_id=obj.user_id,
            token=obj.token,
            device_type=obj.device_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    def _map_to_orm(self, obj: DeviceToken) -> DeviceTokenModel:
        return DeviceTokenModel(
            id=obj.id,
            user_id=obj.user_id,
            token=obj.token,
            device_type=obj.device_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

    async def get_by_user_id(self, user_id: UUID) -> list[DeviceToken]:
        stmt = select(DeviceTokenModel).where(DeviceTokenModel.user_id == user_id)
        result = await self.db.execute(stmt)
        db_tokens = result.scalars().all()
        return [token for token in (self._map_to_domain(t) for t in db_tokens) if token is not None]

    async def get_by_token(self, token: str) -> DeviceToken:
        stmt = select(DeviceTokenModel).where(DeviceTokenModel.token == token)
        result = (await self.db.execute(stmt)).scalar_one_or_none()
        if result is None:
            raise NotFoundError
        return self._map_to_domain(result)

    async def delete_by_token(self, token: str) -> None:
        stmt = delete(DeviceTokenModel).where(DeviceTokenModel.token == token)
        await self.db.execute(stmt)
        await self.db.commit()
