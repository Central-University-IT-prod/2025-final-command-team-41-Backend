from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select

from src.modules.base.infrastructure.repositories.base_repository import BaseRepositoryImpl
from src.modules.bookings.domain.entities import Booking
from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.bookings.infrastructure.orm.models import BookingModel


class BookingRepositoryImpl(BaseRepositoryImpl[Booking, BookingModel], BookingRepository):
    model_type: type[BookingModel] = BookingModel

    def _map_to_domain(self, obj: BookingModel) -> Booking:
        return Booking(
            id=obj.id,
            user_id=obj.user_id,
            spot_id=obj.spot_id,
            time_from=obj.time_from,
            time_until=obj.time_until,
            status=obj.status,
        )

    def _map_to_orm(self, obj: Booking) -> BookingModel:
        return BookingModel(
            id=obj.id,
            user_id=obj.user_id,
            spot_id=obj.spot_id,
            time_from=obj.time_from,
            time_until=obj.time_until,
            status=obj.status,
        )

    async def get_by_user_id(self, user_id: UUID) -> list[Booking]:
        stmt = select(self.model_type).where(self.model_type.user_id == user_id)
        result = await self.db.execute(stmt)
        return [self._map_to_domain(obj) for obj in result.scalars().all()]

    async def get_by_spot_id(self, spot_id: UUID) -> list[Booking]:
        stmt = select(self.model_type).where(self.model_type.spot_id == spot_id)
        result = await self.db.execute(stmt)
        return [self._map_to_domain(obj) for obj in result.scalars().all()]

    async def get_active_bookings_in_time_range(
        self,
        spot_id: UUID,
        time_from: datetime,
        time_until: datetime,
    ) -> list[Booking]:
        stmt = select(self.model_type).where(
            and_(
                self.model_type.spot_id == spot_id,
                self.model_type.status == 'active',
                or_(
                    and_(
                        self.model_type.time_from >= time_from,
                        self.model_type.time_from < time_until,
                    ),
                    and_(
                        self.model_type.time_until > time_from,
                        self.model_type.time_until <= time_until,
                    ),
                    and_(
                        self.model_type.time_from <= time_from,
                        self.model_type.time_until >= time_until,
                    ),
                ),
            ),
        )

        result = await self.db.execute(stmt)
        return [self._map_to_domain(obj) for obj in result.scalars().all()]

    async def get_active_bookings_for_spots(
        self,
        spot_ids: list[UUID],
        time_from: datetime,
        time_until: datetime,
    ) -> list[Booking]:
        if not spot_ids:
            return []

        stmt = select(self.model_type).where(
            and_(
                self.model_type.spot_id.in_(spot_ids),
                self.model_type.status == 'active',
                or_(
                    and_(
                        self.model_type.time_from >= time_from,
                        self.model_type.time_from < time_until,
                    ),
                    and_(
                        self.model_type.time_until > time_from,
                        self.model_type.time_until <= time_until,
                    ),
                    and_(
                        self.model_type.time_from <= time_from,
                        self.model_type.time_until >= time_until,
                    ),
                ),
            ),
        )

        result = await self.db.execute(stmt)
        return [self._map_to_domain(obj) for obj in result.scalars().all()]
