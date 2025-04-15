from dishka import make_async_container

from src.core.di import (
    ConfigProvider,
    DatabaseProvider,
    EventBusProvider,
    PasswordHasherProvider,
    S3StorageProvider,
)
from src.core.logging import LoggerProvider
from src.modules.auth.provider import AuthProvider
from src.modules.bookings.provider import BookingProvider
from src.modules.coworkings.provider import CoworkingProvider
from src.modules.notifications.provider import NotificationsProvider
from src.modules.options.provider import OptionProvider
from src.modules.spots.provider import SpotProvider
from src.modules.users.provider import UserProvider

container = make_async_container(
    ConfigProvider(),
    DatabaseProvider(),
    EventBusProvider(),
    LoggerProvider(),
    PasswordHasherProvider(),
    S3StorageProvider(),
    UserProvider(),
    AuthProvider(),
    NotificationsProvider(),
    CoworkingProvider(),
    SpotProvider(),
    OptionProvider(),
    BookingProvider(),
)
