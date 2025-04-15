from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update

from src.modules.base.domain.value_objects import Pagination
from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.notifications.domain.entities import Notification
from src.modules.notifications.domain.exceptions import NotificationNotFoundError
from src.modules.notifications.domain.repositories import NotificationRepository
from src.modules.notifications.infrastructure.orm.models import NotificationModel


class NotificationRepositoryImpl(BaseRepositoryImpl[Notification, NotificationModel], NotificationRepository):
    model_type = NotificationModel

    def _map_to_domain(
        self,
        obj: NotificationModel,
    ) -> Notification:
        return Notification(
            id=obj.id,
            user_id=obj.user_id,
            type=obj.type,
            title=obj.title,
            body=obj.body,
            data={},
            created_at=obj.created_at,
            read_at=obj.read_at,
        )

    def _map_to_orm(self, obj: Notification) -> NotificationModel:
        return NotificationModel(
            id=obj.id,
            user_id=obj.user_id,
            type=obj.type,
            title=obj.title,
            body=obj.body,
            data=obj.data,
            created_at=obj.created_at,
            read_at=obj.read_at,
        )

    async def get_paginated_by_user_id(
        self,
        user_id: UUID,
        pagination: Pagination,
    ) -> list[Notification]:
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        result = (await self.db.execute(stmt)).scalars().all()
        return [self._map_to_domain(n) for n in result]

    async def mark_as_read(self, notification_id: UUID) -> None:
        notification = await self.db.get(NotificationModel, notification_id)
        if not notification:
            msg = f'Notification with id {notification_id} not found'
            raise NotificationNotFoundError(
                msg,
            )

        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == notification_id)
            .values(read_at=datetime.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_all_as_read(self, user_id: UUID) -> None:
        stmt = (
            update(NotificationModel)
            .where(
                NotificationModel.user_id == user_id,
                NotificationModel.read_at.is_(None),
            )
            .values(read_at=datetime.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_all_for_user(self, user_id: UUID) -> None:
        stmt = delete(NotificationModel).where(NotificationModel.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.commit()
