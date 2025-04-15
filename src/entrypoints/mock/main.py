import asyncio
import datetime
import random
from datetime import time, timedelta
from uuid import UUID, uuid4

from dishka import AsyncContainer
from faker import Faker

from src.core.container import container
from src.core.exceptions import NotFoundError
from src.modules.bookings.application.services import BookingService
from src.modules.coworkings.domain.entities import Coworking
from src.modules.coworkings.domain.repositories import CoworkingRepository
from src.modules.spots.application.services import SpotService
from src.modules.spots.domain.entities import Spot
from src.modules.spots.domain.repositories import SpotRepository
from src.modules.users.domain.entities import User
from src.modules.users.domain.repositories import UserRepository

faker = Faker('ru_RU')

coworkings = (
    Coworking(
        id=UUID('c6158cf4-853f-44f2-b755-904b6781c179'),
        name='Big-Space Белорусская',
        description='Просторный коворкинг в центре Москвы, рядом с метро Белорусская.',
        address='Москва, ул. Лесная, д. 5',
        opens_at=time(9 - 3, 0, tzinfo=datetime.UTC),
        closes_at=time(21 - 3, 0, tzinfo=datetime.UTC),
        images=[
            'https://storage.yandexcloud.net/kurva/ec771665-b740-46b2-a949-0fc0894fa97a',
            'https://storage.yandexcloud.net/kurva/9c1a43f0-427e-446c-a15a-87b2a41fc53b',
        ],
    ),
    Coworking(
        id=UUID('a1b2c3d4-e5f6-7890-1234-567890abcdef'),
        name='Y-Space Технопарк',
        description='Современный коворкинг в районе Технопарка, идеальное место для IT-специалистов.',
        address='Москва, проспект Андропова, д. 18к3',
        opens_at=time(10 - 3, 0, tzinfo=datetime.UTC),
        closes_at=time(22 - 3, 0, tzinfo=datetime.UTC),
        images=[
            'https://storage.yandexcloud.net/kurva/e805ad78-6c99-4527-bb6f-25adccb97641',
            'https://storage.yandexcloud.net/kurva/537b67af-217f-4862-85d8-aa54133f314b',
            'https://storage.yandexcloud.net/kurva/8d0cecfb-3533-4af0-bde7-0bb9fe4721ac',
        ],
    ),
)

spots = [
    Spot(
        id=uuid4(),
        coworking_id=coworking.id,
        name=f'№{k + 1}',
        description='',
        position=k + 1,
        status='active',
    )
    for k in range(28)
    for coworking in coworkings
]

users = [
    User(
        id=uuid4(),
        full_name=faker.name(),
        email=faker.email(),
        hashed_password=uuid4().hex,
        is_business=False,
        avatar_url=None,
    )
    for _ in range(60)
]

current_date = datetime.datetime.now()


async def mock_bookings(spot_service: SpotService, booking_service: BookingService) -> None:
    for user in users:
        start = datetime.datetime.combine(
            current_date,
            datetime.time(random.randint(12, 19), 0, 0, tzinfo=datetime.UTC),  # noqa
            tzinfo=datetime.UTC,
        )
        end = start + timedelta(hours=random.randint(1, 3), days=random.randint(0, 1))  # noqa
        coworking = random.choice(coworkings)
        booking_times = await spot_service.get_spots_with_availability(
            coworking_id=coworking.id,
            time_from=start,
            time_until=end,
        )
        for _ in range(len(booking_times)):
            booking_time = random.choice(booking_times)  # noqa
            if booking_time[1] == 'active':
                await booking_service.create_booking(user.id, booking_time[0].id, start, end)
                break


async def db_mock(cont: AsyncContainer) -> None:
    async with cont() as request_container:
        coworking_repo = await request_container.get(CoworkingRepository)
        spot_repo = await request_container.get(SpotRepository)
        user_repo = await request_container.get(UserRepository)
        spot_serv = await request_container.get(SpotService)
        booking_serv = await request_container.get(BookingService)

        try:
            await coworking_repo.get_by_id(coworkings[0].id)
        except NotFoundError:
            for obj in coworkings:
                await coworking_repo.create(obj)

            for obj in spots:
                await spot_repo.create(obj)

            for obj in users:
                await user_repo.create(obj)

            await mock_bookings(spot_serv, booking_serv)


if __name__ == '__main__':
    asyncio.run(db_mock(container))
