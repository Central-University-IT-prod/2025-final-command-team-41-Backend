import asyncio
import logging

from src.core.container import container
from src.core.events import EventBus
from src.core.logging import get_logger
from src.core.settings import Settings
from src.modules.auth.domain.events import (
    InvalidAuthenticationAttempt,
    UserAuthenticated,
)
from src.modules.auth.infrastructure.event_handlers import AuthEventLogger
from src.modules.users.domain.events import (
    UserCreated,
    UserEmailChanged,
    UserPasswordChanged,
)
from src.modules.users.infrastructure.event_handlers import UserEventLogger

logger = get_logger(__name__)


async def worker(worker_id: int, event_bus: EventBus) -> None:
    auth_logger = AuthEventLogger()
    user_logger = UserEventLogger()

    await event_bus.subscribe(InvalidAuthenticationAttempt, auth_logger.handle)
    await event_bus.subscribe(UserAuthenticated, auth_logger.handle)
    await event_bus.subscribe(UserCreated, user_logger.handle)
    await event_bus.subscribe(UserEmailChanged, user_logger.handle)
    await event_bus.subscribe(UserPasswordChanged, user_logger.handle)

    event = asyncio.Event()
    try:
        await event.wait()
    except asyncio.CancelledError:
        logger.info(f'Worker ID: {worker_id} was stopped')


async def create_runner() -> None:
    settings = await container.get(Settings)
    await container.get(logging.Logger)

    logger.info(
        'Starting runner',
        extra={
            'environment': settings.environment,
            'log_level': settings.environment_log_level,
        },
    )

    event_bus = await container.get(EventBus)

    workers = [asyncio.create_task(worker(i, event_bus)) for i in range(1)]
    await asyncio.gather(*workers)


if __name__ == '__main__':
    asyncio.run(create_runner())
