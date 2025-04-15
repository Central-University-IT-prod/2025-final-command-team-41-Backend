import logging
import typing
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.container import container
from src.core.database import BaseModel, create_engine
from src.core.error_handlers import setup_error_handlers
from src.core.logging import get_logger
from src.core.settings import Settings, get_settings
from src.entrypoints.mock.main import db_mock
from src.modules.auth.adapters.api.router import router as auth_router
from src.modules.auth.application.services import AuthService
from src.modules.bookings.adapters.api.router import router as bookings_router
from src.modules.coworkings.adapters.api.router import router as coworkings_router
from src.modules.healthcheck.adapters.api.router import router as healthcheck_router
from src.modules.notifications.adapters.api.router import router as notifications_router
from src.modules.options.adapters.api.router import router as options_router
from src.modules.spots.adapters.api.router import router as spots_router
from src.modules.storage.adapters.api.router import router as storage_router
from src.modules.users.adapters.api.router import router as users_router
from src.modules.users.application.services import UserService

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    settings = await container.get(Settings)
    await container.get(logging.Logger)

    logger.info(
        'Starting application',
        extra={
            'environment': settings.environment,
            'log_level': settings.environment_log_level,
        },
    )

    engine = create_engine(settings)

    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    await db_mock(container)

    yield

    logger.info('Shutting down application')
    await container.close()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    Instrumentator().instrument(app).expose(app)

    setup_dishka(container, app)
    setup_error_handlers(app)

    routers = (
        healthcheck_router,
        auth_router,
        users_router,
        notifications_router,
        coworkings_router,
        spots_router,
        storage_router,
        options_router,
        bookings_router,
    )

    for router in routers:
        app.include_router(router)

    app.middleware('http')(banlist_middleware)

    return app


async def banlist_middleware(request: fastapi.Request, call_next: typing.Callable) -> fastapi.Response:
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return await call_next(request)

    async with container() as request_container:
        auth_service = await request_container.get(AuthService)
        user_service = await request_container.get(UserService)

        try:
            _, token = auth_header.split()

            user_id = await auth_service.verify_token(token)
            user = await user_service.get_user(user_id)

        except Exception as e:  # noqa
            return await call_next(request)

        if user and user.is_banned:
            return fastapi.responses.JSONResponse(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                content={'detail': 'User is banned.'},
            )

    return await call_next(request)


if __name__ == '__main__':
    settings = get_settings()
    uvicorn.run(
        'src.entrypoints.rest.main:create_app',
        workers=settings.server.workers,
        host='0.0.0.0',  # noqa: S104
        port=settings.server.port,
        root_path=settings.server.root_path,
    )
