from dishka import Provider, Scope, provide

from src.core.database import AsyncSessionProtocol, TransactionManager
from src.core.events import EventBus
from src.modules.bookings.application.services import BookingService
from src.modules.bookings.domain.repositories import BookingRepository
from src.modules.bookings.infrastructure.repositories.booking_repository import BookingRepositoryImpl
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.options.domain.repositories import OptionRepository
from src.modules.spots.domain.repositories import SpotRepository
from src.modules.users.domain.repositories import UserRepository


class BookingProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_booking_repository(self, session: AsyncSessionProtocol) -> BookingRepository:
        return BookingRepositoryImpl(session)

    @provide(scope=Scope.REQUEST)
    def get_booking_service(
        self,
        booking_repo: BookingRepository,
        spot_repo: SpotRepository,
        coworking_repo: CoworkingRepository,
        event_bus: EventBus,
        transaction_manager: TransactionManager,
        user_repo: UserRepository,
        option_repo: OptionRepository,
    ) -> BookingService:
        return BookingService(
            booking_repo=booking_repo,
            spot_repo=spot_repo,
            coworking_repo=coworking_repo,
            event_bus=event_bus,
            transaction_manager=transaction_manager,
            user_repo=user_repo,
            option_repo=option_repo,
        )
