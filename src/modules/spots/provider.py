from dishka import Provider, Scope, provide  # type: ignore

from src.core.database import (
    AsyncSessionProtocol,
    TransactionManager,
)
from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.spots.application.services import SpotService
from src.modules.spots.domain.repositories import SpotRepository
from src.modules.spots.infrastructure.repositories.spot_repository import SpotRepositoryImpl


class SpotProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_spot_repository(self, session: AsyncSessionProtocol) -> SpotRepository:
        return SpotRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_spot_service(
        self,
        repo: SpotRepository,
        transaction_manager: TransactionManager,
        booking_repo: BookingRepository,
    ) -> SpotService:
        return SpotService(repo, transaction_manager, booking_repo)
